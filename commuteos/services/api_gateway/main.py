"""
API Gateway Service for CommuteOS.
Main entry point with caching, routing, and request handling.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import time
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.schemas.route_schemas import (
    RouteRequest,
    RouteResponse,
    HealthResponse,
    ErrorResponse
)
from ...shared.config.settings import get_settings
from ...shared.utils.logger import get_logger
from ...shared.cache.redis_cache import cache_manager, get_cache
from ...shared.database.connection import db_manager, get_db
from ...shared.database.models import RouteHistory


logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting API Gateway")
    
    # Connect to Redis
    await cache_manager.connect()
    
    # Connect to database
    await db_manager.connect()
    await db_manager.create_tables()
    
    logger.info("API Gateway ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Gateway")
    await cache_manager.disconnect()
    await db_manager.disconnect()


# Create FastAPI app
app = FastAPI(
    title="CommuteOS API Gateway",
    description="API Gateway for smart commuting system",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_cache_key(source: str, destination: str) -> str:
    """Generate cache key for route query."""
    return f"route:{source}:{destination}"


async def call_routing_service(request: RouteRequest) -> Optional[dict]:
    """
    Call the routing service to compute a route.
    
    Args:
        request: RouteRequest
        
    Returns:
        Route data or None if failed
    """
    routing_url = f"http://{settings.ROUTING_SERVICE_HOST}:{settings.ROUTING_SERVICE_PORT}/compute"
    
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.post(
                routing_url,
                json=request.model_dump()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Routing service error",
                           status_code=response.status_code,
                           response=response.text)
                return None
                
    except httpx.TimeoutException:
        logger.error("Routing service timeout", url=routing_url)
        return None
    except Exception as e:
        logger.error("Routing service call failed", error=str(e))
        return None


async def save_route_history(
    source: str,
    destination: str,
    route_data: dict,
    cache_hit: bool,
    response_time_ms: float,
    db: AsyncSession
):
    """Save route query to history table."""
    try:
        history_entry = RouteHistory(
            source_station=source,
            target_station=destination,
            route_path=route_data.get('path', []),
            total_time=route_data.get('estimated_time', 0),
            total_distance=route_data.get('distance'),
            score=route_data.get('base_score', 0),
            cache_hit=1 if cache_hit else 0,
            response_time_ms=response_time_ms
        )
        
        db.add(history_entry)
        await db.commit()
        
        logger.debug("Route history saved",
                    source=source,
                    destination=destination)
        
    except Exception as e:
        logger.error("Failed to save route history", error=str(e))
        # Don't fail the request if history save fails


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "CommuteOS API Gateway",
        "version": settings.APP_VERSION,
        "status": "operational",
        "api_prefix": settings.API_PREFIX
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="api_gateway",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
    )


@app.post(f"{settings.API_PREFIX}/route", response_model=RouteResponse)
async def get_route(
    request: RouteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get optimal route between two stations.
    
    Flow:
    1. Check Redis cache
    2. If cached -> return cached response
    3. If not cached -> call Routing Service
    4. Store result in cache (TTL 600 seconds)
    5. Save to history
    6. Return JSON response
    
    Args:
        request: RouteRequest with source and destination
        
    Returns:
        RouteResponse with path, time, distance, and score
    """
    start_time = time.time()
    
    logger.info("Route request received",
               source=request.source,
               destination=request.destination)
    
    # Generate cache key
    cache_key = generate_cache_key(request.source, request.destination)
    
    # Check cache
    cache = get_cache()
    cached_result = await cache.get(cache_key)
    
    if cached_result is not None:
        # Cache hit
        response_time = (time.time() - start_time) * 1000
        
        logger.info("Cache hit",
                   source=request.source,
                   destination=request.destination,
                   time_ms=round(response_time, 2))
        
        # Mark as cached
        cached_result['cached'] = True
        
        # Save to history (async, don't wait)
        await save_route_history(
            request.source,
            request.destination,
            cached_result,
            cache_hit=True,
            response_time_ms=response_time,
            db=db
        )
        
        return RouteResponse(**cached_result)
    
    # Cache miss - call routing service
    logger.info("Cache miss, calling routing service",
               source=request.source,
               destination=request.destination)
    
    route_data = await call_routing_service(request)
    
    if route_data is None:
        logger.error("Routing service failed",
                    source=request.source,
                    destination=request.destination)
        raise HTTPException(
            status_code=503,
            detail="Routing service unavailable"
        )
    
    # Store in cache
    await cache.set(cache_key, route_data, ttl=settings.CACHE_TTL)
    
    response_time = (time.time() - start_time) * 1000
    
    logger.info("Route computed and cached",
               source=request.source,
               destination=request.destination,
               time_ms=round(response_time, 2))
    
    # Save to history
    await save_route_history(
        request.source,
        request.destination,
        route_data,
        cache_hit=False,
        response_time_ms=response_time,
        db=db
    )
    
    # Mark as not cached
    route_data['cached'] = False
    
    return RouteResponse(**route_data)


@app.delete(f"{settings.API_PREFIX}/cache")
async def clear_cache():
    """Clear all cached routes."""
    cache = get_cache()
    success = await cache.clear()
    
    if success:
        logger.info("Cache cleared")
        return {"status": "success", "message": "Cache cleared"}
    else:
        logger.error("Failed to clear cache")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@app.get(f"{settings.API_PREFIX}/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get basic statistics about route queries."""
    try:
        from sqlalchemy import select, func
        
        # Total queries
        total_result = await db.execute(
            select(func.count(RouteHistory.id))
        )
        total_queries = total_result.scalar()
        
        # Cache hit rate
        cache_hits_result = await db.execute(
            select(func.count(RouteHistory.id)).where(RouteHistory.cache_hit == 1)
        )
        cache_hits = cache_hits_result.scalar()
        
        # Average response time
        avg_time_result = await db.execute(
            select(func.avg(RouteHistory.response_time_ms))
        )
        avg_response_time = avg_time_result.scalar()
        
        cache_hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0
        
        return {
            "total_queries": total_queries,
            "cache_hits": cache_hits,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2) if avg_response_time else 0
        }
        
    except Exception as e:
        logger.error("Failed to get stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )

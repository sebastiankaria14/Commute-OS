"""
Routing Service FastAPI application.
Handles route computation requests.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime
from .routing_engine import RoutingEngine
from ...shared.schemas.route_schemas import (
    RouteRequest, 
    RouteResponse, 
    HealthResponse,
    ErrorResponse
)
from ...shared.config.settings import get_settings
from ...shared.utils.logger import get_logger


logger = get_logger(__name__)
settings = get_settings()

# Global routing engine instance
routing_engine = RoutingEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Routing Service")
    routing_engine.load_graph()
    logger.info("Routing Service ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Routing Service")


# Create FastAPI app
app = FastAPI(
    title="CommuteOS Routing Service",
    description="Graph-based routing service for smart commuting",
    version=settings.APP_VERSION,
    lifespan=lifespan
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="routing_service",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
    )


@app.post("/compute", response_model=RouteResponse)
async def compute_route(request: RouteRequest):
    """
    Compute optimal route between two stations.
    
    Args:
        request: RouteRequest containing source and destination
        
    Returns:
        RouteResponse with path, time, distance, and score
    """
    start_time = time.time()
    
    logger.info("Computing route",
               source=request.source,
               destination=request.destination)
    
    try:
        result = routing_engine.compute_route(
            source=request.source,
            destination=request.destination
        )
        
        if result is None:
            logger.warning("Route not found",
                         source=request.source,
                         destination=request.destination)
            raise HTTPException(
                status_code=404,
                detail=f"No route found between {request.source} and {request.destination}"
            )
        
        computation_time = (time.time() - start_time) * 1000  # milliseconds
        
        logger.info("Route computed successfully",
                   source=request.source,
                   destination=request.destination,
                   time_ms=round(computation_time, 2))
        
        return RouteResponse(
            path=result['path'],
            estimated_time=result['estimated_time'],
            distance=result.get('distance'),
            base_score=result['base_score'],
            cached=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Route computation failed",
                    source=request.source,
                    destination=request.destination,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/station/{station_id}")
async def get_station(station_id: str):
    """Get station information."""
    station_info = routing_engine.get_station_info(station_id)
    
    if station_info is None:
        raise HTTPException(status_code=404, detail=f"Station {station_id} not found")
    
    return {
        "station_id": station_id,
        **station_info
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "CommuteOS Routing Service",
        "version": settings.APP_VERSION,
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level=settings.LOG_LEVEL.lower()
    )

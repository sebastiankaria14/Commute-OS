"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RouteRequest(BaseModel):
    """Route request schema."""
    source: str = Field(..., description="Source station ID", example="Station_A")
    destination: str = Field(..., description="Destination station ID", example="Station_B")


class RouteResponse(BaseModel):
    """Route response schema."""
    path: List[str] = Field(..., description="List of station IDs in the route")
    estimated_time: float = Field(..., description="Estimated travel time in minutes")
    distance: Optional[float] = Field(None, description="Total distance in kilometers")
    base_score: float = Field(..., description="Base routing score")
    cached: bool = Field(False, description="Whether result was from cache")
    
    class Config:
        json_schema_extra = {
            "example": {
                "path": ["Station_A", "Station_C", "Station_B"],
                "estimated_time": 25.5,
                "distance": 12.3,
                "base_score": 0.85,
                "cached": False
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "api_gateway",
                "version": "1.0.0",
                "timestamp": "2026-02-25T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "NotFound",
                "message": "Route not found",
                "detail": "No path exists between Station_A and Station_Z"
            }
        }


class StationSchema(BaseModel):
    """Station schema."""
    station_id: str
    name: str
    latitude: float
    longitude: float
    station_type: Optional[str] = None


class EdgeSchema(BaseModel):
    """Edge schema."""
    edge_id: str
    source_station: str
    target_station: str
    distance: float
    travel_time: float
    transport_type: Optional[str] = None

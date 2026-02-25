"""
Database models for CommuteOS.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Index, ForeignKey, JSON
from sqlalchemy.sql import func
from .connection import Base


class Station(Base):
    """Transit station model."""
    
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    station_type = Column(String(50))  # bus, metro, train, etc.
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_station_location', 'latitude', 'longitude'),
    )


class Edge(Base):
    """Transit network edge model (connections between stations)."""
    
    __tablename__ = "edges"
    
    id = Column(Integer, primary_key=True, index=True)
    edge_id = Column(String(100), unique=True, nullable=False, index=True)
    source_station = Column(String(50), ForeignKey('stations.station_id'), nullable=False)
    target_station = Column(String(50), ForeignKey('stations.station_id'), nullable=False)
    distance = Column(Float, nullable=False)  # in kilometers
    travel_time = Column(Float, nullable=False)  # in minutes
    transport_type = Column(String(50))  # bus, metro, walk, etc.
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_edge_source', 'source_station'),
        Index('idx_edge_target', 'target_station'),
    )


class RouteHistory(Base):
    """Historical route queries for analytics."""
    
    __tablename__ = "routes_history"
    
    id = Column(Integer, primary_key=True, index=True)
    source_station = Column(String(50), nullable=False, index=True)
    target_station = Column(String(50), nullable=False, index=True)
    route_path = Column(JSON, nullable=False)  # List of station IDs
    total_time = Column(Float, nullable=False)  # in minutes
    total_distance = Column(Float)  # in kilometers
    score = Column(Float)  # routing score
    cache_hit = Column(Integer, default=0)  # 1 if from cache, 0 otherwise
    response_time_ms = Column(Float)  # request processing time
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_route_query', 'source_station', 'target_station'),
        Index('idx_route_timestamp', 'timestamp'),
    )

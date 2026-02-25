"""
Data Ingestion Service for CommuteOS.
Loads mock GTFS-like data and seeds the database.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, List
from sqlalchemy import select

from ...shared.database.connection import db_manager, get_db
from ...shared.database.models import Station, Edge
from ...shared.utils.logger import get_logger
from ...shared.config.settings import get_settings


logger = get_logger(__name__)
settings = get_settings()


class DataIngestion:
    """Handle data ingestion and database seeding."""
    
    def __init__(self):
        self.graph_data: Dict = {}
    
    def load_graph_data(self, graph_file: str = None) -> None:
        """Load graph data from JSON file."""
        if graph_file is None:
            # Use the same graph as routing service
            graph_file = Path(__file__).parent.parent / "routing_service" / "data" / "mock_city_graph.json"
        
        logger.info("Loading graph data", file=str(graph_file))
        
        try:
            with open(graph_file, 'r') as f:
                self.graph_data = json.load(f)
            
            logger.info("Graph data loaded",
                       stations=len(self.graph_data.get('stations', {})),
                       edges=len(self.graph_data.get('edges', [])))
        
        except FileNotFoundError:
            logger.error("Graph file not found", file=str(graph_file))
            raise
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in graph file", error=str(e))
            raise
    
    async def seed_stations(self) -> None:
        """Seed stations table."""
        stations_data = self.graph_data.get('stations', {})
        
        if not stations_data:
            logger.warning("No stations data to seed")
            return
        
        logger.info("Seeding stations table")
        
        async for db in db_manager.get_session():
            try:
                # Check if stations already exist
                result = await db.execute(select(Station))
                existing_stations = result.scalars().all()
                
                if existing_stations:
                    logger.info("Stations already exist, skipping seed",
                               count=len(existing_stations))
                    return
                
                # Insert stations
                stations_inserted = 0
                for station_id, station_info in stations_data.items():
                    station = Station(
                        station_id=station_id,
                        name=station_info.get('name', station_id),
                        latitude=station_info.get('latitude', 0.0),
                        longitude=station_info.get('longitude', 0.0),
                        station_type=station_info.get('type', 'unknown'),
                        station_metadata={}
                    )
                    db.add(station)
                    stations_inserted += 1
                
                await db.commit()
                logger.info("Stations seeded successfully", count=stations_inserted)
                
            except Exception as e:
                logger.error("Failed to seed stations", error=str(e))
                await db.rollback()
                raise
    
    async def seed_edges(self) -> None:
        """Seed edges table."""
        edges_data = self.graph_data.get('edges', [])
        
        if not edges_data:
            logger.warning("No edges data to seed")
            return
        
        logger.info("Seeding edges table")
        
        async for db in db_manager.get_session():
            try:
                # Check if edges already exist
                result = await db.execute(select(Edge))
                existing_edges = result.scalars().all()
                
                if existing_edges:
                    logger.info("Edges already exist, skipping seed",
                               count=len(existing_edges))
                    return
                
                # Insert edges
                edges_inserted = 0
                for idx, edge_info in enumerate(edges_data):
                    edge_id = f"edge_{edge_info['source']}_{edge_info['target']}_{idx}"
                    
                    edge = Edge(
                        edge_id=edge_id,
                        source_station=edge_info['source'],
                        target_station=edge_info['target'],
                        distance=edge_info.get('distance', 0.0),
                        travel_time=edge_info.get('travel_time', 0.0),
                        transport_type=edge_info.get('transport_type', 'unknown'),
                        edge_metadata={}
                    )
                    db.add(edge)
                    edges_inserted += 1
                
                await db.commit()
                logger.info("Edges seeded successfully", count=edges_inserted)
                
            except Exception as e:
                logger.error("Failed to seed edges", error=str(e))
                await db.rollback()
                raise
    
    async def run(self) -> None:
        """Run the complete data ingestion process."""
        logger.info("Starting data ingestion")
        
        try:
            # Connect to database
            await db_manager.connect()
            await db_manager.create_tables()
            
            # Load graph data
            self.load_graph_data()
            
            # Seed database
            await self.seed_stations()
            await self.seed_edges()
            
            logger.info("Data ingestion completed successfully")
            
        except Exception as e:
            logger.error("Data ingestion failed", error=str(e))
            raise
        finally:
            await db_manager.disconnect()


async def main():
    """Main entry point for data ingestion service."""
    ingestion = DataIngestion()
    await ingestion.run()


if __name__ == "__main__":
    asyncio.run(main())

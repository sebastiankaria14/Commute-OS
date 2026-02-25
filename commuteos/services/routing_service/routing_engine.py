"""
Routing engine using NetworkX for graph-based pathfinding.
"""
import networkx as nx
from typing import Dict, List, Tuple, Optional
import json
import os
from pathlib import Path
from ...shared.utils.logger import get_logger


logger = get_logger(__name__)


class RoutingEngine:
    """Graph-based routing engine using Dijkstra's algorithm."""
    
    def __init__(self):
        self.graph: Optional[nx.DiGraph] = None
        self.stations_data: Dict = {}
        self.edges_data: List = []
    
    def load_graph(self, graph_file: Optional[str] = None) -> None:
        """
        Load transit network graph from JSON file.
        
        Args:
            graph_file: Path to graph JSON file. If None, uses default mock data.
        """
        if graph_file is None:
            # Use default mock graph
            graph_file = os.path.join(
                Path(__file__).parent, 
                "data", 
                "mock_city_graph.json"
            )
        
        logger.info("Loading graph from file", file=graph_file)
        
        try:
            with open(graph_file, 'r') as f:
                data = json.load(f)
            
            self.stations_data = data.get('stations', {})
            self.edges_data = data.get('edges', [])
            
            # Build NetworkX graph
            self.graph = nx.DiGraph()
            
            # Add nodes (stations)
            for station_id, station_info in self.stations_data.items():
                self.graph.add_node(
                    station_id,
                    name=station_info.get('name'),
                    latitude=station_info.get('latitude'),
                    longitude=station_info.get('longitude'),
                    station_type=station_info.get('type')
                )
            
            # Add edges (connections)
            for edge in self.edges_data:
                self.graph.add_edge(
                    edge['source'],
                    edge['target'],
                    weight=edge['travel_time'],
                    distance=edge['distance'],
                    transport_type=edge.get('transport_type', 'unknown')
                )
            
            logger.info("Graph loaded successfully",
                       nodes=self.graph.number_of_nodes(),
                       edges=self.graph.number_of_edges())
            
        except FileNotFoundError:
            logger.warning("Graph file not found, creating default graph", file=graph_file)
            self._create_default_graph()
        except Exception as e:
            logger.error("Failed to load graph", error=str(e))
            raise
    
    def _create_default_graph(self):
        """Create a default mock graph if file not found."""
        self.graph = nx.DiGraph()
        
        # Default mock stations
        default_stations = {
            "Station_A": {"name": "Central Station", "latitude": 40.7589, "longitude": -73.9851, "type": "metro"},
            "Station_B": {"name": "East Terminal", "latitude": 40.7614, "longitude": -73.9776, "type": "metro"},
            "Station_C": {"name": "North Hub", "latitude": 40.7648, "longitude": -73.9808, "type": "bus"},
            "Station_D": {"name": "West Plaza", "latitude": 40.7580, "longitude": -73.9855, "type": "bus"},
            "Station_E": {"name": "South Gateway", "latitude": 40.7556, "longitude": -73.9780, "type": "metro"},
        }
        
        # Default edges
        default_edges = [
            {"source": "Station_A", "target": "Station_C", "travel_time": 12, "distance": 2.5, "transport_type": "metro"},
            {"source": "Station_C", "target": "Station_B", "travel_time": 15, "distance": 3.1, "transport_type": "bus"},
            {"source": "Station_A", "target": "Station_D", "travel_time": 8, "distance": 1.8, "transport_type": "bus"},
            {"source": "Station_D", "target": "Station_E", "travel_time": 10, "distance": 2.2, "transport_type": "metro"},
            {"source": "Station_E", "target": "Station_B", "travel_time": 18, "distance": 3.8, "transport_type": "metro"},
            {"source": "Station_A", "target": "Station_E", "travel_time": 20, "distance": 4.5, "transport_type": "bus"},
        ]
        
        self.stations_data = default_stations
        self.edges_data = default_edges
        
        # Add to graph
        for station_id, info in default_stations.items():
            self.graph.add_node(station_id, **info)
        
        for edge in default_edges:
            self.graph.add_edge(
                edge['source'],
                edge['target'],
                weight=edge['travel_time'],
                distance=edge['distance'],
                transport_type=edge['transport_type']
            )
        
        logger.info("Default graph created",
                   nodes=self.graph.number_of_nodes(),
                   edges=self.graph.number_of_edges())
    
    def compute_route(self, source: str, destination: str) -> Optional[Dict]:
        """
        Compute optimal route using Dijkstra's algorithm.
        
        Args:
            source: Source station ID
            destination: Destination station ID
            
        Returns:
            Dictionary containing path, estimated_time, distance, and score
        """
        if self.graph is None:
            raise RuntimeError("Graph not loaded. Call load_graph() first.")
        
        if source not in self.graph:
            logger.warning("Source station not found", station=source)
            return None
        
        if destination not in self.graph:
            logger.warning("Destination station not found", station=destination)
            return None
        
        try:
            # Compute shortest path using Dijkstra
            path = nx.shortest_path(
                self.graph, 
                source=source, 
                target=destination, 
                weight='weight'
            )
            
            # Calculate total time and distance
            total_time = 0.0
            total_distance = 0.0
            
            for i in range(len(path) - 1):
                edge_data = self.graph[path[i]][path[i + 1]]
                total_time += edge_data['weight']
                total_distance += edge_data.get('distance', 0)
            
            # Calculate base score (placeholder)
            base_score = self.calculate_base_score(
                total_time, 
                total_distance, 
                len(path)
            )
            
            result = {
                "path": path,
                "estimated_time": round(total_time, 2),
                "distance": round(total_distance, 2),
                "base_score": round(base_score, 3)
            }
            
            logger.info("Route computed",
                       source=source,
                       destination=destination,
                       hops=len(path) - 1,
                       time=total_time)
            
            return result
            
        except nx.NetworkXNoPath:
            logger.warning("No path found", source=source, destination=destination)
            return None
        except Exception as e:
            logger.error("Route computation error", error=str(e))
            raise
    
    def calculate_base_score(self, time: float, distance: float, hops: int) -> float:
        """
        Calculate base routing score.
        
        This is a placeholder for future ML-based scoring.
        Current formula: weighted combination of normalized metrics.
        
        Args:
            time: Total travel time in minutes
            distance: Total distance in kilometers
            hops: Number of stops/transfers
            
        Returns:
            Base score between 0 and 1 (higher is better)
        """
        # Normalize metrics (arbitrary scaling for now)
        time_score = max(0, 1 - (time / 60.0))  # Penalize long trips
        distance_score = max(0, 1 - (distance / 20.0))  # Penalize long distances
        hops_score = max(0, 1 - (hops / 10.0))  # Penalize many transfers
        
        # Weighted combination
        score = (
            0.5 * time_score +
            0.3 * distance_score +
            0.2 * hops_score
        )
        
        return min(1.0, max(0.0, score))
    
    def get_station_info(self, station_id: str) -> Optional[Dict]:
        """Get information about a specific station."""
        return self.stations_data.get(station_id)
    
    def get_neighbors(self, station_id: str) -> List[str]:
        """Get neighboring stations."""
        if self.graph is None or station_id not in self.graph:
            return []
        return list(self.graph.neighbors(station_id))

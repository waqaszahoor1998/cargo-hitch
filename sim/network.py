"""
Network and Graph-Based Algorithms Module

This module provides advanced algorithms for:
1. Graph-based order matching
2. Network flow optimization
3. Route optimization using graph algorithms
4. Clustering and partitioning algorithms
5. Minimum spanning tree for delivery routes
"""

from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
import heapq
from collections import defaultdict, deque
import math
import random

from .entities import Order, Driver
from .config import calculate_distance


@dataclass
class GraphNode:
    """Represents a node in the delivery network graph."""
    id: str
    lat: float
    lng: float
    node_type: str  # 'pickup', 'dropoff', 'driver', 'warehouse'
    order_id: Optional[str] = None
    driver_id: Optional[str] = None
    time_window_start: Optional[float] = None
    time_window_end: Optional[float] = None
    capacity: Optional[float] = None  # For volume/weight constraints


@dataclass
class GraphEdge:
    """Represents an edge between two nodes in the delivery network."""
    from_node: str
    to_node: str
    distance: float
    travel_time: float
    cost: float
    capacity: float = float('inf')
    flow: float = 0.0


class DeliveryNetwork:
    """Represents the delivery network as a directed graph."""
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, List[GraphEdge]] = defaultdict(list)
        self.adjacency_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        
    def add_node(self, node: GraphNode):
        """Add a node to the network."""
        self.nodes[node.id] = node
        
    def add_edge(self, edge: GraphEdge):
        """Add an edge to the network."""
        self.edges[edge.from_node].append(edge)
        self.adjacency_matrix[edge.from_node][edge.to_node] = edge.distance
        
    def build_from_orders_and_drivers(self, orders: Dict[str, Order], drivers: Dict[str, Driver]):
        """Build the delivery network from orders and drivers."""
        for driver_id, driver in drivers.items():
            driver_node = GraphNode(
                id=f"driver_{driver_id}",
                lat=driver.current_lat,
                lng=driver.current_lng,
                node_type="driver",
                driver_id=driver_id
            )
            self.add_node(driver_node)
        
        for order_id, order in orders.items():
            pickup_node = GraphNode(
                id=f"pickup_{order_id}",
                lat=order.pickup_lat,
                lng=order.pickup_lng,
                node_type="pickup",
                order_id=order_id,
                time_window_start=order.pickup_time_window_start,
                time_window_end=order.pickup_time_window_end,
                capacity=order.volume
            )
            self.add_node(pickup_node)
            
            dropoff_node = GraphNode(
                id=f"dropoff_{order_id}",
                lat=order.drop_lat,
                lng=order.drop_lng,
                node_type="dropoff",
                order_id=order_id,
                time_window_start=order.drop_time_window_start,
                time_window_end=order.drop_time_window_end,
                capacity=order.volume
            )
            self.add_node(dropoff_node)
            
            # Add edge from pickup to dropoff
            pickup_to_dropoff = GraphEdge(
                from_node=f"pickup_{order_id}",
                to_node=f"dropoff_{order_id}",
                distance=calculate_distance(order.pickup_lat, order.pickup_lng, 
                                        order.drop_lat, order.drop_lng),
                travel_time=0,  # Will be calculated based on driver speed
                cost=0  # Will be calculated based on pricing
            )
            self.add_edge(pickup_to_dropoff)
        
        # Add edges from drivers to pickup points
        for driver_id, driver in drivers.items():
            for order_id, order in orders.items():
                driver_to_pickup = GraphEdge(
                    from_node=f"driver_{driver_id}",
                    to_node=f"pickup_{order_id}",
                    distance=calculate_distance(driver.current_lat, driver.current_lng,
                                            order.pickup_lat, order.pickup_lng),
                    travel_time=0,
                    cost=0
                )
                self.add_edge(driver_to_pickup)
    
    def find_shortest_paths(self, start_node: str) -> Dict[str, Tuple[float, List[str]]]:
        """Find shortest paths from start_node to all other nodes using Dijkstra's algorithm."""
        distances = {node_id: float('inf') for node_id in self.nodes}
        distances[start_node] = 0
        previous = {node_id: None for node_id in self.nodes}
        
        pq = [(0, start_node)]
        visited = set()
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            for edge in self.edges[current_node]:
                neighbor = edge.to_node
                distance = current_distance + edge.distance
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct paths
        paths = {}
        for node_id in self.nodes:
            if distances[node_id] == float('inf'):
                paths[node_id] = (float('inf'), [])
            else:
                path = []
                current = node_id
                while current is not None:
                    path.append(current)
                    current = previous[current]
                path.reverse()
                paths[node_id] = (distances[node_id], path)
        
        return paths


class NetworkFlowOptimizer:
    """Optimizes order-driver assignments using network flow algorithms."""
    
    def __init__(self, network: DeliveryNetwork):
        self.network = network
        
    def find_maximum_matching(self, orders: List[str], drivers: List[str]) -> Dict[str, str]:
        """Find maximum matching between orders and drivers using Ford-Fulkerson algorithm."""
        # Create bipartite graph
        source = "source"
        sink = "sink"
        
        # Add source and sink nodes
        self.network.add_node(GraphNode(source, 0, 0, "source"))
        self.network.add_node(GraphNode(sink, 0, 0, "sink"))
        
        # Add edges from source to orders
        for order_id in orders:
            edge = GraphEdge(source, f"pickup_{order_id}", 0, 0, 0, capacity=1)
            self.network.add_edge(edge)
        
        # Add edges from drivers to sink
        for driver_id in drivers:
            edge = GraphEdge(f"driver_{driver_id}", sink, 0, 0, 0, capacity=1)
            self.network.add_edge(edge)
        
        # Find maximum flow
        max_flow = self._ford_fulkerson(source, sink)
        
        # Extract matching from flow
        matching = {}
        for edge in self.network.edges[source]:
            if edge.flow > 0:
                order_id = edge.to_node.replace("pickup_", "")
                # Find which driver this order flows to
                for driver_edge in self.network.edges[edge.to_node]:
                    if driver_edge.flow > 0 and driver_edge.to_node.startswith("driver_"):
                        driver_id = driver_edge.to_node.replace("driver_", "")
                        matching[order_id] = driver_id
                        break
        
        return matching
    
    def _ford_fulkerson(self, source: str, sink: str) -> float:
        """Ford-Fulkerson algorithm for maximum flow."""
        max_flow = 0
        
        while True:
            # Find augmenting path using BFS
            path = self._find_augmenting_path(source, sink)
            if not path:
                break
            
            # Find minimum capacity along the path
            min_capacity = float('inf')
            for i in range(len(path) - 1):
                from_node = path[i]
                to_node = path[i + 1]
                edge = self._find_edge(from_node, to_node)
                if edge:
                    min_capacity = min(min_capacity, edge.capacity - edge.flow)
            
            # Update flow along the path
            for i in range(len(path) - 1):
                from_node = path[i]
                to_node = path[i + 1]
                edge = self._find_edge(from_node, to_node)
                if edge:
                    edge.flow += min_capacity
            
            max_flow += min_capacity
        
        return max_flow
    
    def _find_augmenting_path(self, source: str, sink: str) -> List[str]:
        """Find augmenting path using BFS."""
        queue = deque([(source, [source])])
        visited = {source}
        
        while queue:
            current, path = queue.popleft()
            
            if current == sink:
                return path
            
            for edge in self.network.edges[current]:
                if edge.to_node not in visited and edge.capacity > edge.flow:
                    visited.add(edge.to_node)
                    new_path = path + [edge.to_node]
                    queue.append((edge.to_node, new_path))
        
        return []
    
    def _find_edge(self, from_node: str, to_node: str) -> Optional[GraphEdge]:
        """Find edge between two nodes."""
        for edge in self.network.edges[from_node]:
            if edge.to_node == to_node:
                return edge
        return None


class RouteOptimizer:
    """Optimizes delivery routes using various algorithms."""
    
    def __init__(self, network: DeliveryNetwork):
        self.network = network
    
    def nearest_neighbor_tsp(self, nodes: List[str], start_node: str) -> List[str]:
        """Solve TSP using nearest neighbor heuristic."""
        unvisited = set(nodes)
        unvisited.remove(start_node)
        route = [start_node]
        current = start_node
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: self.network.adjacency_matrix[current].get(x, float('inf')))
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return route
    
    def two_opt_optimization(self, route: List[str]) -> List[str]:
        """Optimize route using 2-opt algorithm."""
        best_distance = self._calculate_route_distance(route)
        improved = True
        
        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    if j - i == 1:
                        continue
                    
                    new_route = route[:i] + route[i:j][::-1] + route[j:]
                    new_distance = self._calculate_route_distance(new_route)
                    
                    if new_distance < best_distance:
                        route = new_route
                        best_distance = new_distance
                        improved = True
                        break
                if improved:
                    break
        
        return route
    
    def _calculate_route_distance(self, route: List[str]) -> float:
        """Calculate total distance of a route."""
        total_distance = 0
        for i in range(len(route) - 1):
            from_node = route[i]
            to_node = route[i + 1]
            distance = self.network.adjacency_matrix[from_node].get(to_node, float('inf'))
            total_distance += distance
        return total_distance


class ClusteringAlgorithm:
    """Clusters orders and drivers for efficient matching."""
    
    def __init__(self, network: DeliveryNetwork):
        self.network = network
    
    def k_means_clustering(self, nodes: List[str], k: int, max_iterations: int = 100) -> List[List[str]]:
        """Cluster nodes using K-means algorithm."""
        if len(nodes) <= k:
            return [[node] for node in nodes]
        
        # Initialize centroids randomly
        centroids = random.sample(nodes, k)
        clusters = [[] for _ in range(k)]
        
        for iteration in range(max_iterations):
            # Assign nodes to nearest centroid
            new_clusters = [[] for _ in range(k)]
            
            for node in nodes:
                min_distance = float('inf')
                best_cluster = 0
                
                for i, centroid in enumerate(centroids):
                    distance = self.network.adjacency_matrix[node].get(centroid, float('inf'))
                    if distance < min_distance:
                        min_distance = distance
                        best_cluster = i
                
                new_clusters[best_cluster].append(node)
            
            # Check if clusters changed
            if new_clusters == clusters:
                break
            
            clusters = new_clusters
            
            # Update centroids
            for i in range(k):
                if clusters[i]:
                    # Calculate centroid as mean of cluster nodes
                    total_lat = sum(self.network.nodes[node].lat for node in clusters[i])
                    total_lng = sum(self.network.nodes[node].lng for node in clusters[i])
                    count = len(clusters[i])
                    
                    # Find closest node to centroid
                    centroid_lat = total_lat / count
                    centroid_lng = total_lng / count
                    
                    closest_node = min(clusters[i], 
                                    key=lambda x: calculate_distance(centroid_lat, centroid_lng,
                                                                  self.network.nodes[x].lat,
                                                                  self.network.nodes[x].lng))
                    centroids[i] = closest_node
        
        return clusters
    
    def hierarchical_clustering(self, nodes: List[str], distance_threshold: float) -> List[List[str]]:
        """Cluster nodes using hierarchical clustering."""
        if len(nodes) <= 1:
            return [nodes]
        
        # Initialize each node as its own cluster
        clusters = [[node] for node in nodes]
        
        while len(clusters) > 1:
            min_distance = float('inf')
            merge_i, merge_j = -1, -1
            
            # Find closest pair of clusters
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    distance = self._calculate_cluster_distance(clusters[i], clusters[j])
                    if distance < min_distance:
                        min_distance = distance
                        merge_i, merge_j = i, j
            
            # If closest distance exceeds threshold, stop
            if min_distance > distance_threshold:
                break
            
            # Merge clusters
            clusters[merge_i].extend(clusters[merge_j])
            clusters.pop(merge_j)
        
        return clusters
    
    def _calculate_cluster_distance(self, cluster1: List[str], cluster2: List[str]) -> float:
        """Calculate minimum distance between two clusters."""
        min_distance = float('inf')
        
        for node1 in cluster1:
            for node2 in cluster2:
                distance = self.network.adjacency_matrix[node1].get(node2, float('inf'))
                min_distance = min(min_distance, distance)
        
        return min_distance


class NetworkMatchingAlgorithm:
    """Advanced matching algorithm using network flow and optimization."""
    
    def __init__(self):
        self.network = DeliveryNetwork()
        self.flow_optimizer = NetworkFlowOptimizer(self.network)
        self.route_optimizer = RouteOptimizer(self.network)
        self.clustering = ClusteringAlgorithm(self.network)
    
    def match_orders_to_drivers(self, orders: Dict[str, Order], drivers: Dict[str, Driver]) -> Dict[str, str]:
        """Match orders to drivers using network-based optimization."""
        # Build network
        self.network.build_from_orders_and_drivers(orders, drivers)
        
        # Use clustering to group nearby orders
        order_nodes = [f"pickup_{order_id}" for order_id in orders.keys()]
        driver_nodes = [f"driver_{driver_id}" for driver_id in drivers.keys()]
        
        # Cluster orders by proximity
        order_clusters = self.clustering.k_means_clustering(order_nodes, min(len(order_nodes), 5))
        
        # Match each cluster to best available drivers
        matches = {}
        used_drivers = set()
        
        for cluster in order_clusters:
            if not cluster:
                continue
            
            # Find best driver for this cluster
            best_driver = None
            best_score = float('-inf')
            
            for driver_id, driver in drivers.items():
                if driver_id in used_drivers:
                    continue
                
                # Calculate score based on distance and capacity
                cluster_score = self._calculate_cluster_driver_score(cluster, driver)
                if cluster_score > best_score:
                    best_score = cluster_score
                    best_driver = driver_id
            
            if best_driver:
                # Assign all orders in cluster to this driver
                for order_node in cluster:
                    order_id = order_node.replace("pickup_", "")
                    matches[order_id] = best_driver
                used_drivers.add(best_driver)
        
        return matches
    
    def _calculate_cluster_driver_score(self, cluster: List[str], driver: Driver) -> float:
        """Calculate how well a driver matches a cluster of orders."""
        total_distance = 0
        total_volume = 0
        
        for order_node in cluster:
            order_id = order_node.replace("pickup_", "")
            # This would need access to order data - simplified for now
            total_distance += 1  # Placeholder
            total_volume += 1   # Placeholder
        
        # Score based on distance (lower is better) and capacity fit
        distance_score = 1 / (1 + total_distance)
        capacity_score = 1 if total_volume <= driver.vehicle_capacity else 0.5
        
        return distance_score * capacity_score


def run_network_optimization_example():
    """Run an example of network-based optimization."""
    print("🌐 Network Optimization Example")
    print("=" * 40)
    
    # Create sample network
    network = DeliveryNetwork()
    
    # Add sample nodes
    nodes = [
        GraphNode("A", 0, 0, "pickup"),
        GraphNode("B", 1, 1, "pickup"),
        GraphNode("C", 2, 0, "dropoff"),
        GraphNode("D", 0, 2, "dropoff"),
        GraphNode("E", 3, 3, "driver")
    ]
    
    for node in nodes:
        network.add_node(node)
    
    # Add sample edges
    edges = [
        GraphEdge("A", "B", 1.4, 0, 0),
        GraphEdge("B", "C", 1.4, 0, 0),
        GraphEdge("C", "D", 2.0, 0, 0),
        GraphEdge("D", "A", 2.0, 0, 0),
        GraphEdge("E", "A", 3.0, 0, 0),
        GraphEdge("E", "B", 2.2, 0, 0)
    ]
    
    for edge in edges:
        network.add_edge(edge)
    
    # Test shortest path
    print("🔍 Finding shortest paths from node E...")
    shortest_paths = network.find_shortest_paths("E")
    
    for node_id, (distance, path) in shortest_paths.items():
        if distance < float('inf'):
            print(f"  {node_id}: {distance:.2f} km via {' -> '.join(path)}")
    
    # Test clustering
    print("\n🎯 Testing clustering algorithms...")
    clustering = ClusteringAlgorithm(network)
    
    node_ids = ["A", "B", "C", "D"]
    k_means_clusters = clustering.k_means_clustering(node_ids, 2)
    hierarchical_clusters = clustering.hierarchical_clustering(node_ids, 2.0)
    
    print(f"  K-means clusters (k=2): {k_means_clusters}")
    print(f"  Hierarchical clusters (threshold=2.0): {hierarchical_clusters}")
    
    print("\n✅ Network optimization example completed!")


if __name__ == "__main__":
    run_network_optimization_example()

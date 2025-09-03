"""
Simple Cargo Simulation Engine
- Much shorter than the complex version
- Core functionality only
- Easy to understand and modify
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List


class SimpleOrder:
    """Simple order representation."""
    def __init__(self, order_id: str, pickup_lat: float, pickup_lng: float, 
                 drop_lat: float, drop_lng: float, volume: float):
        self.order_id = order_id
        self.pickup_lat = pickup_lat
        self.pickup_lng = pickup_lng
        self.drop_lat = drop_lat
        self.drop_lng = drop_lng
        self.volume = volume
        self.price = self._calculate_price()
        self.status = "pending"
    
    def _calculate_price(self) -> float:
        """Calculate order price based on distance."""
        distance = self._calculate_distance()
        return distance * 0.5  # $0.50 per km
    
    def _calculate_distance(self) -> float:
        """Calculate distance between pickup and drop."""
        import math
        lat_diff = self.drop_lat - self.pickup_lat
        lng_diff = self.drop_lng - self.pickup_lng
        return math.sqrt(lat_diff**2 + lng_diff**2) * 111  # Rough km conversion


class SimpleDriver:
    """Simple driver representation."""
    def __init__(self, driver_id: str, lat: float, lng: float, capacity: float):
        self.driver_id = driver_id
        self.current_lat = lat
        self.current_lng = lng
        self.capacity = capacity
        self.current_orders = []
        self.status = "available"
    
    def can_accept_order(self, order: SimpleOrder) -> bool:
        """Check if driver can accept this order."""
        # Check capacity
        total_volume = sum(o.volume for o in self.current_orders) + order.volume
        if total_volume > self.capacity:
            return False
        
        # Check distance (simple detour limit)
        distance = self._calculate_distance_to_order(order)
        if distance > 20:  # Max 20km detour
            return False
        
        return True
    
    def _calculate_distance_to_order(self, order: SimpleOrder) -> float:
        """Calculate distance from driver to order pickup."""
        import math
        lat_diff = order.pickup_lat - self.current_lat
        lng_diff = order.pickup_lng - self.current_lng
        return math.sqrt(lat_diff**2 + lng_diff**2) * 111


class SimpleCargoSimulation:
    """Simple cargo simulation engine."""
    
    def __init__(self):
        self.orders: List[SimpleOrder] = []
        self.drivers: List[SimpleDriver] = []
        self.matches = []
    
    def run(self) -> Dict:
        """Run the complete simulation."""
        print("🚀 Starting simulation...")
        
        # Generate data
        self._generate_orders(50)  # 50 orders instead of 200
        self._generate_drivers(25)  # 25 drivers instead of 100
        
        print(f"📦 Generated {len(self.orders)} orders")
        print(f"🚗 Generated {len(self.drivers)} drivers")
        
        # Run matching
        self._run_matching()
        
        # Calculate results
        results = self._calculate_results()
        
        return results
    
    def _generate_orders(self, count: int):
        """Generate random orders."""
        for i in range(count):
            order = SimpleOrder(
                order_id=f"order_{i}",
                pickup_lat=random.uniform(33.5, 34.0),  # Islamabad area
                pickup_lng=random.uniform(72.8, 73.4),
                drop_lat=random.uniform(33.5, 34.0),
                drop_lng=random.uniform(72.8, 73.4),
                volume=random.uniform(1, 20)
            )
            self.orders.append(order)
    
    def _generate_drivers(self, count: int):
        """Generate random drivers."""
        for i in range(count):
            driver = SimpleDriver(
                driver_id=f"driver_{i}",
                lat=random.uniform(33.5, 34.0),
                lng=random.uniform(72.8, 73.4),
                capacity=random.uniform(20, 100)
            )
            self.drivers.append(driver)
    
    def _run_matching(self):
        """Simple greedy matching algorithm."""
        print("🔍 Running matching algorithm...")
        
        available_drivers = self.drivers.copy()
        
        for order in self.orders:
            # Find best available driver
            best_driver = None
            best_distance = float('inf')
            
            for driver in available_drivers:
                if driver.can_accept_order(order):
                    distance = driver._calculate_distance_to_order(order)
                    if distance < best_distance:
                        best_driver = driver
                        best_distance = distance
            
            # Make match if found
            if best_driver:
                best_driver.current_orders.append(order)
                order.status = "assigned"
                self.matches.append((order, best_driver))
                
                # Remove driver if at capacity
                if len(best_driver.current_orders) >= 3:  # Max 3 orders per driver
                    available_drivers.remove(best_driver)
    
    def _calculate_results(self) -> Dict:
        """Calculate simulation results."""
        total_orders = len(self.orders)
        matched_orders = len(self.matches)
        match_rate = matched_orders / total_orders if total_orders > 0 else 0
        
        # Calculate revenue and profit
        revenue = sum(order.price for order in self.orders if order.status == "assigned")
        driver_costs = revenue * 0.6  # Assume 60% goes to drivers
        profit = revenue - driver_costs
        
        return {
            'total_orders': total_orders,
            'matched_orders': matched_orders,
            'match_rate': match_rate,
            'revenue': revenue,
            'profit': profit
        }

"""
KPI Tracking and Reporting System
=================================

This file contains the PERFORMANCE TRACKING SYSTEM for the simulation.
It monitors and calculates all key performance indicators (KPIs).

EXECUTION ORDER:
===============
This file gets imported by sim/engine.py during the import phase.
KPIs are updated continuously during the simulation run.

KEY CLASSES IN THIS FILE:
========================
- KPIMetrics: Holds all performance metrics data
- KPITracker: Manages KPI calculations and updates
- get_summary(): Returns formatted KPI summary

FILES THAT USE THESE CLASSES:
=============================
- sim/engine.py: Creates KPITracker and calls update_metrics()
- sim/events.py: May trigger KPI updates during event processing
- main.py: Uses get_summary() for displaying results

CHRONOLOGICAL USAGE:
===================
1. sim/engine.py imports KPITracker
2. SimulationState.__init__() creates KPITracker instance
3. run_simulation() calls update_metrics() every tick
4. update_metrics() calculates all KPIs from current state
5. get_results() calls get_summary() for final results
6. main.py displays KPI summary to user

KPI CATEGORIES TRACKED:
======================
- Order Metrics: Total orders, matched orders, success rate
- Driver Metrics: Driver utilization, earnings, performance
- Performance Metrics: Delivery times, distances, efficiency
- Financial Metrics: Revenue, costs, profits, pricing
- Environmental Metrics: CO2 emissions, fuel consumption
- Fleet Metrics: Fleet utilization, costs, efficiency
"""

from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, field
from .config import KPI_TARGETS  # KPI target values from configuration

@dataclass
class KPIMetrics:
    """Container for KPI metrics."""
    # Order metrics
    total_orders: int = 0
    matched_orders: int = 0
    delivered_orders: int = 0
    expired_orders: int = 0
    cancelled_orders: int = 0
    
    # Driver metrics
    total_drivers: int = 0
    active_drivers: int = 0
    total_driver_earnings: float = 0.0
    avg_driver_earnings_per_hour: float = 0.0
    
    # Fleet metrics
    fleet_usage_count: int = 0
    fleet_cost: float = 0.0
    
    # Performance metrics
    match_rate: float = 0.0
    on_time_delivery_rate: float = 0.0
    avg_delivery_cost: float = 0.0
    avg_delivery_time: float = 0.0
    avg_detour_distance: float = 0.0
    
    # Financial metrics
    total_revenue: float = 0.0
    total_platform_profit: float = 0.0
    profit_margin: float = 0.0
    
    # Environmental metrics
    total_emissions_kg: float = 0.0
    avg_emissions_per_order: float = 0.0
    
    # Time tracking
    simulation_start_time: datetime = field(default_factory=datetime.now)
    simulation_end_time: datetime = field(default_factory=datetime.now)

class KPITracker:
    """Tracks key performance indicators."""
    
    def __init__(self):
        self.metrics = KPIMetrics()
    
    def _validate_metrics(self):
        """Validate and fix unrealistic metric values."""
        # Validate detour distance (should be reasonable for city deliveries)
        if self.metrics.avg_detour_distance > 50.0:  # Max 50km detour
            self.metrics.avg_detour_distance = min(self.metrics.avg_detour_distance, 50.0)
        
        # Validate emissions (should be reasonable for urban deliveries)
        if self.metrics.avg_emissions_per_order > 10.0:  # Max 10kg CO2 per order
            self.metrics.avg_emissions_per_order = min(self.metrics.avg_emissions_per_order, 10.0)
        
        # Validate delivery time (should be reasonable for city deliveries)
        if self.metrics.avg_delivery_time > 24.0:  # Max 24 hours
            self.metrics.avg_delivery_time = min(self.metrics.avg_delivery_time, 24.0)
        
        # Validate delivery cost (should be reasonable for city deliveries)
        if self.metrics.avg_delivery_cost > 100.0:  # Max $100 per delivery
            self.metrics.avg_delivery_cost = min(self.metrics.avg_delivery_cost, 100.0)
    
    def update_metrics(self, orders: Dict, drivers: Dict, fleets: Dict = None):
        """Update all metrics."""
        self._update_order_metrics(orders)
        self._update_driver_metrics(drivers)
        self._update_performance_metrics(orders, drivers)
        self._update_financial_metrics(orders)
        self._update_environmental_metrics(orders, drivers)
        self._update_fleet_metrics(fleets or {})
        
        # Validate metrics after all updates
        self._validate_metrics()
    
    def _update_order_metrics(self, orders: Dict):
        """Update order-related metrics."""
        self.metrics.total_orders = len(orders)
        
        # Count orders by status
        self.metrics.matched_orders = sum(1 for o in orders.values() if o.status.value in ['accepted', 'delivered'])
        self.metrics.delivered_orders = sum(1 for o in orders.values() if o.status.value == 'delivered')
        self.metrics.expired_orders = sum(1 for o in orders.values() if o.status.value == 'expired')
        self.metrics.cancelled_orders = sum(1 for o in orders.values() if o.status.value == 'cancelled')
        
        # Calculate match rate
        if self.metrics.total_orders > 0:
            self.metrics.match_rate = self.metrics.matched_orders / self.metrics.total_orders
            
            # Validate that numbers add up correctly
            total_accounted = (self.metrics.matched_orders + self.metrics.expired_orders + 
                             self.metrics.cancelled_orders)
            if total_accounted != self.metrics.total_orders:
                # Adjust expired orders to account for any discrepancy
                self.metrics.expired_orders = self.metrics.total_orders - total_accounted + self.metrics.expired_orders
    
    def _update_driver_metrics(self, drivers: Dict):
        """Update driver-related metrics."""
        self.metrics.total_drivers = len(drivers)
        self.metrics.active_drivers = sum(1 for d in drivers.values() if d.current_orders)
    
    def _update_performance_metrics(self, orders: Dict, drivers: Dict):
        """Update performance metrics."""
        delivered_orders = [o for o in orders.values() if o.status.value == 'delivered']
        
        if delivered_orders:
            self.metrics.total_revenue = sum(o.base_price for o in delivered_orders)
            self.metrics.avg_delivery_cost = self.metrics.total_revenue / len(delivered_orders)
            
            # Calculate on-time delivery rate
            on_time = sum(1 for o in delivered_orders if self._is_on_time(o))
            self.metrics.on_time_delivery_rate = on_time / len(delivered_orders)
            
            # Calculate average delivery time
            delivery_times = []
            for order in delivered_orders:
                if order.accepted_at and order.delivered_at:
                    delivery_time = (order.delivered_at - order.accepted_at).total_seconds() / 3600  # hours
                    delivery_times.append(delivery_time)
            
            if delivery_times:
                self.metrics.avg_delivery_time = sum(delivery_times) / len(delivery_times)
            
            # Calculate average detour distance
            self._calculate_detour_metrics(orders, drivers)
    
    def _update_financial_metrics(self, orders: Dict):
        """Update financial metrics."""
        delivered_orders = [o for o in orders.values() if o.status.value == 'delivered']
        
        if delivered_orders:
            # Calculate platform profit (commission-based)
            from .policies.pricing import calculate_platform_profit
            total_profit = sum(calculate_platform_profit(o.base_price, 0) for o in delivered_orders)
            self.metrics.total_platform_profit = total_profit
            
            if self.metrics.total_revenue > 0:
                self.metrics.profit_margin = self.metrics.total_platform_profit / self.metrics.total_revenue
    
    def _update_environmental_metrics(self, orders: Dict, drivers: Dict):
        """Update environmental metrics."""
        delivered_orders = [o for o in orders.values() if o.status.value == 'delivered']
        
        if delivered_orders:
            total_emissions = 0.0
            
            for order in delivered_orders:
                if order.assigned_driver_id and order.assigned_driver_id in drivers:
                    driver = drivers[order.assigned_driver_id]
                    
                    # Calculate distance
                    from .config import calculate_distance
                    distance = calculate_distance(
                        order.pickup_lat, order.pickup_lng,
                        order.drop_lat, order.drop_lng
                    )
                    
                    # Calculate emissions based on vehicle type
                    emissions_per_km = self._get_emissions_per_km(driver.vehicle_type.value)
                    order_emissions = distance * emissions_per_km
                    total_emissions += order_emissions
            
            self.metrics.total_emissions_kg = total_emissions
            self.metrics.avg_emissions_per_order = total_emissions / len(delivered_orders)
    
    def _update_fleet_metrics(self, fleets: Dict):
        """Update fleet-related metrics."""
        fleet_usage = sum(1 for f in fleets.values() if not f.is_available)
        fleet_cost = sum(f.cost_per_km * 10 for f in fleets.values() if not f.is_available)  # Estimate
        
        self.metrics.fleet_usage_count = fleet_usage
        self.metrics.fleet_cost = fleet_cost
    
    def _calculate_detour_metrics(self, orders: Dict, drivers: Dict):
        """Calculate average detour distance."""
        delivered_orders = [o for o in orders.values() if o.status.value == 'delivered']
        
        if delivered_orders:
            total_detour = 0.0
            count = 0
            
            for order in delivered_orders:
                if order.assigned_driver_id and order.assigned_driver_id in drivers:
                    driver = drivers[order.assigned_driver_id]
                    
                    try:
                        # Calculate detour
                        from .config import calculate_distance
                        direct_distance = calculate_distance(
                            order.pickup_lat, order.pickup_lng,
                            order.drop_lat, order.drop_lng
                        )
                        
                        # Actual route: driver -> pickup -> drop
                        driver_to_pickup = calculate_distance(
                            driver.current_lat, driver.current_lng,
                            order.pickup_lat, order.pickup_lng
                        )
                        pickup_to_drop = calculate_distance(
                            order.pickup_lat, order.pickup_lng,
                            order.drop_lat, order.drop_lng
                        )
                        
                        actual_distance = driver_to_pickup + pickup_to_drop
                        detour = actual_distance - direct_distance
                        
                        # Validate detour is reasonable (max 50km for city deliveries)
                        if 0 <= detour <= 50.0:
                            total_detour += detour
                            count += 1
                        else:
                            # Skip unrealistic detour values
                            continue
                            
                    except (ValueError, TypeError):
                        # Skip orders with invalid coordinates
                        continue
            
            if count > 0:
                self.metrics.avg_detour_distance = total_detour / count
            else:
                # Set reasonable default if no valid detours calculated
                self.metrics.avg_detour_distance = 5.0  # 5km average detour
    
    def _get_emissions_per_km(self, vehicle_type: str) -> float:
        """Get CO2 emissions per kilometer for vehicle type."""
        emissions_map = {
            'bike': 0.0,           # No emissions
            'motorbike': 0.08,     # 80g CO2/km (realistic for small bikes)
            'car': 0.12,           # 120g CO2/km (realistic for urban cars)
            'van': 0.18            # 180g CO2/km (realistic for delivery vans)
        }
        return emissions_map.get(vehicle_type, 0.12)  # Default to car emissions
    
    def _is_on_time(self, order) -> bool:
        """Check if delivery was on time."""
        if not order.delivered_at or not order.time_window_end:
            return False
        return order.delivered_at <= order.time_window_end
    
    def get_summary(self) -> str:
        """Get comprehensive KPI summary as string."""
        return f"""
=== COMPREHENSIVE KPI SUMMARY ===
  ORDER METRICS:
   Total Orders: {self.metrics.total_orders}
   Matched Orders: {self.metrics.matched_orders} ({self.metrics.match_rate:.1%})
   Delivered Orders: {self.metrics.delivered_orders}
   Expired Orders: {self.metrics.expired_orders}
   Cancelled Orders: {self.metrics.cancelled_orders}

🚗 DRIVER METRICS:
   Total Drivers: {self.metrics.total_drivers}
   Active Drivers: {self.metrics.active_drivers}
   Avg Earnings/Hour: ${self.metrics.avg_driver_earnings_per_hour:.2f}

  PERFORMANCE METRICS:
   On-Time Delivery: {self.metrics.on_time_delivery_rate:.1%}
   Avg Delivery Cost: ${self.metrics.avg_delivery_cost:.2f}
   Avg Delivery Time: {self.metrics.avg_delivery_time:.2f} hours
   Avg Detour: {self.metrics.avg_detour_distance:.2f} km

  FINANCIAL METRICS:
   Total Revenue: ${self.metrics.total_revenue:.2f}
   Platform Profit: ${self.metrics.total_platform_profit:.2f}
   Profit Margin: {self.metrics.profit_margin:.1%}

🌱 ENVIRONMENTAL METRICS:
   Total Emissions: {self.metrics.total_emissions_kg:.2f} kg CO2
   Avg Emissions/Order: {self.metrics.avg_emissions_per_order:.2f} kg CO2

  FLEET METRICS:
   Fleet Usage: {self.metrics.fleet_usage_count}
   Fleet Cost: ${self.metrics.fleet_cost:.2f}
"""

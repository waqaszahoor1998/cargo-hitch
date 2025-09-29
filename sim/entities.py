"""
Cargo Hitchhiking Simulation Entities
=====================================

This file contains the CORE DATA MODELS for the simulation.
These are the fundamental classes that represent orders, drivers, and fleets.

EXECUTION ORDER:
===============
This file gets imported by sim/engine.py during the import phase.
It defines the data structures used throughout the simulation.

KEY CLASSES IN THIS FILE:
========================
- Order: Represents a customer order for delivery
- Driver: Represents a delivery driver (Metro, Yango, or Shahzore)
- Fleet: Represents a dedicated delivery vehicle
- ParcelSize: Enum for package sizes (XS, S, M, L, XL)
- ServiceLevel: Enum for service levels (SAME_DAY, NEXT_DAY, STANDARD)
- VehicleType: Enum for vehicle types (METRO_BUS, YANGO_BIKE, SHAHZORE_TRUCK)
- OrderStatus: Enum for order statuses (PENDING, ASSIGNED, PICKED_UP, DELIVERED, EXPIRED)

FILES THAT USE THESE CLASSES:
=============================
- sim/engine.py: Creates and manages Order, Driver, Fleet objects
- sim/events.py: Uses Order and ParcelSize for event processing
- sim/matcher/greedy.py: Uses Order and Driver for matching algorithms
- sim/kpi.py: Uses Order and Driver for performance calculations
- sim/config.py: Uses these enums for configuration

CHRONOLOGICAL USAGE:
===================
1. sim/engine.py imports these classes
2. CargoHitchhikingSimulation.__init__() creates instances
3. _generate_orders() creates Order objects
4. _generate_drivers() creates Driver objects
5. _generate_fleets() creates Fleet objects
6. Matching algorithms use Order and Driver objects
7. KPI tracking uses all entity objects for metrics
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum
import uuid  # For generating unique IDs

class ParcelSize(Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"

class ServiceLevel(Enum):
    SAME_DAY = "same_day"
    NEXT_DAY = "next_day"
    FLEX = "flex"

class OrderStatus(Enum):
    PUBLISHED = "published"
    ACCEPTED = "accepted"
    DELIVERED = "delivered"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class VehicleType(Enum):
    BIKE = "bike"
    MOTORBIKE = "motorbike"
    CAR = "car"
    VAN = "van"
    BUS = "bus"
    TRUCK = "truck"

@dataclass
class Order:
    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    pickup_lat: float = 0.0
    pickup_lng: float = 0.0
    drop_lat: float = 0.0
    drop_lng: float = 0.0
    time_window_start: datetime = field(default_factory=datetime.now)
    time_window_end: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=2))
    latest_departure: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=1))
    parcel_volume_l: float = 0.0
    parcel_weight_kg: float = 0.0
    parcel_size_class: ParcelSize = ParcelSize.M
    service_level: ServiceLevel = ServiceLevel.SAME_DAY
    base_price: float = 0.0
    status: OrderStatus = OrderStatus.PUBLISHED
    assigned_driver_id: Optional[str] = None
    accepted_at: Optional[datetime] = None
    pickup_time: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    def is_expired(self, current_time: datetime) -> bool:
        """Check if order has expired based on latest departure time."""
        return current_time > self.latest_departure
    
    def is_available_for_assignment(self, current_time: datetime) -> bool:
        """Check if order can still be assigned."""
        return (self.status == OrderStatus.PUBLISHED and 
                not self.is_expired(current_time) and
                current_time <= self.latest_departure)
    
    def accept(self, driver_id: str, current_time: datetime):
        """Accept the order by a driver."""
        self.status = OrderStatus.ACCEPTED
        self.assigned_driver_id = driver_id
        self.accepted_at = current_time
    
    def deliver(self, current_time: datetime):
        """Mark order as delivered."""
        self.status = OrderStatus.DELIVERED
        self.delivered_at = current_time
    
    def cancel(self, reason: str = "Unknown"):
        """Cancel the order."""
        self.status = OrderStatus.CANCELLED
    
    def expire(self):
        """Mark order as expired."""
        self.status = OrderStatus.EXPIRED

@dataclass
class Driver:
    driver_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    home_base_lat: float = 0.0
    home_base_lng: float = 0.0
    current_lat: float = 0.0
    current_lng: float = 0.0
    available_from: datetime = field(default_factory=datetime.now)
    available_to: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=8))
    vehicle_type: VehicleType = VehicleType.CAR
    capacity_volume_l: float = 100.0
    max_weight_kg: float = 50.0
    max_detour_km: float = 10.0
    speed_kmph: float = 30.0
    acceptance_rate_7d: float = 0.8
    rating: float = 4.5
    wage_expectation_per_km: float = 0.5
    current_orders: list[str] = field(default_factory=list)
    total_earnings: float = 0.0
    driver_type: str = "general"  # metro, yango, shahzore, general
    max_orders: int = 3  # Maximum orders this driver can handle
    
    def is_available(self, current_time: datetime) -> bool:
        """Check if driver is currently available."""
        return (current_time >= self.available_from and 
                current_time <= self.available_to and
                len(self.current_orders) < self._get_max_orders())
    
    def can_accept_order(self, order: Order) -> bool:
        """Check if driver can accept this order based on capacity and constraints."""
        # Check capacity constraints
        if (order.parcel_volume_l > self.capacity_volume_l or 
            order.parcel_weight_kg > self.max_weight_kg):
            return False
        
        # Check if adding this order would exceed max orders
        if len(self.current_orders) >= self._get_max_orders():
            return False
        
        return True
    
    def accept_order(self, order_id: str):
        """Accept an order."""
        self.current_orders.append(order_id)
    
    def complete_order(self, order_id: str, earnings: float):
        """Complete an order and update earnings."""
        if order_id in self.current_orders:
            self.current_orders.remove(order_id)
            self.total_earnings += earnings
    
    def _get_max_orders(self) -> int:
        """Get maximum number of orders this driver can handle."""
        return self.max_orders

@dataclass
class Fleet:
    fleet_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    capacity_volume_l: float = 500.0
    max_weight_kg: float = 200.0
    cost_per_km: float = 2.0
    cost_per_min: float = 0.1
    dispatch_cutoff: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    current_location_lat: float = 0.0
    current_location_lng: float = 0.0
    is_available: bool = True
    
    def can_handle_order(self, order: Order) -> bool:
        """Check if fleet can handle this order."""
        return (order.parcel_volume_l <= self.capacity_volume_l and 
                order.parcel_weight_kg <= self.max_weight_kg)
    
    def calculate_cost(self, distance_km: float, time_minutes: float) -> float:
        """Calculate cost for a delivery."""
        return (distance_km * self.cost_per_km + 
                time_minutes * self.cost_per_min)
    
    def dispatch(self):
        """Mark fleet as dispatched."""
        self.is_available = False
    
    def return_to_base(self):
        """Mark fleet as available again."""
        self.is_available = True

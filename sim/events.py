"""
Event System for Cargo Hitchhiking Simulation
=============================================

This file contains the EVENT SYSTEM that drives the simulation forward.
Events are processed chronologically to simulate the passage of time.

EXECUTION ORDER:
===============
This file gets imported by sim/engine.py during the import phase.
Events are created and processed during the simulation run.

KEY CLASSES IN THIS FILE:
========================
- Event: Abstract base class for all events
- OrderArrival: Event when a new order arrives
- DriverArrival: Event when a driver becomes available
- Tick: Event that processes simulation state every 15 minutes
- Cancellation: Event when an order is cancelled
- DeliveryComplete: Event when a delivery is completed
- OrderPickup: Event when an order is picked up

FILES THAT USE THESE CLASSES:
=============================
- sim/engine.py: Creates and processes events in the main simulation loop
- sim/events.py: Defines event classes and their processing logic

CHRONOLOGICAL USAGE:
===================
1. sim/engine.py imports these event classes
2. _schedule_initial_events() creates initial events
3. run_simulation() processes events in chronological order
4. Each event.apply() method updates simulation state
5. Events trigger matching, KPI updates, and state changes

EVENT PROCESSING FLOW:
=====================
1. Event is created with a timestamp
2. Event is added to event_queue (sorted by timestamp)
3. run_simulation() pops next event from queue
4. event.apply(simulation_state) is called
5. Event updates simulation state (orders, drivers, KPIs)
6. New events may be scheduled as a result
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from enum import Enum

class EventType(Enum):
    ORDER_ARRIVAL = "order_arrival"
    DRIVER_ARRIVAL = "driver_arrival"
    TICK = "tick"
    CANCELLATION = "cancellation"
    DELIVERY_COMPLETE = "delivery_complete"
    ORDER_PICKUP = "order_pickup"

@dataclass
class Event(ABC):
    """Base class for all simulation events."""
    event_id: str
    timestamp: datetime
    event_type: EventType
    
    @abstractmethod
    def apply(self, simulation_state: Any) -> None:
        """Apply this event to the simulation state."""
        pass

@dataclass
class OrderArrival(Event):
    """Event when a new order arrives."""
    order_id: str
    order_data: dict
    
    def __init__(self, timestamp: datetime, order_id: str, order_data: dict):
        super().__init__(f"order_arrival_{order_id}", timestamp, EventType.ORDER_ARRIVAL)
        self.order_id = order_id
        self.order_data = order_data
    
    def apply(self, simulation_state: Any) -> None:
        """Add new order to the simulation."""
        from .entities import Order, ParcelSize, ServiceLevel
        from .config import get_time_slot, get_grid_cell, get_surge_multiplier
        
        # Create order from data
        order = Order(
            order_id=self.order_id,
            created_at=self.timestamp,
            pickup_lat=self.order_data.get('pickup_lat', 0.0),
            pickup_lng=self.order_data.get('pickup_lng', 0.0),
            drop_lat=self.order_data.get('drop_lat', 0.0),
            drop_lng=self.order_data.get('drop_lng', 0.0),
            time_window_start=self.order_data.get('time_window_start', self.timestamp),
            time_window_end=self.order_data.get('time_window_end', self.timestamp),
            latest_departure=self.order_data.get('latest_departure', self.timestamp),
            parcel_volume_l=self.order_data.get('parcel_volume_l', 0.0),
            parcel_weight_kg=self.order_data.get('parcel_weight_kg', 0.0),
            parcel_size_class=ParcelSize(self.order_data.get('parcel_size_class', 'M')),
            service_level=ServiceLevel(self.order_data.get('service_level', 'same_day')),
            base_price=self.order_data.get('base_price', 0.0)
        )
        
        # Calculate dynamic pricing if needed
        if simulation_state.pricing_model == "dynamic":
            time_slot = get_time_slot(self.timestamp)
            grid_cell = get_grid_cell(order.pickup_lat, order.pickup_lng)
            surge_multiplier = get_surge_multiplier(grid_cell, time_slot)
            order.base_price *= surge_multiplier
        
        simulation_state.orders[order.order_id] = order
        simulation_state.unassigned_orders.add(order.order_id)

@dataclass
class DriverArrival(Event):
    """Event when a new driver becomes available."""
    driver_id: str
    driver_data: dict
    
    def __init__(self, timestamp: datetime, driver_id: str, driver_data: dict):
        super().__init__(f"driver_arrival_{driver_id}", timestamp, EventType.DRIVER_ARRIVAL)
        self.driver_id = driver_id
        self.driver_data = driver_data
    
    def apply(self, simulation_state: Any) -> None:
        """Add new driver to the simulation."""
        from .entities import Driver, VehicleType
        
        driver = Driver(
            driver_id=self.driver_id,
            home_base_lat=self.driver_data.get('home_base_lat', 0.0),
            home_base_lng=self.driver_data.get('home_base_lng', 0.0),
            current_lat=self.driver_data.get('current_lat', 0.0),
            current_lng=self.driver_data.get('current_lng', 0.0),
            available_from=self.timestamp,
            available_to=self.driver_data.get('available_to', self.timestamp),
            vehicle_type=VehicleType(self.driver_data.get('vehicle_type', 'car')),
            capacity_volume_l=self.driver_data.get('capacity_volume_l', 100.0),
            max_weight_kg=self.driver_data.get('max_weight_kg', 50.0),
            max_detour_km=self.driver_data.get('max_detour_km', 10.0),
            speed_kmph=self.driver_data.get('speed_kmph', 30.0),
            acceptance_rate_7d=self.driver_data.get('acceptance_rate_7d', 0.8),
            rating=self.driver_data.get('rating', 4.5),
            wage_expectation_per_km=self.driver_data.get('wage_expectation_per_km', 0.5)
        )
        
        simulation_state.drivers[driver.driver_id] = driver
        simulation_state.available_drivers.add(driver.driver_id)

@dataclass
class Tick(Event):
    """Regular time tick event for simulation progression."""
    tick_number: int
    
    def __init__(self, timestamp: datetime, tick_number: int):
        super().__init__(f"tick_{tick_number}", timestamp, EventType.TICK)
        self.tick_number = tick_number
    
    def apply(self, simulation_state: Any) -> None:
        """Process tick: check expiries, trigger matching, update KPIs."""
        # Check for expired orders
        expired_orders = []
        for order_id in list(simulation_state.unassigned_orders):
            order = simulation_state.orders[order_id]
            if order.is_expired(self.timestamp):
                order.expire()
                expired_orders.append(order_id)
                simulation_state.unassigned_orders.remove(order_id)
        
        # Trigger matching if there are orders and drivers (more frequent)
        if (simulation_state.unassigned_orders and 
            simulation_state.available_drivers):
            simulation_state.trigger_matching()
        
        # Additional matching attempt for better coverage
        if simulation_state.unassigned_orders and simulation_state.available_drivers:
            simulation_state.trigger_matching()
        
        # Dispatch dedicated fleet for orders crossing deadline
        simulation_state.dispatch_dedicated_fleet()
        
        # Update KPIs
        simulation_state.update_kpis()
        
        # Log tick information
        simulation_state.log_tick(self.tick_number, len(expired_orders))

@dataclass
class Cancellation(Event):
    """Event when an order or driver is cancelled."""
    entity_id: str
    entity_type: str  # 'order' or 'driver'
    reason: str
    
    def __init__(self, timestamp: datetime, entity_id: str, entity_type: str, reason: str):
        super().__init__(f"cancellation_{entity_id}", timestamp, EventType.CANCELLATION)
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.reason = reason
    
    def apply(self, simulation_state: Any) -> None:
        """Handle cancellation of order or driver."""
        if self.entity_type == 'order':
            if self.entity_id in simulation_state.orders:
                order = simulation_state.orders[self.entity_id]
                order.cancel(self.reason)
                if self.entity_id in simulation_state.unassigned_orders:
                    simulation_state.unassigned_orders.remove(self.entity_id)
                if self.entity_id in simulation_state.assigned_orders:
                    simulation_state.assigned_orders.remove(self.entity_id)
        
        elif self.entity_type == 'driver':
            if self.entity_id in simulation_state.drivers:
                driver = simulation_state.drivers[self.entity_id]
                # Remove driver from available drivers
                if self.entity_id in simulation_state.available_drivers:
                    simulation_state.available_drivers.remove(self.entity_id)
                # Handle any assigned orders
                for order_id in list(driver.current_orders):
                    order = simulation_state.orders[order_id]
                    # Don't reset status - just move back to unassigned
                    simulation_state.unassigned_orders.add(order_id)
                    simulation_state.assigned_orders.remove(order_id)

@dataclass
class DeliveryComplete(Event):
    """Event when an order is successfully delivered."""
    order_id: str
    driver_id: str
    delivery_time: datetime
    actual_distance_km: float
    actual_time_minutes: float
    
    def __init__(self, timestamp: datetime, order_id: str, driver_id: str, 
                 delivery_time: datetime, actual_distance_km: float, actual_time_minutes: float):
        super().__init__(f"delivery_complete_{order_id}", timestamp, EventType.DELIVERY_COMPLETE)
        self.order_id = order_id
        self.driver_id = driver_id
        self.delivery_time = delivery_time
        self.actual_distance_km = actual_distance_km
        self.actual_time_minutes = actual_time_minutes
    
    def apply(self, simulation_state: Any) -> None:
        """Complete the delivery and update driver earnings."""
        if self.order_id in simulation_state.orders:
            order = simulation_state.orders[self.order_id]
            order.deliver(self.delivery_time)
            
            # Calculate driver earnings
            from .policies.pricing import calculate_driver_wage
            earnings = calculate_driver_wage(
                self.actual_distance_km,
                self.actual_time_minutes,
                simulation_state.wage_model,
                simulation_state.drivers[self.driver_id].rating
            )
            
            # Update driver
            if self.driver_id in simulation_state.drivers:
                driver = simulation_state.drivers[self.driver_id]
                driver.complete_order(self.order_id, earnings)
                
                # Make driver available again if they have no more orders
                if not driver.current_orders:
                    simulation_state.available_drivers.add(self.driver_id)
            
            # Remove from assigned orders
            if self.order_id in simulation_state.assigned_orders:
                simulation_state.assigned_orders.remove(self.order_id)
            
            # Update delivery statistics
            simulation_state.completed_deliveries += 1
            simulation_state.total_delivery_distance += self.actual_distance_km
            simulation_state.total_delivery_time += self.actual_time_minutes

@dataclass
class OrderPickup(Event):
    """Event when a driver picks up an order."""
    order_id: str
    driver_id: str
    pickup_time: datetime
    
    def __init__(self, timestamp: datetime, order_id: str, driver_id: str, pickup_time: datetime):
        super().__init__(f"order_pickup_{order_id}", timestamp, EventType.ORDER_PICKUP)
        self.order_id = order_id
        self.driver_id = driver_id
        self.pickup_time = pickup_time
    
    def apply(self, simulation_state: Any) -> None:
        """Handle order pickup."""
        if self.order_id in simulation_state.orders:
            order = simulation_state.orders[self.order_id]
            
            # Mark order as picked up
            order.pickup_time = self.pickup_time
            
            # Update driver location to pickup location
            if self.driver_id in simulation_state.drivers:
                driver = simulation_state.drivers[self.driver_id]
                driver.current_lat = order.pickup_lat
                driver.current_lng = order.pickup_lng

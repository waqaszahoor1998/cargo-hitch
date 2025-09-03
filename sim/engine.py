"""
Cargo Hitchhiking Simulation Engine
Core simulation logic for order-driver matching and delivery optimization.
"""

from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime, timedelta
import random
import math
from .entities import Order, Driver, Fleet, ParcelSize, ServiceLevel, VehicleType
from .events import Event, OrderArrival, DriverArrival, Tick, Cancellation, DeliveryComplete, OrderPickup
from .matcher.greedy import greedy_matching
from .kpi import KPITracker
from .config import (
    SIMULATION_START_TIME, SIMULATION_END_TIME, TICK_INTERVAL_MINUTES,
    DRIVER_GENERATION, ORDER_GENERATION, FLEET_CONFIG, ISLAMABAD_CENTER, CITY_RADIUS_KM,
    MAX_DETOUR_KM, MAX_BUNDLE_SIZE
)

class SimulationState:
    """Main simulation state container."""
    
    def __init__(self):
        # Core entities
        self.orders: Dict[str, Order] = {}
        self.drivers: Dict[str, Driver] = {}
        self.fleets: Dict[str, Fleet] = {}
        
        # Assignment tracking
        self.unassigned_orders: Set[str] = set()
        self.assigned_orders: Set[str] = set()
        self.available_drivers: Set[str] = set()
        
        # Simulation state
        self.current_time = SIMULATION_START_TIME
        self.tick_number = 0
        
        # Performance metrics
        self.completed_deliveries = 0
        self.total_delivery_distance = 0.0
        self.total_delivery_time = 0.0
        
        # Business configuration
        self.pricing_model = "dynamic"
        self.wage_model = "dynamic"
        self.base_price_multiplier = 1.0
        self.base_wage_multiplier = 1.0
        self.max_detour_km = MAX_DETOUR_KM
        self.bundle_size_limit = MAX_BUNDLE_SIZE
        
        # System components
        self.kpi_tracker = KPITracker()
        self.event_queue: List[Event] = []
        self.log = []
    
    def trigger_matching(self):
        """Trigger the matching algorithm to assign orders to drivers."""
        if self.unassigned_orders and self.available_drivers:
            best_matches = self._find_profitable_matches()
            
            for order_id, driver_id, profit in best_matches:
                if (order_id in self.unassigned_orders and 
                    driver_id in self.available_drivers):
                    
                    order = self.orders[order_id]
                    driver = self.drivers[driver_id]
                    
                    # Assign order to driver
                    order.accept(driver_id, self.current_time)
                    driver.accept_order(order_id)
                    
                    # Update tracking sets
                    self.unassigned_orders.remove(order_id)
                    self.assigned_orders.add(order_id)
                    
                    # Remove driver if at capacity
                    if len(driver.current_orders) >= driver._get_max_orders():
                        self.available_drivers.remove(driver_id)
                    
                    # Schedule delivery completion
                    self._schedule_delivery_completion(order, driver)
    
    def _find_profitable_matches(self) -> List[Tuple[str, str, float]]:
        """Find the most profitable order-driver matches."""
        matches = []
        
        for order_id in self.unassigned_orders:
            order = self.orders[order_id]
            
            for driver_id in self.available_drivers:
                driver = self.drivers[driver_id]
                
                if driver.can_accept_order(order):
                    profit = self._calculate_match_profit(order, driver)
                    matches.append((order_id, driver_id, profit))
        
        # Return top 10 most profitable matches
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches[:min(len(matches), 10)]
    
    def _calculate_match_profit(self, order: Order, driver: Driver) -> float:
        """Calculate profit for an order-driver match."""
        from .policies.pricing import calculate_driver_wage, calculate_platform_profit
        
        # Calculate driver wage
        distance = self._calculate_distance(
            driver.current_lat, driver.current_lng,
            order.pickup_lat, order.pickup_lng
        ) + self._calculate_distance(
            order.pickup_lat, order.pickup_lng,
            order.drop_lat, order.drop_lng
        )
        
        time_minutes = (distance / driver.speed_kmph) * 60
        driver_wage = calculate_driver_wage(
            distance, time_minutes, 
            self.wage_model, driver.rating
        )
        
        # Calculate platform profit
        platform_profit = calculate_platform_profit(order.base_price, driver_wage)
        
        return platform_profit
    
    def dispatch_dedicated_fleet(self):
        """Dispatch dedicated fleet for orders crossing deadline."""
        # This method will be called by events to dispatch fleet
        pass
    
    def update_kpis(self):
        """Update KPI metrics."""
        # This method will be called by events to update KPIs
        pass
    
    def log_tick(self, tick_number: int, expired_count: int):
        """Log tick information."""
        # This method will be called by events to log tick info
        pass
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points."""
        from .config import calculate_distance
        return calculate_distance(lat1, lng1, lat2, lng2)
    
    def _schedule_delivery_completion(self, order: Order, driver: Driver):
        """Schedule when the delivery will be completed."""
        # Calculate delivery time
        pickup_distance = self._calculate_distance(
            driver.current_lat, driver.current_lng,
            order.pickup_lat, order.pickup_lng
        )
        
        delivery_distance = self._calculate_distance(
            order.pickup_lat, order.pickup_lng,
            order.drop_lat, order.drop_lng
        )
        
        time_to_pickup = (pickup_distance / driver.speed_kmph) * 60
        delivery_time = (delivery_distance / driver.speed_kmph) * 60
        
        total_time = time_to_pickup + delivery_time
        
        # Ensure delivery happens within simulation time
        max_delivery_time = 30  # Maximum 30 minutes for delivery
        total_time = min(total_time, max_delivery_time)
        
        # Ensure delivery happens within the simulation day
        completion_time = self.current_time + timedelta(minutes=total_time)
        
        # If delivery would be after simulation end, schedule it for current time + small delay
        if completion_time > SIMULATION_END_TIME:
            completion_time = self.current_time + timedelta(minutes=5)  # 5 minutes from now
        
        # Create delivery completion event
        from .events import DeliveryComplete, OrderPickup
        event = DeliveryComplete(
            completion_time,
            order.order_id,
            driver.driver_id,
            completion_time,
            pickup_distance + delivery_distance,
            total_time
        )
        
        # Schedule the event
        self._schedule_event(event)
        
        # Also schedule a pickup event (when driver reaches pickup location)
        pickup_time = self.current_time + timedelta(minutes=time_to_pickup)
        pickup_event = OrderPickup(
            pickup_time,
            order.order_id,
            driver.driver_id,
            pickup_time
        )
        self._schedule_event(pickup_event)
    
    def _schedule_event(self, event: Event):
        """Schedule an event in the event queue."""
        self.event_queue.append(event)
        # Sort by timestamp
        self.event_queue.sort(key=lambda e: e.timestamp)

class CargoHitchhikingSimulation:
    """Main simulation class."""
    
    def __init__(self, config: dict = None):
        self.state = SimulationState()
        self.config = config or {}
        self.setup_simulation()
    
    def setup_simulation(self):
        """Initialize simulation with orders, drivers, and fleets."""
        # Apply config values to simulation state
        if self.config:
            if 'max_detour_km' in self.config:
                self.state.max_detour_km = self.config['max_detour_km']
            if 'base_price_multiplier' in self.config:
                self.state.base_price_multiplier = self.config['base_price_multiplier']
        
        self._generate_orders()
        self._generate_drivers()
        self._generate_fleets()
        self._schedule_initial_events()
    
    def apply_scenario_config(self, config):
        """Apply scenario configuration to the simulation."""
        from .scenario import ScenarioConfig
        
        if isinstance(config, ScenarioConfig):
            # Apply pricing parameters
            if hasattr(config, 'base_price_multiplier'):
                # Update pricing in the simulation state
                self.state.base_price_multiplier = config.base_price_multiplier
            
            # Apply wage parameters
            if hasattr(config, 'base_wage_multiplier'):
                self.state.base_wage_multiplier = config.base_wage_multiplier
            
            # Apply matching parameters
            if hasattr(config, 'max_detour_km'):
                self.state.max_detour_km = config.max_detour_km
            
            if hasattr(config, 'bundle_size_limit'):
                self.state.bundle_size_limit = config.bundle_size_limit
            
            # Apply supply/demand parameters
            if hasattr(config, 'demand_multiplier') and config.demand_multiplier != 1.0:
                # Regenerate orders with new demand
                self._regenerate_orders_with_demand(config.demand_multiplier)
            
            if hasattr(config, 'supply_multiplier') and config.supply_multiplier != 1.0:
                # Regenerate drivers with new supply
                self._regenerate_drivers_with_supply(config.supply_multiplier)
            
            print(f"✅ Applied scenario configuration: {config.name}")
            print(f"   - Base price multiplier: {getattr(config, 'base_price_multiplier', 1.0)}")
            print(f"   - Base wage multiplier: {getattr(config, 'base_wage_multiplier', 1.0)}")
            print(f"   - Max detour: {getattr(config, 'max_detour_km', 'default')} km")
            print(f"   - Bundle size limit: {getattr(config, 'bundle_size_limit', 'default')}")
    
    def _regenerate_orders_with_demand(self, demand_multiplier: float):
        """Regenerate orders with adjusted demand."""
        # Clear existing orders
        self.state.orders.clear()
        self.state.unassigned_orders.clear()
        self.state.assigned_orders.clear()
        
        # Generate new orders with adjusted count
        from .config import ORDER_GENERATION
        new_order_count = int(ORDER_GENERATION['total_orders'] * demand_multiplier)
        
        for i in range(new_order_count):
            order = self._create_random_order(f"order_{i}")
            self.state.orders[order.order_id] = order
            self.state.unassigned_orders.add(order.order_id)
    
    def _regenerate_drivers_with_supply(self, supply_multiplier: float):
        """Regenerate drivers with adjusted supply."""
        # Clear existing drivers
        self.state.drivers.clear()
        self.state.available_drivers.clear()
        
        # Generate new drivers with adjusted count
        from .config import DRIVER_GENERATION
        new_driver_count = int(DRIVER_GENERATION['total_drivers'] * supply_multiplier)
        
        for i in range(new_driver_count):
            driver = self._create_random_driver(f"driver_{i}")
            self.state.drivers[driver.driver_id] = driver
            self.state.available_drivers.add(driver.driver_id)
    
    def _generate_orders(self):
        """Generate initial orders based on configuration."""
        # Use config value if provided, otherwise use default
        num_orders = self.config.get('total_orders', ORDER_GENERATION['total_orders'])
        
        for i in range(num_orders):
            order = self._create_random_order(f"order_{i}")
            self.state.orders[order.order_id] = order
            self.state.unassigned_orders.add(order.order_id)
    
    def _create_random_order(self, order_id: str) -> Order:
        """Create a random order with realistic parameters."""
        # Random location within Islamabad
        pickup_lat, pickup_lng = self._random_location_in_city()
        drop_lat, drop_lng = self._random_location_in_city()
        
        # Random time window - much more realistic for Metro delivery
        time_window_start = self.state.current_time + timedelta(
            hours=random.uniform(0, 4)  # Orders can start within 4 hours
        )
        time_window_end = time_window_start + timedelta(
            hours=random.uniform(6, 18)  # Much longer delivery windows
        )
        latest_departure = time_window_start + timedelta(
            hours=random.uniform(4, 12)  # Much more time for drivers to reach pickup
        )
        
        # Random parcel characteristics
        size_class = random.choices(
            list(ParcelSize), 
            weights=[ORDER_GENERATION['size_distribution'][s.value] for s in ParcelSize]
        )[0]
        
        service_level = random.choices(
            list(ServiceLevel),
            weights=[ORDER_GENERATION['service_level_distribution'][s.value] for s in ServiceLevel]
        )[0]
        
        # Calculate base price based on distance and size
        distance = self._calculate_distance(pickup_lat, pickup_lng, drop_lat, drop_lng)
        base_price = self._calculate_base_price(distance, size_class, service_level)
        
        return Order(
            order_id=order_id,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            drop_lat=drop_lat,
            drop_lng=drop_lng,
            time_window_start=time_window_start,
            time_window_end=time_window_end,
            latest_departure=latest_departure,
            parcel_volume_l=random.uniform(0.1, 50.0),
            parcel_weight_kg=random.uniform(0.1, 20.0),
            parcel_size_class=size_class,
            service_level=service_level,
            base_price=base_price
        )
    
    def _generate_drivers(self):
        """Generate initial drivers based on configuration."""
        # Use config value if provided, otherwise use default
        num_drivers = self.config.get('total_drivers', DRIVER_GENERATION['total_drivers'])
        
        for i in range(num_drivers):
            driver = self._create_random_driver(f"driver_{i}")
            self.state.drivers[driver.driver_id] = driver
            self.state.available_drivers.add(driver.driver_id)
    
    def _create_random_driver(self, driver_id: str) -> Driver:
        """Create a random driver with realistic parameters."""
        # Random location within Islamabad
        home_lat, home_lng = self._random_location_in_city()
        current_lat, current_lng = self._random_location_in_city()
        
        # Random availability pattern
        availability_pattern = random.choice(list(DRIVER_GENERATION['availability_patterns'].keys()))
        start_hour, end_hour = DRIVER_GENERATION['availability_patterns'][availability_pattern]
        
        available_from = self.state.current_time.replace(hour=start_hour, minute=0)
        available_to = self.state.current_time.replace(hour=end_hour, minute=0)
        
        # Random vehicle type
        vehicle_type = random.choices(
            list(VehicleType),
            weights=[DRIVER_GENERATION['vehicle_distribution'][v.value] for v in VehicleType]
        )[0]
        
        # Set capacity based on vehicle type
        capacity_map = {
            VehicleType.BIKE: (5.0, 10.0),
            VehicleType.MOTORBIKE: (15.0, 25.0),
            VehicleType.CAR: (50.0, 100.0),
            VehicleType.VAN: (200.0, 500.0)
        }
        
        capacity_volume, max_weight = capacity_map[vehicle_type]
        
        return Driver(
            driver_id=driver_id,
            home_base_lat=home_lat,
            home_base_lng=home_lng,
            current_lat=current_lat,
            current_lng=current_lng,
            available_from=available_from,
            available_to=available_to,
            vehicle_type=vehicle_type,
            capacity_volume_l=capacity_volume,
            max_weight_kg=max_weight,
            max_detour_km=random.uniform(5.0, 15.0),
            speed_kmph=random.uniform(25.0, 40.0),
            acceptance_rate_7d=random.uniform(0.6, 0.95),
            rating=random.uniform(3.5, 5.0),
            wage_expectation_per_km=random.uniform(0.3, 0.8)
        )
    
    def _generate_fleets(self):
        """Generate dedicated fleet vehicles."""
        num_fleets = FLEET_CONFIG['num_vehicles']
        
        for i in range(num_fleets):
            fleet = Fleet(
                fleet_id=f"fleet_{i}",
                capacity_volume_l=FLEET_CONFIG['capacity_volume_l'],
                max_weight_kg=FLEET_CONFIG['max_weight_kg'],
                cost_per_km=FLEET_CONFIG['cost_per_km'],
                cost_per_min=FLEET_CONFIG['cost_per_min'],
                current_location_lat=ISLAMABAD_CENTER[0],
                current_location_lng=ISLAMABAD_CENTER[1]
            )
            self.state.fleets[fleet.fleet_id] = fleet
    
    def _schedule_initial_events(self):
        """Schedule initial events for the simulation."""
        # Orders are already created, no need for OrderArrival events
        
        # Schedule driver arrivals
        for driver in self.state.drivers.values():
            arrival_time = driver.available_from
            event = DriverArrival(arrival_time, driver.driver_id, {})
            self._schedule_event(event)
        
        # Schedule regular ticks
        current_time = SIMULATION_START_TIME
        tick_number = 0
        
        while current_time <= SIMULATION_END_TIME:
            event = Tick(current_time, tick_number)
            self._schedule_event(event)
            current_time += timedelta(minutes=TICK_INTERVAL_MINUTES)
            tick_number += 1
    
    def _schedule_event(self, event: Event):
        """Schedule an event in the event queue."""
        self.state.event_queue.append(event)
        # Sort by timestamp
        self.state.event_queue.sort(key=lambda e: e.timestamp)
    
    def _random_location_in_city(self) -> tuple:
        """Generate a random location within Islamabad city limits."""
        center_lat, center_lng = ISLAMABAD_CENTER
        
        # Random angle and radius
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, CITY_RADIUS_KM)
        
        # Convert to lat/lng offset (more accurate conversion)
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 * cos(latitude) km
        lat_offset = radius * math.cos(angle) / 111.0
        lng_offset = radius * math.sin(angle) / (111.0 * math.cos(math.radians(center_lat)))
        
        # Ensure coordinates stay within reasonable bounds
        new_lat = center_lat + lat_offset
        new_lng = center_lng + lng_offset
        
        # Validate coordinates are within city bounds
        if abs(new_lat - center_lat) > 0.25:  # Max ~27km north/south
            new_lat = center_lat + (0.25 if lat_offset > 0 else -0.25)
        if abs(new_lng - center_lng) > 0.25:  # Max ~27km east/west
            new_lng = center_lng + (0.25 if lng_offset > 0 else -0.25)
        
        return new_lat, new_lng
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points."""
        from .config import calculate_distance
        return calculate_distance(lat1, lng1, lat2, lng2)
    
    def _calculate_base_price(self, distance: float, size_class: ParcelSize, service_level: ServiceLevel) -> float:
        """Calculate base price for an order using Metro Cash & Carry pricing model."""
        # Metro Cash & Carry uses fixed pricing: Rs 99 for standard, Rs 129 for premium
        # For simulation, use distance-based pricing but with realistic Metro rates
        
        # Base Metro pricing (Rs per km)
        metro_base_rate = 3.0  # Rs 3 per km (more realistic for Metro)
        
        # Size adjustments (smaller impact for Metro)
        size_multiplier = {
            "XS": 0.8,   # Small packages
            "S": 0.9,    # Medium packages  
            "M": 1.0,    # Large packages (base)
            "L": 1.2,    # Extra large packages
            "XL": 1.5    # Oversized packages
        }
        
        # Service level adjustments
        service_multiplier = {
            "same_day": 1.3,    # Premium for same day
            "next_day": 1.0,    # Standard rate
            "flex": 0.8         # Discount for flexible delivery
        }
        
        size_factor = size_multiplier.get(size_class.value, 1.0)
        service_factor = service_multiplier.get(service_level.value, 1.0)
        
        # Calculate price with minimum and maximum bounds
        base_price = metro_base_rate * distance * size_factor * service_factor
        
        # Ensure realistic bounds (Rs 50-200 for typical deliveries)
        base_price = max(50, min(200, base_price))
        
        return base_price
    
    def run_simulation(self):
        """Run the main simulation loop."""
        print(f"Starting simulation from {SIMULATION_START_TIME} to {SIMULATION_END_TIME}")
        
        event_count = 0
        while self.state.event_queue:
            event = self.state.event_queue.pop(0)
            event_count += 1
            
            # Update current time
            self.state.current_time = event.timestamp
            
            # Apply event
            event.apply(self.state)
            
            # Log event
            self._log_event(event)
            
            # Update KPIs periodically
            if isinstance(event, Tick):
                self.state.kpi_tracker.update_metrics(
                    self.state.orders, 
                    self.state.drivers, 
                    self.state.fleets
                )
                
                if self.state.tick_number % 4 == 0:  # Every hour
                    print(f"Tick {self.state.tick_number}: {len(self.state.unassigned_orders)} unmatched orders, "
                          f"{len(self.state.available_drivers)} available drivers")
                
                self.state.tick_number += 1
            

        
        print(f"\nTotal events processed: {event_count}")
        print(f"Final time: {self.state.current_time}")
        
        print("\nSimulation completed!")
    
    def trigger_matching(self):
        """Trigger the matching algorithm."""
        if not self.state.unassigned_orders or not self.state.available_drivers:
            return
        
        # Get current available orders and drivers
        available_orders = [self.state.orders[order_id] for order_id in self.state.unassigned_orders]
        available_drivers = [self.state.drivers[driver_id] for driver_id in self.state.available_drivers]
        
        # Run matching algorithm
        assignments = greedy_matching(
            available_orders, 
            available_drivers, 
            self.state.current_time,
            allow_bundling=True
        )
        
        # Process assignments
        for order, driver in assignments:
            if (order.order_id in self.state.unassigned_orders and 
                driver.driver_id in self.state.available_drivers):
                
                # Make assignment
                order.accept(driver.driver_id, self.state.current_time)
                driver.accept_order(order.order_id)
                
                # Update sets
                self.state.unassigned_orders.remove(order.order_id)
                self.state.assigned_orders.add(order.order_id)
                
                # Remove driver from available if they have max orders
                if len(driver.current_orders) >= driver._get_max_orders():
                    self.state.available_drivers.remove(driver.driver_id)
                
                # Schedule delivery completion
                self.state._schedule_delivery_completion(order, driver)
    

    
    def dispatch_dedicated_fleet(self):
        """Dispatch dedicated fleet for orders crossing deadline."""
        # Find orders that need fleet dispatch
        for order_id in list(self.state.unassigned_orders):
            order = self.state.orders[order_id]
            
            # Check if order is close to deadline
            time_until_deadline = (order.latest_departure - self.state.current_time).total_seconds() / 60
            
            if time_until_deadline <= 30:  # 30 minutes before deadline
                # Find available fleet
                available_fleet = None
                for fleet in self.state.fleets.values():
                    if fleet.is_available and fleet.can_handle_order(order):
                        available_fleet = fleet
                        break
                
                if available_fleet:
                    # Dispatch fleet
                    available_fleet.dispatch()
                    order.accept(f"fleet_{available_fleet.fleet_id}", self.state.current_time)
                    
                    # Update sets
                    self.state.unassigned_orders.remove(order_id)
                    self.state.assigned_orders.add(order_id)
                    
                    # Schedule fleet return
                    self._schedule_fleet_return(available_fleet, order)
    
    def _schedule_fleet_return(self, fleet: Fleet, order: Order):
        """Schedule when the fleet will return to base."""
        # Calculate delivery time
        delivery_distance = self._calculate_distance(
            fleet.current_location_lat, fleet.current_location_lng,
            order.drop_lat, order.drop_lng
        )
        
        delivery_time = (delivery_distance / 30.0) * 60  # Assume 30 km/h average speed
        return_time = self.state.current_time + timedelta(minutes=delivery_time)
        
        # Create fleet return event (simplified)
        # In a full implementation, this would be a FleetReturn event
        
        # For now, just mark fleet as available after delivery
        def return_fleet():
            fleet.return_to_base()
            fleet.current_location_lat = order.drop_lat
            fleet.current_location_lng = order.drop_lng
        
        # Schedule return (simplified)
        # In practice, you'd create a proper event for this
    
    def update_kpis(self):
        """Update KPI metrics."""
        self.state.kpi_tracker.update_metrics(
            self.state.orders, 
            self.state.drivers, 
            self.state.fleets
        )
    
    def _log_event(self, event: Event):
        """Log an event for debugging."""
        log_entry = {
            'timestamp': event.timestamp,
            'event_type': event.event_type.value,
            'event_id': event.event_id
        }
        self.state.log.append(log_entry)
    
    def get_results(self) -> dict:
        """Get simulation results."""
        # Force a final KPI update to ensure accurate counts
        self.state.kpi_tracker.update_metrics(
            self.state.orders, 
            self.state.drivers, 
            self.state.fleets
        )
        
        # Calculate matched orders from KPI metrics for consistency
        matched_orders = self.state.kpi_tracker.metrics.matched_orders
        
        return {
            'orders': len(self.state.orders),
            'drivers': len(self.state.drivers),
            'matched_orders': matched_orders,
            'unmatched_orders': len(self.state.unassigned_orders),
            'completed_deliveries': self.state.completed_deliveries,
            'kpi_summary': self.state.kpi_tracker.get_summary()
        }

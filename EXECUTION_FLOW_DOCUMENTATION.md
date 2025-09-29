# Complete Execution Flow Documentation
## Cargo Hitchhiking Simulation System

This document provides a comprehensive, chronological breakdown of how the cargo simulation system works when you run `python main.py`.

---

##   **Phase 1: Import Phase (Immediate Execution)**

When you run `python main.py`, Python immediately executes the import statements in this exact order:

### **1. main.py starts execution**
```python
# File: main.py
# Line: 1-61
#!/usr/bin/env python3
"""
Cargo Hitchhiking Simulation System
===================================
[Documentation and execution flow comments]
"""

# Import statements execute immediately
import time                    # For measuring execution time
import random                  # For generating random data
from sim.engine import CargoHitchhikingSimulation  # ← TRIGGERS sim/__init__.py
import sim.config as config   # ← TRIGGERS sim/config.py
```

### **2. sim/__init__.py loads (via import)**
```python
# File: sim/__init__.py
# Lines: 40-55
from .engine import CargoHitchhikingSimulation  # ← TRIGGERS sim/engine.py
from .entities import Order, Driver, Fleet      # ← TRIGGERS sim/entities.py
from .kpi import KPITracker                     # ← TRIGGERS sim/kpi.py
```

### **3. sim/config.py loads (via import)**
```python
# File: sim/config.py
# Lines: 1-697
# All configuration data loads immediately:
# - Real Metro store locations
# - Customer survey data (131 responses)
# - Metro bus stop locations
# - Delivery areas
# - Pricing models
# - KPI targets
```

### **4. sim/engine.py loads (via import)**
```python
# File: sim/engine.py
# Lines: 48-70
from .entities import Order, Driver, Fleet, ParcelSize, ServiceLevel, VehicleType  # ← TRIGGERS sim/entities.py
from .events import Event, OrderArrival, DriverArrival, Tick, Cancellation, DeliveryComplete, OrderPickup  # ← TRIGGERS sim/events.py
from .matcher.greedy import greedy_matching  # ← TRIGGERS sim/matcher/greedy.py
from .kpi import KPITracker  # ← TRIGGERS sim/kpi.py
from .config import (...)  # ← TRIGGERS sim/config.py (already loaded)
```

### **5. sim/entities.py loads (via import)**
```python
# File: sim/entities.py
# Lines: 1-174
# Pure data classes with no imports of other sim files
# Defines: Order, Driver, Fleet, ParcelSize, ServiceLevel, VehicleType, OrderStatus
```

### **6. sim/events.py loads (via import)**
```python
# File: sim/events.py
# Lines: 40-42
from .entities import Order, ParcelSize, ServiceLevel  # ← TRIGGERS sim/entities.py (already loaded)
from .config import get_time_slot, get_grid_cell, get_surge_multiplier  # ← TRIGGERS sim/config.py (already loaded)
```

### **7. sim/matcher/greedy.py loads (via import)**
```python
# File: sim/matcher/greedy.py
# Lines: 4-6
from ..entities import Order, Driver  # ← TRIGGERS sim/entities.py (already loaded)
from .filters import filter_feasible_matches, is_feasible_match  # ← TRIGGERS sim/matcher/filters.py
from ..config import MAX_BUNDLE_SIZE  # ← TRIGGERS sim/config.py (already loaded)
```

### **8. sim/matcher/filters.py loads (via import)**
```python
# File: sim/matcher/filters.py
# Likely imports sim/entities.py (already loaded)
```

### **9. sim/kpi.py loads (via import)**
```python
# File: sim/kpi.py
# Lines: 9-10
from .config import KPI_TARGETS  # ← TRIGGERS sim/config.py (already loaded)
```

---

##   **Phase 2: Execution Phase (When main() runs)**

After all imports are complete, Python executes the main program:

### **10. main.py main execution starts**
```python
# File: main.py
# Lines: 1958-2005
if __name__ == "__main__":
    print("CARGO HITCHHIKING SIMULATION")
    print("=" * 50)
    print("Interactive simulation with multiple output options")
    print("=" * 50)

    try:
        run_interactive_simulation()  # ← CALLS main.py function
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nError: {e}")
```

### **11. run_interactive_simulation() function executes**
```python
# File: main.py
# Lines: 1425-1501
def run_interactive_simulation():
    """
    MAIN SIMULATION FUNCTION - This is the core function that runs everything!
    """
    print("CARGO HITCHHIKING SIMULATION")
    print("=" * 50)
    print("Running hybrid Metro + Yango delivery simulation...")
    print("=" * 50)

    # STEP 1: Import real data from sim.config
    from sim.config import (
        REAL_CUSTOMER_DATA, REAL_METRO_OPERATIONAL_DATA,
        REAL_METRO_STORES, REAL_METRO_BUS_STOPS, REAL_DELIVERY_AREAS
    )

    # STEP 2: Create hybrid configuration
    config = {
        'total_orders': 280,  # From Metro Excel data
        'total_drivers': 13 + 100 + 5,  # Metro + Yango + Shahzore
        'metro_drivers': 13,  # 1 driver per Metro bus
        'yango_drivers': 100,  # Yango delivery drivers
        'shahzore_trucks': 5,  # For large deliveries
        'max_detour_km': 14,  # 14km from Excel
        'base_price_multiplier': 1.2,  # 20% price increase
        'use_hybrid_delivery': True,  # Enable hybrid model
        # ... more configuration
    }

    # STEP 3: Create and run simulation
    print("Running hybrid simulation...")
    
    # This calls sim.engine.CargoHitchhikingSimulation.__init__()
    simulation = CargoHitchhikingSimulation(config)
    
    # This calls sim.engine.run_simulation()
    simulation.run_simulation()
    
    # This calls sim.engine.get_results()
    results = simulation.get_results()
```

### **12. CargoHitchhikingSimulation.__init__() executes**
```python
# File: sim/engine.py
# Lines: 335-367
def __init__(self, config: dict = None):
    """
    INITIALIZE SIMULATION
    =====================
    
    This method gets called by main.py when creating the simulation.
    """
    # Create the simulation state container
    self.state = SimulationState()  # ← CALLS SimulationState.__init__()
    
    # Store configuration parameters
    self.config = config or {}
    
    # Set up the simulation (generate orders, drivers, events)
    self.setup_simulation()  # ← CALLS setup_simulation()
```

### **13. SimulationState.__init__() executes**
```python
# File: sim/engine.py
# Lines: 100-150
def __init__(self):
    """
    INITIALIZE SIMULATION STATE
    ===========================
    
    This method sets up all the data structures for the simulation.
    """
    # Core entities
    self.orders: Dict[str, Order] = {}      # All orders: {order_id: Order}
    self.drivers: Dict[str, Driver] = {}    # All drivers: {driver_id: Driver}
    self.fleets: Dict[str, Fleet] = {}      # All fleet vehicles: {fleet_id: Fleet}
    
    # Assignment tracking
    self.unassigned_orders: Set[str] = set()    # Order IDs waiting for drivers
    self.assigned_orders: Set[str] = set()      # Order IDs matched to drivers
    self.available_drivers: Set[str] = set()    # Driver IDs available for new orders
    
    # Simulation state
    self.current_time = SIMULATION_START_TIME  # Current simulation time (8 AM)
    self.tick_number = 0                       # Number of time ticks processed
    
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
    self.kpi_tracker = KPITracker()  # ← CALLS sim/kpi.py KPITracker.__init__()
    self.event_queue: List[Event] = []
    self.log = []
```

### **14. KPITracker.__init__() executes**
```python
# File: sim/kpi.py
# Lines: 54-55
def __init__(self):
    self.metrics = KPIMetrics()  # ← CALLS KPIMetrics.__init__()
```

### **15. setup_simulation() executes**
```python
# File: sim/engine.py
# Lines: 369-383
def setup_simulation(self):
    """
    Initialize simulation with orders, drivers, and fleets.
    """
    # Apply config values to simulation state
    if self.config:
        if 'max_detour_km' in self.config:
            self.state.max_detour_km = self.config['max_detour_km']
        if 'base_price_multiplier' in self.config:
            self.state.base_price_multiplier = self.config['base_price_multiplier']
    
    self._generate_orders()    # ← CALLS _generate_orders()
    self._generate_drivers()  # ← CALLS _generate_drivers()
    self._generate_fleets()   # ← CALLS _generate_fleets()
    self._schedule_initial_events()  # ← CALLS _schedule_initial_events()
```

### **16. _generate_orders() executes**
```python
# File: sim/engine.py
# Lines: 303-311
def _generate_orders(self):
    """
    Generate initial orders based on configuration.
    """
    # Use config value if provided, otherwise use default
    num_orders = self.config.get('total_orders', ORDER_GENERATION['total_orders'])
    
    for i in range(num_orders):
        order = self._create_realistic_order(f"order_{i}")  # ← CALLS _create_realistic_order()
        self.state.orders[order.order_id] = order
        self.state.unassigned_orders.add(order.order_id)
```

### **17. _generate_drivers() executes**
```python
# File: sim/engine.py
# Lines: 433-454
def _generate_drivers(self):
    """
    Generate drivers based on hybrid Metro + Yango configuration.
    """
    # Metro drivers: 13 (1 per bus)
    metro_drivers = self.config.get('metro_drivers', 13)
    for i in range(metro_drivers):
        driver = self._create_metro_driver(f"metro_driver_{i}")  # ← CALLS _create_metro_driver()
        self.state.drivers[driver.driver_id] = driver
        self.state.available_drivers.add(driver.driver_id)
    
    # Yango drivers: Variable based on demand
    yango_drivers = self.config.get('yango_drivers', 50)
    for i in range(yango_drivers):
        driver = self._create_yango_driver(f"yango_driver_{i}")  # ← CALLS _create_yango_driver()
        self.state.drivers[driver.driver_id] = driver
        self.state.available_drivers.add(driver.driver_id)
    
    # Shahzore trucks for big deliveries
    shahzore_trucks = self.config.get('shahzore_trucks', 5)
    for i in range(shahzore_trucks):
        driver = self._create_shahzore_driver(f"shahzore_driver_{i}")  # ← CALLS _create_shahzore_driver()
        self.state.drivers[driver.driver_id] = driver
        self.state.available_drivers.add(driver.driver_id)
```

### **18. _generate_fleets() executes**
```python
# File: sim/engine.py
# Lines: 582-596
def _generate_fleets(self):
    """
    Generate dedicated fleet vehicles.
    """
    num_fleets = FLEET_CONFIG['num_vehicles']
    
    for i in range(num_fleets):
        fleet = Fleet(  # ← CREATES Fleet object from sim/entities.py
            fleet_id=f"fleet_{i}",
            capacity_volume_l=FLEET_CONFIG['capacity_volume_l'],
            max_weight_kg=FLEET_CONFIG['max_weight_kg'],
            cost_per_km=FLEET_CONFIG['cost_per_km'],
            cost_per_min=FLEET_CONFIG['cost_per_min'],
            current_location_lat=ISLAMABAD_CENTER[0],
            current_location_lng=ISLAMABAD_CENTER[1]
        )
        self.state.fleets[fleet.fleet_id] = fleet
```

### **19. _schedule_initial_events() executes**
```python
# File: sim/engine.py
# Lines: 598-616
def _schedule_initial_events(self):
    """
    Schedule initial events for the simulation.
    """
    # Schedule driver arrivals
    for driver in self.state.drivers.values():
        arrival_time = driver.available_from
        event = DriverArrival(arrival_time, driver.driver_id, {})  # ← CREATES DriverArrival event
        self._schedule_event(event)
    
    # Schedule regular ticks
    current_time = SIMULATION_START_TIME
    tick_number = 0
    
    while current_time <= SIMULATION_END_TIME:
        event = Tick(current_time, tick_number)  # ← CREATES Tick event
        self._schedule_event(event)
        current_time += timedelta(minutes=TICK_INTERVAL_MINUTES)
        tick_number += 1
```

### **20. run_simulation() executes**
```python
# File: sim/engine.py
# Lines: 714-742
def run_simulation(self):
    """
    Run the main simulation loop.
    """
    # Run simulation silently for cleaner output
    event_count = 0
    while self.state.event_queue:
        event = self.state.event_queue.pop(0)  # Get next event
        event_count += 1
        
        # Update current time
        self.state.current_time = event.timestamp
        
        # Apply event
        event.apply(self.state)  # ← CALLS sim/events.py event processing
        
        # Log event
        self._log_event(event)
        
        # Update KPIs periodically
        if isinstance(event, Tick):
            self.state.kpi_tracker.update_metrics(  # ← CALLS sim/kpi.py update_metrics()
                self.state.orders, 
                self.state.drivers, 
                self.state.fleets
            )
            
            self.state.tick_number += 1
```

### **21. Event processing in sim/events.py**
```python
# File: sim/events.py
# Lines: 117-144
def apply(self, simulation_state: Any) -> None:
    """
    Process tick: check expiries, trigger matching, update KPIs.
    """
    # Check for expired orders
    expired_orders = []
    for order_id in list(simulation_state.unassigned_orders):
        order = simulation_state.orders[order_id]
        if order.is_expired(self.timestamp):
            order.expire()
            expired_orders.append(order_id)
            simulation_state.unassigned_orders.remove(order_id)
    
    # Trigger matching if there are orders and drivers
    if (simulation_state.unassigned_orders and 
        simulation_state.available_drivers):
        simulation_state.trigger_matching()  # ← CALLS sim/engine.py trigger_matching()
    
    # Additional matching attempt for better coverage
    if simulation_state.unassigned_orders and simulation_state.available_drivers:
        simulation_state.trigger_matching()  # ← CALLS sim/engine.py trigger_matching()
    
    # Dispatch dedicated fleet for orders crossing deadline
    simulation_state.dispatch_dedicated_fleet()
    
    # Update KPIs
    simulation_state.update_kpis()  # ← CALLS sim/engine.py update_kpis()
    
    # Log tick information
    simulation_state.log_tick(self.tick_number, len(expired_orders))
```

### **22. trigger_matching() executes**
```python
# File: sim/engine.py
# Lines: 56-91
def trigger_matching(self):
    """
    Trigger the matching algorithm to assign orders to drivers.
    """
    if not self.unassigned_orders or not self.available_drivers:
        return
    
    # Get current available orders and drivers
    available_orders = [self.orders[order_id] for order_id in self.unassigned_orders]
    available_drivers = [self.drivers[driver_id] for driver_id in self.available_drivers]
    
    # Run improved matching algorithm
    assignments = greedy_matching(  # ← CALLS sim/matcher/greedy.py greedy_matching()
        available_orders, 
        available_drivers, 
        self.current_time,
        allow_bundling=True
    )
    
    # Process assignments
    for order, driver in assignments:
        if (order.order_id in self.unassigned_orders and 
            driver.driver_id in self.available_drivers):
            
            # Make assignment
            order.accept(driver.driver_id, self.current_time)
            driver.accept_order(order.order_id)
            
            # Update sets
            self.unassigned_orders.remove(order.order_id)
            self.assigned_orders.add(order.order_id)
            
            # Remove driver from available if they have max orders
            if len(driver.current_orders) >= driver._get_max_orders():
                self.available_drivers.remove(driver.driver_id)
            
            # Schedule delivery completion
            self._schedule_delivery_completion(order, driver)
```

### **23. greedy_matching() in sim/matcher/greedy.py**
```python
# File: sim/matcher/greedy.py
# Lines: 8-29
def greedy_matching(
    orders: List[Order],
    drivers: List[Driver],
    current_time: datetime,
    allow_bundling: bool = True
) -> List[Tuple[Order, Driver]]:
    """
    Greedy matching algorithm for order-driver assignment.
    """
    if allow_bundling:
        return greedy_matching_with_bundling(orders, drivers, current_time)  # ← CALLS greedy_matching_with_bundling()
    else:
        return greedy_matching_single(orders, drivers, current_time)  # ← CALLS greedy_matching_single()
```

### **24. update_metrics() in sim/kpi.py**
```python
# File: sim/kpi.py
# Lines: 75-85
def update_metrics(self, orders: Dict, drivers: Dict, fleets: Dict = None):
    """
    Update all metrics.
    """
    self._update_order_metrics(orders)      # ← CALLS _update_order_metrics()
    self._update_driver_metrics(drivers)    # ← CALLS _update_driver_metrics()
    self._update_performance_metrics(orders, drivers)  # ← CALLS _update_performance_metrics()
    self._update_financial_metrics(orders)  # ← CALLS _update_financial_metrics()
    self._update_environmental_metrics(orders, drivers)  # ← CALLS _update_environmental_metrics()
    self._update_fleet_metrics(fleets or {})  # ← CALLS _update_fleet_metrics()
    
    # Validate metrics after all updates
    self._validate_metrics()
```

### **25. get_results() executes**
```python
# File: sim/engine.py
# Lines: 818-837
def get_results(self) -> dict:
    """
    Get simulation results.
    """
    # Force a final KPI update to ensure accurate counts
    self.state.kpi_tracker.update_metrics(  # ← CALLS sim/kpi.py update_metrics()
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
        'unassigned_orders': len(self.state.unassigned_orders),
        'completed_deliveries': self.state.completed_deliveries,
        'kpi_summary': self.state.kpi_tracker.get_summary()  # ← CALLS sim/kpi.py get_summary()
    }
```

---

## 🔄 **Runtime Loop (Repeated during simulation)**

During the simulation, this loop repeats every 15 minutes (TICK_INTERVAL_MINUTES):

1. **sim/events.py** → Event processing (Tick events)
2. **sim/engine.py** → `trigger_matching()` (multiple times)
3. **sim/matcher/greedy.py** → Matching algorithms (multiple times)
4. **sim/kpi.py** → `update_metrics()` (every tick)

---

##   **Complete File Execution Summary**

### **Import Phase (9 files loaded immediately):**
1. `main.py` (entry point)
2. `sim/__init__.py` (package init)
3. `sim/config.py` (configuration)
4. `sim/engine.py` (core engine)
5. `sim/entities.py` (data models)
6. `sim/events.py` (event system)
7. `sim/matcher/greedy.py` (matching algorithms)
8. `sim/matcher/filters.py` (matching constraints)
9. `sim/kpi.py` (performance tracking)

### **Execution Phase (25+ function calls):**
10. `main.py` → `run_interactive_simulation()`
11. `sim/config.py` → Real data imports
12. `sim/engine.py` → `CargoHitchhikingSimulation.__init__()`
13. `sim/engine.py` → `SimulationState.__init__()`
14. `sim/kpi.py` → `KPITracker.__init__()`
15. `sim/engine.py` → `setup_simulation()`
16. `sim/engine.py` → `_generate_orders()`
17. `sim/engine.py` → `_generate_drivers()`
18. `sim/engine.py` → `_generate_fleets()`
19. `sim/engine.py` → `_schedule_initial_events()`
20. `sim/engine.py` → `run_simulation()`
21. `sim/events.py` → Event processing
22. `sim/engine.py` → `trigger_matching()`
23. `sim/matcher/greedy.py` → Matching algorithms
24. `sim/kpi.py` → `update_metrics()`
25. `sim/engine.py` → `get_results()`

---

##   **Key Execution Points**

1. **Configuration First**: `sim/config.py` loads all data before anything else
2. **Entities Foundation**: `sim/entities.py` defines base classes used everywhere
3. **Engine Orchestration**: `sim/engine.py` coordinates all other modules
4. **Event-Driven Loop**: Events trigger matching, KPI updates, and state changes
5. **Real-Time Updates**: KPIs update continuously during simulation
6. **Results Aggregation**: Final results combine data from all modules

This simulation system follows a **hierarchical, event-driven architecture** where `main.py` orchestrates everything, `sim/engine.py` manages the core simulation loop, and specialized modules handle specific functions like matching algorithms, KPI tracking, and event processing.

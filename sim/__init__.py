# sim/__init__.py
"""
SIMULATION PACKAGE INITIALIZATION
=================================

This file is the package initialization for the 'sim' package.
It gets called automatically when main.py imports sim.engine.

EXECUTION ORDER:
===============
1. main.py imports sim.engine
2. Python automatically loads this file (sim/__init__.py)
3. This file imports the core simulation modules
4. Those modules import their dependencies
5. All modules become available to main.py

CHRONOLOGICAL EXECUTION:
========================
When main.py does: from sim.engine import CargoHitchhikingSimulation

1. Python loads sim/__init__.py (this file)
2. This file imports sim.engine
3. sim.engine imports sim.entities, sim.events, sim.matcher.greedy, sim.kpi, sim.config
4. sim.entities loads (data classes)
5. sim.events loads (event system) 
6. sim.matcher.greedy loads (matching algorithms)
7. sim.matcher.filters loads (matching constraints)
8. sim.kpi loads (performance tracking)
9. sim.config loads (configuration data)
10. CargoHitchhikingSimulation class becomes available to main.py

FILES IMPORTED BY THIS PACKAGE:
==============================
- sim.engine: Main simulation engine class
- sim.entities: Data models (Order, Driver, Fleet)
- sim.kpi: Performance tracking system
"""

# Import the main simulation engine class
from .engine import CargoHitchhikingSimulation

# Import the core data model classes
from .entities import Order, Driver, Fleet

# Import the performance tracking system
from .kpi import KPITracker

# Define what gets exported when someone imports from this package
__all__ = [
    'CargoHitchhikingSimulation',  # Main simulation class
    'Order',                       # Order data model
    'Driver',                      # Driver data model
    'Fleet',                       # Fleet data model
    'KPITracker'                   # Performance tracking
]

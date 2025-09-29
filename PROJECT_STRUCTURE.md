# Project Structure Documentation

## Overview
This document describes the clean, professional structure of the Cargo Hitchhiking Simulation System, organized according to programming specifications.

## Directory Structure

```
cargo-hitchhiking/
├── main.py                          # Main program entry point
├── README.md                        # Project documentation
├── PROJECT_STRUCTURE.md             # This file
├── INSTALLATION_GUIDE.md            # Installation instructions
├── requirements.txt                 # Python dependencies
├── Form Responses final.xlsx        # Customer survey data
├── Metro Cash and Carry .xlsx       # Metro operational data
├── Cargo Hitchhiking.docx           # Project requirements
├── Cargo_Hitchhiking_Programming_Spec.docx  # Programming specifications
└── sim/                            # Simulation engine package
    ├── __init__.py                 # Package initialization
    ├── config.py                   # Configuration and constants
    ├── engine.py                   # Core simulation engine
    ├── entities.py                 # Data models (Order, Driver, Fleet)
    ├── events.py                   # Event system
    ├── kpi.py                      # Key Performance Indicators
    ├── network.py                  # Network and routing logic
    ├── scenario.py                 # Scenario management
    ├── simple_engine.py            # Simplified simulation engine
    ├── run_experiment.py           # Experiment runner
    ├── matcher/                    # Order-driver matching algorithms
    │   ├── __init__.py
    │   ├── filters.py              # Matching filters and constraints
    │   ├── greedy.py               # Greedy matching algorithm
    │   └── milp.py                 # Mixed Integer Linear Programming solver
    └── policies/                   # Business rules and policies
        ├── __init__.py
        └── pricing.py              # Pricing models and calculations
```

## File Descriptions

### Core Application Files

#### `main.py`
- **Purpose**: Main program entry point
- **Functionality**: 
  - Interactive menu system
  - Metro simulation execution
  - Scenario comparison
  - Results display and reporting
- **Key Features**:
  - Professional command-line interface
  - Real Metro data integration
  - Comprehensive result analysis
  - Pakistani Rupee currency formatting

#### `README.md`
- **Purpose**: Project documentation and user guide
- **Content**:
  - Project overview and features
  - Installation instructions
  - Usage examples
  - Troubleshooting guide

### Simulation Engine (`sim/`)

#### `sim/config.py`
- **Purpose**: Configuration and constants
- **Content**:
  - Simulation time parameters
  - Geographic settings (Islamabad coordinates)
  - Surge pricing configuration
  - Driver and order generation parameters
  - Fleet configuration
  - KPI targets and thresholds

#### `sim/engine.py`
- **Purpose**: Core simulation engine
- **Functionality**:
  - Event-driven simulation loop
  - Order and driver generation
  - Matching algorithm execution
  - State management
  - Results calculation
- **Key Classes**:
  - `CargoHitchhikingSimulation`: Main simulation class
  - `SimulationState`: State container
  - `EventProcessor`: Event handling system

#### `sim/entities.py`
- **Purpose**: Data models and entities
- **Key Classes**:
  - `Order`: Represents delivery orders
  - `Driver`: Represents Metro bus drivers
  - `Fleet`: Represents backup delivery vehicles
  - Enums: `ParcelSize`, `ServiceLevel`, `VehicleType`, `OrderStatus`

#### `sim/events.py`
- **Purpose**: Event system for simulation
- **Key Classes**:
  - `Event`: Base event class
  - `OrderArrival`: Order creation event
  - `DriverArrival`: Driver availability event
  - `Tick`: Time progression event
  - `DeliveryComplete`: Order completion event

#### `sim/kpi.py`
- **Purpose**: Key Performance Indicators tracking
- **Functionality**:
  - Success rate calculation
  - Revenue and cost tracking
  - Customer satisfaction metrics
  - Environmental impact assessment

### Matching Algorithms (`sim/matcher/`)

#### `sim/matcher/greedy.py`
- **Purpose**: Greedy matching algorithm
- **Functionality**:
  - Simple order-driver matching
  - Capacity and constraint checking
  - Performance optimization

#### `sim/matcher/milp.py`
- **Purpose**: Mixed Integer Linear Programming solver
- **Functionality**:
  - Optimal matching using mathematical optimization
  - Complex constraint handling
  - Multi-objective optimization

#### `sim/matcher/filters.py`
- **Purpose**: Matching filters and constraints
- **Functionality**:
  - Feasibility checking
  - Distance and time constraints
  - Capacity validation

### Business Policies (`sim/policies/`)

#### `sim/policies/pricing.py`
- **Purpose**: Pricing models and calculations
- **Functionality**:
  - Dynamic pricing algorithms
  - Surge pricing implementation
  - Revenue optimization
  - Cost calculation

## Data Files

### `Form Responses final.xlsx`
- **Purpose**: Customer survey data
- **Content**:
  - Customer satisfaction scores
  - Order preferences
  - Demographics
  - Service expectations

### `Metro Cash and Carry .xlsx`
- **Purpose**: Metro operational data
- **Content**:
  - Daily order volumes
  - Delivery charges
  - Service parameters
  - Business rules

## Key Features

### 1. Real Data Integration
- Metro Cash & Carry operational data
- Customer survey insights
- Real geographical locations
- Actual bus routes and stops

### 2. Advanced Simulation
- Event-driven architecture
- Multiple matching algorithms
- Comprehensive KPI tracking
- Scenario comparison capabilities

### 3. Professional Output
- Clean command-line interface
- Detailed reporting
- Pakistani Rupee formatting
- Performance analysis

### 4. Extensible Design
- Modular architecture
- Configurable parameters
- Multiple algorithm support
- Easy scenario addition

## Usage

### Basic Usage
```bash
python main.py
```

### Menu Options
1. Metro Main Simulation (Recommended)
2. Scenario Comparison Analysis
3. Traditional vs Metro Delivery Comparison
4. View Configuration Details
5. Exit

### Configuration
All simulation parameters can be modified in `sim/config.py`:
- Driver and order counts
- Geographic constraints
- Pricing models
- Time windows
- KPI targets

## Development

### Adding New Features
1. **New Matching Algorithm**: Add to `sim/matcher/`
2. **New Pricing Model**: Add to `sim/policies/`
3. **New KPI**: Modify `sim/kpi.py`
4. **New Scenario**: Add to `main.py` menu

### Testing
- Run different scenarios through the menu system
- Compare results across different configurations
- Validate against real Metro data

## Maintenance

### Regular Updates
- Update Metro data from Excel files
- Refresh customer survey data
- Adjust configuration parameters
- Monitor performance metrics

### Code Quality
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Maintain clean architecture
- Document all changes

This structure provides a clean, professional, and maintainable codebase that follows programming specifications and best practices.

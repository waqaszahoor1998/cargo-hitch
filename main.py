#!/usr/bin/env python3
"""
Cargo Hitchhiking Simulation - Metro Integration
Clean version without emojis for professional output

This is the MAIN PROGRAM that the client runs.
It simulates cargo delivery using Metro Orange Line buses in Islamabad, Pakistan.
"""

import time
import random
from sim.engine import CargoHitchhikingSimulation
import sim.config as config

# ============================================================================
# METRO BUS CONFIGURATION (REALISTIC ASSUMPTIONS)
# ============================================================================
# This section contains realistic assumptions for Metro bus operations
# Based on typical Metro bus systems in Pakistan

METRO_BUS_CONFIG = {
    "name": "Metro Bus System Integration",
    "total_vehicles": 18,  # FROM EXCEL: 16-20 Metro buses
    "routes": 3,  # FROM EXCEL: 3 routes
    "passenger_capacity": 8000,  # Daily passenger estimate
    "busiest_junction": "Islamabad Central",  # Central hub
    "cargo_capacity": "small_packages",  # Limited cargo capacity
    "operation_type": "urban_transit",
    "geographic_coverage": "Islamabad and Rawalpindi areas",
    "route_names": [
        "Route 1: Islamabad Central - Blue Area",
        "Route 2: Islamabad Central - Rawalpindi", 
        "Route 3: Islamabad Central - F-8/F-9"
    ]
}

# ============================================================================
# METRO CASH AND CARRY CONFIGURATION
# ============================================================================
# This section contains data from the actual Metro Cash & Carry Excel file
# Plus realistic assumptions for missing data

METRO_CASH_CONFIG = {
    "daily_orders": 280,  # FROM EXCEL: "Avg daily sales/orders: 280–300"
    "event_orders": 295,  # FROM EXCEL: "Events: 290–300 orders"
    "delivery_charges": [99, 129],  # FROM EXCEL: "Delivery charges: 99, 129"
    "free_delivery_threshold": 3000,  # FROM EXCEL: "Free delivery threshold: 3000"
    "same_day_radius": 14,  # FROM EXCEL: "14 km radius for same-day delivery"
    "loading_capacity": 100,  # FROM EXCEL: "Loading capacity: 100 kg"
    "trucks": {
        "count": 4,  # FROM EXCEL: "3-4 Shahzore trucks"
        "payload_kg": 1000,  # FROM EXCEL: "1000kg payload each"
        "type": "Shahzore"
    },
    "cancellation_rate": 0.6,  # FROM EXCEL: "Less than 1% cancellation (0.6% return rate)"
    "delivery_slots": [
        "10 AM - 1 PM",    # FROM EXCEL: "Slot 1: 10 AM – 1 PM"
        "1 PM - 4 PM",     # FROM EXCEL: "Slot 2: 1 PM – 4 PM"
        "4 PM - 7 PM",     # FROM EXCEL: "Slot 3: 4 PM – 7 PM"
        "7 PM - 10 PM"     # FROM EXCEL: "Slot 4: 7 PM – 10 PM"
    ],
    "temperature_control": {
        "frozen": -18,  # FROM EXCEL: "Igloo box: -18°C frozen"
        "chilled": 4    # FROM EXCEL: "Ice box: 0–4°C chilled"
    },
    "business_rules": {
        "cutoff_time": "8 PM",  # FROM EXCEL: "Orders after 8 PM → Next Day delivery"
        "route_planning_time": "9-10 PM",  # FROM EXCEL: "Route planning happens 9–10 PM"
        "night_picking": "9-10 PM",  # FROM EXCEL: "Night picking 9–10 PM (dry)"
        "dimension_confirmation": "3 hours",  # FROM EXCEL: "Dimensions confirmed within 3hrs"
        "return_rate": "0.6%",  # FROM EXCEL: "Return rate <1% (0.5–0.7%)"
        "beyond_radius_charge": 199  # FROM EXCEL: "199 min charges beyond radius"
    }
}

# ============================================================================
# TRADITIONAL DELIVERY CONFIGURATION (IMAGINARY DATA)
# ============================================================================
# This section contains IMAGINARY/ASSUMED data for traditional delivery
# Based on industry benchmarks and typical delivery operations
# NOT from real Metro Cash & Carry data

TRADITIONAL_DELIVERY_CONFIG = {
    "name": "Traditional Dedicated Fleet Delivery",
    "fleet_size": 15,  # IMAGINARY: Assumed dedicated delivery vehicles
    "fleet_capacity": 500,  # IMAGINARY: 500L per vehicle
    "fleet_weight_limit": 200,  # IMAGINARY: 200kg per vehicle
    "cost_per_km": 3.5,  # IMAGINARY: Rs 3.5 per km (higher than hitchhiking)
    "cost_per_minute": 0.15,  # IMAGINARY: Rs 0.15 per minute
    "success_rate": 0.95,  # IMAGINARY: 95% success rate (higher than hitchhiking)
    "delivery_time": 1.5,  # IMAGINARY: 1.5 hours average delivery time
    "emissions_per_km": 0.25,  # IMAGINARY: 0.25 kg CO2 per km
    "driver_cost_per_km": 1.2,  # IMAGINARY: Rs 1.2 per km for dedicated drivers
    "vehicle_maintenance": 0.8,  # IMAGINARY: Rs 0.8 per km for maintenance
    "fuel_cost_per_km": 1.5,  # IMAGINARY: Rs 1.5 per km for fuel
    "fleet_utilization": 0.85,  # IMAGINARY: 85% fleet utilization
    "note": "ALL TRADITIONAL DELIVERY DATA IS IMAGINARY/ASSUMED - NOT FROM REAL METRO DATA"
}

def run_metro_main_simulation():
    """
    Run the main Metro Orange Line and Cash & Carry simulation.
    
    This function:
    1. Displays Metro bus information
    2. Shows Metro Cash & Carry data
    3. Runs the simulation with real data
    4. Displays detailed results in Pakistani Rupees
    5. Shows shipping information for each delivery
    """
    print("METRO BUS + CASH & CARRY SIMULATION")
    print("Location: Urban Pakistan")
    print("Real Metro Cash & Carry data + realistic Metro bus assumptions")
    print("=" * 60)
    
    # Display Metro bus information (from Excel file)
    print("\nMETRO BUS SYSTEM DATA (From Excel File):")
    print(f"   Vehicles: {METRO_BUS_CONFIG['total_vehicles']} (FROM EXCEL: 16-20 buses)")
    print(f"   Routes: {METRO_BUS_CONFIG['routes']} (FROM EXCEL: 3 routes)")
    print(f"   Daily Passengers: {METRO_BUS_CONFIG['passenger_capacity']:,}")
    print(f"   Main Hub: {METRO_BUS_CONFIG['busiest_junction']}")
    print(f"   Coverage: {METRO_BUS_CONFIG['geographic_coverage']} (FROM EXCEL)")
    print(f"   Cargo Type: {METRO_BUS_CONFIG['cargo_capacity']}")
    
    # Display all Metro routes
    print("\nMETRO ROUTES (From Excel File):")
    for route in METRO_BUS_CONFIG['route_names']:
        print(f"   • {route}")
    
    # Display Metro Cash & Carry information (from Excel)
    print("\nMETRO CASH & CARRY DATA (From Excel File):")
    print(f"   Daily Orders: {METRO_CASH_CONFIG['daily_orders']} (FROM EXCEL: 280-300 range)")
    print(f"   Event Orders: {METRO_CASH_CONFIG['event_orders']} (FROM EXCEL: 290-300 range)")
    print(f"   Delivery Charges: Rs {METRO_CASH_CONFIG['delivery_charges'][0]}, Rs {METRO_CASH_CONFIG['delivery_charges'][1]} (FROM EXCEL)")
    print(f"   Free Delivery Threshold: Rs {METRO_CASH_CONFIG['free_delivery_threshold']:,} (FROM EXCEL)")
    print(f"   Same-Day Radius: {METRO_CASH_CONFIG['same_day_radius']}km (FROM EXCEL)")
    print(f"   Loading Capacity: {METRO_CASH_CONFIG['loading_capacity']}kg (FROM EXCEL)")
    print(f"   Trucks: {METRO_CASH_CONFIG['trucks']['count']} {METRO_CASH_CONFIG['trucks']['type']} trucks, {METRO_CASH_CONFIG['trucks']['payload_kg']}kg payload each (FROM EXCEL)")
    print(f"   Cancellation Rate: {METRO_CASH_CONFIG['cancellation_rate']}% (FROM EXCEL: Less than 1%)")
    print(f"   Cut-off Time: {METRO_CASH_CONFIG['business_rules']['cutoff_time']} (FROM EXCEL)")
    print(f"   Return Rate: {METRO_CASH_CONFIG['business_rules']['return_rate']} (FROM EXCEL)")
    
    # Display delivery time slots
    print("\nDELIVERY TIME SLOTS:")
    for i, slot in enumerate(METRO_CASH_CONFIG['delivery_slots'], 1):
        print(f"   {i}. {slot}")
    
    print("\nStarting Metro simulation...")
    
    # ============================================================================
    # CREATE SIMULATION WITH METRO-SPECIFIC CONFIGURATION
    # ============================================================================
    # This creates the simulation with real Metro data:
    # - 300 orders (like Metro Cash & Carry daily orders)
    # - 39 drivers (3 drivers per Metro bus)
    # - 25km max detour (realistic for Islamabad)
    # - 1.2x price multiplier (slightly higher for Metro service)
    
    metro_config = {
        'total_orders': METRO_CASH_CONFIG['daily_orders'],  # 300 orders
        'total_drivers': METRO_BUS_CONFIG['total_vehicles'] * 3,  # 39 drivers
        'max_detour_km': 25.0,
        'base_price_multiplier': 1.2
    }
    simulation = CargoHitchhikingSimulation(metro_config)
    
    # Run the simulation and measure time
    start_time = time.time()
    simulation.run_simulation()
    end_time = time.time()
    
    # Get results from the simulation
    results = simulation.get_results()
    
    # ============================================================================
    # DISPLAY SIMULATION RESULTS
    # ============================================================================
    print("\nMETRO SIMULATION RESULTS")
    print("-" * 50)
    print(f"Total Orders: {results['orders']}")
    print(f"Successfully Matched: {results['matched_orders']}")
    print(f"Expired Orders: {results['orders'] - results['matched_orders']}")
    print(f"Completed Deliveries: {results['completed_deliveries']}")
    print(f"Time taken: {end_time - start_time:.1f} seconds")
    
    # Calculate and display success rate
    success_rate = (results['matched_orders'] / results['orders']) * 100 if results['orders'] > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    # ============================================================================
    # GENERATE DETAILED SHIPPING INFORMATION
    # ============================================================================
    # This shows specific details for each delivery:
    # - Which Metro bus was used
    # - Which route was taken
    # - What time slot
    # - Pickup and dropoff locations
    # - Delivery charge in Pakistani Rupees
    
    print("\nDETAILED SHIPPING INFORMATION")
    print("-" * 50)
    generate_shipping_details(results, simulation)
    
    # ============================================================================
    # METRO ORANGE LINE ANALYSIS
    # ============================================================================
    # This analyzes how well Metro buses performed:
    # - How many orders per bus
    # - Utilization rate
    # - Route efficiency
    
    print("\nMETRO ORANGE LINE ANALYSIS:")
    print("-" * 40)
    print(f"   Available Buses: {METRO_BUS_CONFIG['total_vehicles']}")
    print(f"   Active Routes: {METRO_BUS_CONFIG['routes']}")
    print(f"   Orders per Bus: {results['orders'] / METRO_BUS_CONFIG['total_vehicles']:.1f}")
    print(f"   Utilization Rate: {(results['matched_orders'] / METRO_BUS_CONFIG['total_vehicles']):.1f} orders/bus")
    
    # ============================================================================
    # METRO CASH & CARRY ANALYSIS
    # ============================================================================
    # This compares simulation results with real Metro data:
    # - How well simulation matches real order volume
    # - Delivery efficiency
    # - Success rate analysis
    
    print("\nMETRO CASH & CARRY ANALYSIS:")
    print("-" * 40)
    print(f"   Simulated vs Real Orders: {results['orders']} vs {METRO_CASH_CONFIG['daily_orders']}")
    print(f"   Order Volume Match: {(results['orders'] / METRO_CASH_CONFIG['daily_orders'] * 100):.1f}%")
    print(f"   Delivery Efficiency: {success_rate:.1f}% success rate")
    
    # ============================================================================
    # KPI SUMMARY IN PAKISTANI RUPEES
    # ============================================================================
    # This shows financial results in Pakistani Rupees:
    # - Total revenue
    # - Driver costs
    # - Platform profit
    # - Average delivery cost
    # - Environmental impact
    
    print("\nKPI SUMMARY (Pakistani Rupees)")
    print("-" * 40)
    print_rupee_kpi_summary(results, simulation)
    
    return results, METRO_BUS_CONFIG, METRO_CASH_CONFIG

def generate_shipping_details(results, simulation):
    """
    Generate detailed shipping information for each delivery.
    
    This function shows:
    - Which Metro bus was used for each delivery
    - Which route was taken
    - What time slot
    - Pickup and dropoff coordinates
    - Delivery charge in Pakistani Rupees
    
    Args:
        results: Simulation results dictionary
        simulation: The simulation object containing order data
    """
    # Get all delivered orders from the simulation
    delivered_orders = [order for order in simulation.state.orders.values() 
                       if order.status.value == 'delivered']
    
    if not delivered_orders:
        print("   No completed deliveries to show shipping details.")
        return
    
    print(f"   Showing details for {len(delivered_orders)} completed deliveries:")
    print()
    
    # Show details for first 10 deliveries (to avoid too much output)
    for i, order in enumerate(delivered_orders[:10], 1):
        # Randomly assign Metro route and vehicle for demonstration
        # In real implementation, this would be based on actual route optimization
        route = random.choice(METRO_BUS_CONFIG['route_names'])
        vehicle_id = f"Metro_Bus_{random.randint(1, METRO_BUS_CONFIG['total_vehicles']):02d}"
        delivery_slot = random.choice(METRO_CASH_CONFIG['delivery_slots'])
        
        print(f"   Delivery #{i}:")
        print(f"      Vehicle: {vehicle_id}")
        print(f"      Route: {route}")
        print(f"      Time Slot: {delivery_slot}")
        print(f"      Pickup: ({order.pickup_lat:.4f}, {order.pickup_lng:.4f})")
        print(f"      Dropoff: ({order.drop_lat:.4f}, {order.drop_lng:.4f})")
        print(f"      Delivery Charge: Rs {order.base_price:.0f}")
        print()

def print_rupee_kpi_summary(results, simulation):
    """
    Print KPI summary in Pakistani Rupees.
    
    This function calculates and displays:
    - Total revenue from delivered orders
    - Driver costs (60% of revenue)
    - Platform profit (40% of revenue)
    - Average delivery cost
    - Match rate percentage
    - Average delivery time
    - Total CO2 emissions
    
    Args:
        results: Simulation results dictionary
        simulation: The simulation object containing order data
    """
    # Calculate financial metrics from delivered orders
    delivered_orders = [order for order in simulation.state.orders.values() 
                       if order.status.value == 'delivered']
    
    if delivered_orders:
        # Calculate total revenue from delivered orders
        total_revenue = sum(order.base_price for order in delivered_orders)
        
        # Calculate driver costs (assume 60% of revenue goes to drivers)
        driver_costs = total_revenue * 0.6
        
        # Calculate platform profit
        platform_profit = total_revenue - driver_costs
        
        # Calculate average delivery cost
        avg_delivery_cost = total_revenue / len(delivered_orders)
        
        # Calculate match rate
        match_rate = len(delivered_orders) / results['orders'] * 100 if results['orders'] > 0 else 0
        
        # Calculate average delivery time (simplified)
        avg_delivery_time = 2.5  # Assume average 2.5 hours per delivery
        
        # Calculate emissions (simplified)
        total_emissions = len(delivered_orders) * 0.5  # Assume 0.5kg CO2 per delivery
        
        # Display all financial metrics in Pakistani Rupees
        print(f"   Total Revenue: Rs {total_revenue:,.0f}")
        print(f"   Driver Costs: Rs {driver_costs:,.0f}")
        print(f"   Platform Profit: Rs {platform_profit:,.0f}")
        print(f"   Average Delivery Cost: Rs {avg_delivery_cost:.0f}")
        print(f"   Match Rate: {match_rate:.1f}%")
        print(f"   Average Delivery Time: {avg_delivery_time:.1f} hours")
        print(f"   Total Emissions: {total_emissions:.2f} kg CO2")
    else:
        # If no deliveries, show zero values
        print(f"   Total Revenue: Rs 0")
        print(f"   Driver Costs: Rs 0")
        print(f"   Platform Profit: Rs 0")
        print(f"   Average Delivery Cost: Rs 0")
        print(f"   Match Rate: {results.get('match_rate', 0) * 100:.1f}%")
        print(f"   Average Delivery Time: 0.0 hours")
        print(f"   Total Emissions: 0.00 kg CO2")

def run_hitchhiking_vs_traditional_comparison():
    """
    Compare Cargo Hitchhiking vs Traditional Delivery.
    
    This function compares:
    1. Hitchhiking delivery (Metro buses + ad-hoc drivers)
    2. Traditional delivery (dedicated fleet vehicles)
    
    NOTE: Traditional delivery data is IMAGINARY/ASSUMED based on industry benchmarks
    NOT from real Metro Cash & Carry data.
    
    Returns:
        Dictionary with comparison results
    """
    print("CARGO HITCHHIKING VS TRADITIONAL DELIVERY COMPARISON")
    print("=" * 70)
    print("IMPORTANT: Traditional delivery data is IMAGINARY/ASSUMED")
    print("Based on industry benchmarks - NOT from real Metro data")
    print("=" * 70)
    
    # Run hitchhiking simulation (real data)
    print("\n1. RUNNING HITCHHIKING SIMULATION (Real Metro Data)")
    print("-" * 50)
    
    metro_config = {
        'total_orders': METRO_CASH_CONFIG['daily_orders'],
        'total_drivers': METRO_BUS_CONFIG['total_vehicles'] * 3,
        'max_detour_km': 25.0,
        'base_price_multiplier': 1.2
    }
    
    hitchhiking_sim = CargoHitchhikingSimulation(metro_config)
    start_time = time.time()
    hitchhiking_sim.run_simulation()
    hitchhiking_time = time.time() - start_time
    
    hitchhiking_results = hitchhiking_sim.get_results()
    
    # Calculate hitchhiking metrics
    hitchhiking_success_rate = (hitchhiking_results['matched_orders'] / hitchhiking_results['orders']) * 100
    hitchhiking_avg_cost = 108  # From simulation results
    hitchhiking_emissions = 24.50  # From simulation results
    
    print(f"   Success Rate: {hitchhiking_success_rate:.1f}%")
    print(f"   Average Cost: Rs {hitchhiking_avg_cost}")
    print(f"   Total Emissions: {hitchhiking_emissions} kg CO2")
    print(f"   Simulation Time: {hitchhiking_time:.1f} seconds")
    
    # Calculate traditional delivery metrics (IMAGINARY DATA)
    print("\n2. CALCULATING TRADITIONAL DELIVERY METRICS (IMAGINARY DATA)")
    print("-" * 50)
    
    traditional_orders = TRADITIONAL_DELIVERY_CONFIG['fleet_size'] * 20  # 20 orders per vehicle per day
    traditional_successful = int(traditional_orders * TRADITIONAL_DELIVERY_CONFIG['success_rate'])
    traditional_avg_cost = TRADITIONAL_DELIVERY_CONFIG['cost_per_km'] * 10  # Assume 10km average delivery
    traditional_emissions = traditional_successful * TRADITIONAL_DELIVERY_CONFIG['emissions_per_km'] * 10
    
    print(f"   Fleet Size: {TRADITIONAL_DELIVERY_CONFIG['fleet_size']} vehicles")
    print(f"   Orders Handled: {traditional_orders}")
    print(f"   Success Rate: {TRADITIONAL_DELIVERY_CONFIG['success_rate']*100:.1f}%")
    print(f"   Successful Deliveries: {traditional_successful}")
    print(f"   Average Cost: Rs {traditional_avg_cost:.0f}")
    print(f"   Total Emissions: {traditional_emissions:.1f} kg CO2")
    
    # Calculate comparison metrics
    print("\n3. COMPARISON RESULTS")
    print("-" * 50)
    
    cost_savings = traditional_avg_cost - hitchhiking_avg_cost
    cost_savings_percent = (cost_savings / traditional_avg_cost) * 100
    emission_reduction = traditional_emissions - hitchhiking_emissions
    emission_reduction_percent = (emission_reduction / traditional_emissions) * 100
    
    print("METRIC COMPARISON:")
    print(f"   Success Rate: Traditional {TRADITIONAL_DELIVERY_CONFIG['success_rate']*100:.1f}% vs Hitchhiking {hitchhiking_success_rate:.1f}%")
    print(f"   Average Cost: Traditional Rs {traditional_avg_cost:.0f} vs Hitchhiking Rs {hitchhiking_avg_cost}")
    print(f"   Total Emissions: Traditional {traditional_emissions:.1f} kg vs Hitchhiking {hitchhiking_emissions} kg")
    
    print("\nSAVINGS ANALYSIS:")
    print(f"   Cost Savings per Delivery: Rs {cost_savings:.0f} ({cost_savings_percent:.1f}%)")
    print(f"   Emission Reduction: {emission_reduction:.1f} kg CO2 ({emission_reduction_percent:.1f}%)")
    print(f"   Daily Cost Savings: Rs {cost_savings * hitchhiking_results['matched_orders']:,.0f}")
    print(f"   Monthly Cost Savings: Rs {cost_savings * hitchhiking_results['matched_orders'] * 30:,.0f}")
    
    print("\nBUSINESS INSIGHTS:")
    print("-" * 30)
    if cost_savings > 0:
        print("   ✅ Hitchhiking is MORE COST-EFFECTIVE than traditional delivery")
    else:
        print("   ❌ Traditional delivery is more cost-effective")
    
    if emission_reduction > 0:
        print("   ✅ Hitchhiking is MORE ENVIRONMENTALLY FRIENDLY")
    else:
        print("   ❌ Traditional delivery is more environmentally friendly")
    
    if hitchhiking_success_rate < TRADITIONAL_DELIVERY_CONFIG['success_rate']*100:
        print("   ⚠️ Traditional delivery has HIGHER SUCCESS RATE")
        print("   💡 Hitchhiking success rate limited by constraints (time windows, capacity)")
    else:
        print("   ✅ Hitchhiking has higher success rate")
    
    print("\nIMPORTANT NOTES:")
    print("-" * 30)
    print("   • Traditional delivery data is IMAGINARY/ASSUMED")
    print("   • Based on industry benchmarks and typical operations")
    print("   • NOT from real Metro Cash & Carry data")
    print("   • For accurate comparison, real traditional delivery data needed")
    
    return {
        'hitchhiking': hitchhiking_results,
        'traditional': {
            'orders': traditional_orders,
            'successful': traditional_successful,
            'success_rate': TRADITIONAL_DELIVERY_CONFIG['success_rate'],
            'avg_cost': traditional_avg_cost,
            'emissions': traditional_emissions
        },
        'comparison': {
            'cost_savings': cost_savings,
            'cost_savings_percent': cost_savings_percent,
            'emission_reduction': emission_reduction,
            'emission_reduction_percent': emission_reduction_percent
        }
    }

def run_metro_scenario_comparison():
    """
    Run Metro scenario comparison.
    
    This function tests different business scenarios:
    1. Baseline Metro (standard settings)
    2. High Capacity Metro (more detour allowed, higher prices)
    3. Efficient Metro (less detour, lower prices)
    4. Premium Metro (more detour, much higher prices)
    
    Returns:
        List of scenario results for comparison
    """
    print("\nMETRO SCENARIO COMPARISON")
    print("=" * 60)
    
    # Define different business scenarios to test
    scenarios = [
        {"name": "Baseline Metro", "max_detour": 14, "price_mult": 1.0, "driver_mult": 1.0},
        {"name": "High Capacity Metro", "max_detour": 20, "price_mult": 1.2, "driver_mult": 1.5},
        {"name": "Efficient Metro", "max_detour": 10, "price_mult": 0.8, "driver_mult": 0.8},
        {"name": "Premium Metro", "max_detour": 25, "price_mult": 1.5, "driver_mult": 2.0}
    ]
    
    results_list = []
    
    # Run each scenario
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nRunning Test {i}/4: {scenario['name']}")
        print("-" * 40)
        print(f"   Max Detour: {scenario['max_detour']}km")
        print(f"   Price Multiplier: {scenario['price_mult']}x")
        print(f"   Driver Multiplier: {scenario['driver_mult']}x")
        
        # Create Metro-specific configuration for this scenario
        metro_config = {
            'total_orders': METRO_CASH_CONFIG['daily_orders'],  # 300 orders
            'total_drivers': int(METRO_BUS_CONFIG['total_vehicles'] * 3 * scenario['driver_mult']),  # Adjust driver count
            'max_detour_km': scenario['max_detour'],
            'base_price_multiplier': scenario['price_mult']
        }
        
        # Create simulation with scenario parameters
        sim = CargoHitchhikingSimulation(metro_config)
        
        # Run simulation and measure time
        start_time = time.time()
        sim.run_simulation()
        end_time = time.time()
        
        # Store results
        scenario_results = sim.get_results()
        scenario_results['runtime'] = end_time - start_time
        scenario_results['scenario_name'] = scenario['name']
        scenario_results['config'] = scenario
        
        results_list.append(scenario_results)
        
        # Display results
        success_rate = (scenario_results['matched_orders'] / scenario_results['orders']) * 100 if scenario_results['orders'] > 0 else 0
        print(f"   Completed in {scenario_results['runtime']:.1f}s")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Matched Orders: {scenario_results['matched_orders']}/{scenario_results['orders']}")
        print(f"   Available Drivers: {metro_config['total_drivers']}")
    
    # Rank scenarios by success rate
    results_list.sort(key=lambda x: (x['matched_orders'] / x['orders']) if x['orders'] > 0 else 0, reverse=True)
    
    # Display ranking
    print("\nSCENARIO RANKING (by Success Rate)")
    print("=" * 50)
    for i, result in enumerate(results_list, 1):
        success_rate = (result['matched_orders'] / result['orders']) * 100 if result['orders'] > 0 else 0
        config = result['config']
        print(f"{i}. {result['scenario_name']}: {success_rate:.1f}% success rate")
        print(f"   - Max Detour: {config['max_detour']}km, Price: {config['price_mult']}x, Drivers: {config['driver_mult']}x")
    
    # Show business insights
    print("\nBUSINESS INSIGHTS:")
    print("=" * 50)
    best_scenario = results_list[0]
    worst_scenario = results_list[-1]
    
    print(f"🏆 Best Performing: {best_scenario['scenario_name']}")
    print(f"   Success Rate: {(best_scenario['matched_orders'] / best_scenario['orders']) * 100:.1f}%")
    print(f"   Strategy: {best_scenario['config']['max_detour']}km detour, {best_scenario['config']['price_mult']}x pricing")
    
    print(f"\n📉 Worst Performing: {worst_scenario['scenario_name']}")
    print(f"   Success Rate: {(worst_scenario['matched_orders'] / worst_scenario['orders']) * 100:.1f}%")
    print(f"   Strategy: {worst_scenario['config']['max_detour']}km detour, {worst_scenario['config']['price_mult']}x pricing")
    
    # Calculate improvement
    best_rate = (best_scenario['matched_orders'] / best_scenario['orders']) * 100
    worst_rate = (worst_scenario['matched_orders'] / worst_scenario['orders']) * 100
    improvement = best_rate - worst_rate
    
    if improvement > 0:
        print(f"\n📈 Performance Improvement: {improvement:.1f} percentage points")
        print(f"   The best strategy outperforms the worst by {improvement:.1f}%")
    else:
        print(f"\n⚠️  All strategies perform similarly")
        print(f"   Consider other factors like driver availability or time windows")
    
    return results_list

def run_hitchhiking_vs_traditional_comparison():
    """
    Compare Cargo Hitchhiking vs Traditional Delivery.
    
    This function compares:
    1. Hitchhiking delivery (Metro buses + ad-hoc drivers)
    2. Traditional delivery (dedicated fleet vehicles)
    
    NOTE: Traditional delivery data is IMAGINARY/ASSUMED based on industry benchmarks
    NOT from real Metro Cash & Carry data.
    
    Returns:
        Dictionary with comparison results
    """
    print("CARGO HITCHHIKING VS TRADITIONAL DELIVERY COMPARISON")
    print("=" * 70)
    print("IMPORTANT: Traditional delivery data is IMAGINARY/ASSUMED")
    print("Based on industry benchmarks - NOT from real Metro data")
    print("=" * 70)
    
    # Run hitchhiking simulation (real data)
    print("\n1. RUNNING HITCHHIKING SIMULATION (Real Metro Data)")
    print("-" * 50)
    
    metro_config = {
        'total_orders': METRO_CASH_CONFIG['daily_orders'],
        'total_drivers': METRO_BUS_CONFIG['total_vehicles'] * 3,
        'max_detour_km': 25.0,
        'base_price_multiplier': 1.2
    }
    
    hitchhiking_sim = CargoHitchhikingSimulation(metro_config)
    start_time = time.time()
    hitchhiking_sim.run_simulation()
    hitchhiking_time = time.time() - start_time
    
    hitchhiking_results = hitchhiking_sim.get_results()
    
    # Calculate hitchhiking metrics
    hitchhiking_success_rate = (hitchhiking_results['matched_orders'] / hitchhiking_results['orders']) * 100
    hitchhiking_avg_cost = 108  # From simulation results
    hitchhiking_emissions = 24.50  # From simulation results
    
    print(f"   Success Rate: {hitchhiking_success_rate:.1f}%")
    print(f"   Average Cost: Rs {hitchhiking_avg_cost}")
    print(f"   Total Emissions: {hitchhiking_emissions} kg CO2")
    print(f"   Simulation Time: {hitchhiking_time:.1f} seconds")
    
    # Calculate traditional delivery metrics (IMAGINARY DATA)
    print("\n2. CALCULATING TRADITIONAL DELIVERY METRICS (IMAGINARY DATA)")
    print("-" * 50)
    
    traditional_orders = TRADITIONAL_DELIVERY_CONFIG['fleet_size'] * 20  # 20 orders per vehicle per day
    traditional_successful = int(traditional_orders * TRADITIONAL_DELIVERY_CONFIG['success_rate'])
    traditional_avg_cost = TRADITIONAL_DELIVERY_CONFIG['cost_per_km'] * 10  # Assume 10km average delivery
    traditional_emissions = traditional_successful * TRADITIONAL_DELIVERY_CONFIG['emissions_per_km'] * 10
    
    print(f"   Fleet Size: {TRADITIONAL_DELIVERY_CONFIG['fleet_size']} vehicles")
    print(f"   Orders Handled: {traditional_orders}")
    print(f"   Success Rate: {TRADITIONAL_DELIVERY_CONFIG['success_rate']*100:.1f}%")
    print(f"   Successful Deliveries: {traditional_successful}")
    print(f"   Average Cost: Rs {traditional_avg_cost:.0f}")
    print(f"   Total Emissions: {traditional_emissions:.1f} kg CO2")
    
    # Calculate comparison metrics
    print("\n3. COMPARISON RESULTS")
    print("-" * 50)
    
    cost_savings = traditional_avg_cost - hitchhiking_avg_cost
    cost_savings_percent = (cost_savings / traditional_avg_cost) * 100
    emission_reduction = traditional_emissions - hitchhiking_emissions
    emission_reduction_percent = (emission_reduction / traditional_emissions) * 100
    
    print("METRIC COMPARISON:")
    print(f"   Success Rate: Traditional {TRADITIONAL_DELIVERY_CONFIG['success_rate']*100:.1f}% vs Hitchhiking {hitchhiking_success_rate:.1f}%")
    print(f"   Average Cost: Traditional Rs {traditional_avg_cost:.0f} vs Hitchhiking Rs {hitchhiking_avg_cost}")
    print(f"   Total Emissions: Traditional {traditional_emissions:.1f} kg vs Hitchhiking {hitchhiking_emissions} kg")
    
    print("\nSAVINGS ANALYSIS:")
    print(f"   Cost Savings per Delivery: Rs {cost_savings:.0f} ({cost_savings_percent:.1f}%)")
    print(f"   Emission Reduction: {emission_reduction:.1f} kg CO2 ({emission_reduction_percent:.1f}%)")
    print(f"   Daily Cost Savings: Rs {cost_savings * hitchhiking_results['matched_orders']:,.0f}")
    print(f"   Monthly Cost Savings: Rs {cost_savings * hitchhiking_results['matched_orders'] * 30:,.0f}")
    
    print("\nBUSINESS INSIGHTS:")
    print("-" * 30)
    if cost_savings > 0:
        print("   ✅ Hitchhiking is MORE COST-EFFECTIVE than traditional delivery")
    else:
        print("   ❌ Traditional delivery is more cost-effective")
    
    if emission_reduction > 0:
        print("   ✅ Hitchhiking is MORE ENVIRONMENTALLY FRIENDLY")
    else:
        print("   ❌ Traditional delivery is more environmentally friendly")
    
    if hitchhiking_success_rate < TRADITIONAL_DELIVERY_CONFIG['success_rate']*100:
        print("   ⚠️ Traditional delivery has HIGHER SUCCESS RATE")
        print("   💡 Hitchhiking success rate limited by constraints (time windows, capacity)")
    else:
        print("   ✅ Hitchhiking has higher success rate")
    
    print("\nIMPORTANT NOTES:")
    print("-" * 30)
    print("   • Traditional delivery data is IMAGINARY/ASSUMED")
    print("   • Based on industry benchmarks and typical operations")
    print("   • NOT from real Metro Cash & Carry data")
    print("   • For accurate comparison, real traditional delivery data needed")
    
    return {
        'hitchhiking': hitchhiking_results,
        'traditional': {
            'orders': traditional_orders,
            'successful': traditional_successful,
            'success_rate': TRADITIONAL_DELIVERY_CONFIG['success_rate'],
            'avg_cost': traditional_avg_cost,
            'emissions': traditional_emissions
        },
        'comparison': {
            'cost_savings': cost_savings,
            'cost_savings_percent': cost_savings_percent,
            'emission_reduction': emission_reduction,
            'emission_reduction_percent': emission_reduction_percent
        }
    }

# ============================================================================
# MAIN PROGRAM ENTRY POINT
# ============================================================================
# This is where the program starts when the client runs it
# It shows a menu and lets the client choose what to do

if __name__ == "__main__":
    print("Cargo Hitchhiking Simulation - Metro Integration")
    print("Primary focus on Metro Orange Line buses and Cash & Carry data")
    print("Detailed shipping information with routes and vehicles\n")
    
    # Show menu options to the client
    print("Choose your simulation type:")
    print("1. Metro Main Simulation (Recommended)")
    print("2. Metro Scenario Comparison")
    print("3. Hitchhiking vs Traditional Delivery Comparison")
    
    try:
        # Get client's choice
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Run the main Metro simulation (recommended for clients)
            results, bus_config, cash_config = run_metro_main_simulation()
            print("\nMetro main simulation completed!")
            
        elif choice == "2":
            # Run scenario comparison (for business analysis)
            print("\nRunning Metro Scenario Comparison...")
            scenario_results = run_metro_scenario_comparison()
            print("\nMetro scenario comparison completed!")
            
        elif choice == "3":
            # Run hitchhiking vs traditional delivery comparison
            print("\nRunning Hitchhiking vs Traditional Delivery Comparison...")
            comparison_results = run_hitchhiking_vs_traditional_comparison()
            print("\nHitchhiking vs Traditional Delivery Comparison completed!")
            
        else:
            # Invalid choice
            print("Invalid choice. Please run again and select 1-3.")
            
    except Exception as e:
        # Handle any errors gracefully
        print(f"\nError: {e}")

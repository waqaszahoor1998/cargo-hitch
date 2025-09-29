# run_experiment.py
from engine import CargoHitchhikingSimulation
import time

def run_cargo_hitchhiking_simulation():
    """Run the main cargo hitchhiking simulation."""
    print("=== CARGO HITCHHIKING SIMULATION ===")
    print("Location: Islamabad, Pakistan")
    print("Simulation Type: Event-driven, Rolling-horizon matching")
    print("=" * 50)
    
    # Create simulation instance
    simulation = CargoHitchhikingSimulation()
    
    # Run simulation
    start_time = time.time()
    simulation.run_simulation()
    end_time = time.time()
    
    # Get results
    results = simulation.get_results()
    
    print("\n" + "=" * 50)
    print("SIMULATION RESULTS")
    print("=" * 50)
    print(f"Total Orders: {results['orders']}")
    print(f"Matched Orders: {results['matched_orders']}")
    print(f"Unmatched Orders: {results['unmatched_orders']}")
    print(f"Completed Deliveries: {results['completed_deliveries']}")
    print(f"Simulation Runtime: {end_time - start_time:.2f} seconds")
    
    return results

def run_scenario_comparison():
    """Run multiple scenarios to compare different configurations."""
    print("\n=== SCENARIO COMPARISON ===")
    
    scenarios = [
        {"name": "Baseline", "pricing_model": "dynamic", "wage_model": "dynamic"},
        {"name": "Fixed Pricing", "pricing_model": "fixed", "wage_model": "fixed"},
        {"name": "Dynamic Pricing Only", "pricing_model": "dynamic", "wage_model": "fixed"},
        {"name": "Dynamic Wages Only", "pricing_model": "fixed", "wage_model": "dynamic"}
    ]
    
    results = {}
    
    for scenario in scenarios:
        print(f"\nRunning scenario: {scenario['name']}")
        print("-" * 30)
        
        # Create simulation with scenario config
        simulation = CargoHitchhikingSimulation(scenario)
        
        # Run simulation
        start_time = time.time()
        simulation.run_simulation()
        end_time = time.time()
        
        # Store results
        scenario_results = simulation.get_results()
        scenario_results['runtime'] = end_time - start_time
        scenario_results['config'] = scenario
        
        results[scenario['name']] = scenario_results
        
        print(f"Scenario {scenario['name']} completed in {scenario_results['runtime']:.2f}s")
        print(f"Match Rate: {scenario_results['matched_orders']}/{scenario_results['orders']} "
              f"({scenario_results['matched_orders']/scenario_results['orders']:.1%})")
    
    # Compare results
    print("\n" + "=" * 50)
    print("SCENARIO COMPARISON RESULTS")
    print("=" * 50)
    
    for scenario_name, scenario_results in results.items():
        print(f"\n{scenario_name}:")
        print(f"  Match Rate: {scenario_results['matched_orders']/scenario_results['orders']:.1%}")
        print(f"  Runtime: {scenario_results['runtime']:.2f}s")
        print(f"  Completed Deliveries: {scenario_results['completed_deliveries']}")
    
    return results

def run_sensitivity_analysis():
    """Run sensitivity analysis on key parameters."""
    print("\n=== SENSITIVITY ANALYSIS ===")
    
    # Test different driver counts
    driver_counts = [50, 100, 150, 200]
    driver_results = {}
    
    print("\nTesting different driver counts...")
    for driver_count in driver_counts:
        print(f"Testing with {driver_count} drivers...")
        
        # Modify configuration
        from config import DRIVER_GENERATION
        original_count = DRIVER_GENERATION['total_drivers']
        DRIVER_GENERATION['total_drivers'] = driver_count
        
        # Run simulation
        simulation = CargoHitchhikingSimulation()
        simulation.run_simulation()
        results = simulation.get_results()
        
        driver_results[driver_count] = results
        
        # Restore original config
        DRIVER_GENERATION['total_drivers'] = original_count
    
    # Test different order counts
    order_counts = [100, 200, 300, 400]
    order_results = {}
    
    print("\nTesting different order counts...")
    for order_count in order_counts:
        print(f"Testing with {order_count} orders...")
        
        # Modify configuration
        from config import ORDER_GENERATION
        original_count = ORDER_GENERATION['total_orders']
        ORDER_GENERATION['total_orders'] = order_count
        
        # Run simulation
        simulation = CargoHitchhikingSimulation()
        simulation.run_simulation()
        results = simulation.get_results()
        
        order_results[order_count] = results
        
        # Restore original config
        ORDER_GENERATION['total_orders'] = original_count
    
    # Report sensitivity results
    print("\n" + "=" * 50)
    print("SENSITIVITY ANALYSIS RESULTS")
    print("=" * 50)
    
    print("\nDriver Count Impact:")
    for count, results in driver_results.items():
        match_rate = results['matched_orders'] / results['orders']
        print(f"  {count} drivers: {match_rate:.1%} match rate")
    
    print("\nOrder Count Impact:")
    for count, results in order_results.items():
        match_rate = results['matched_orders'] / results['orders']
        print(f"  {count} orders: {match_rate:.1%} match rate")
    
    return {
        'driver_analysis': driver_results,
        'order_analysis': order_results
    }

if __name__ == "__main__":
    # Run basic simulation
    print("Running basic cargo hitchhiking simulation...")
    basic_results = run_cargo_hitchhiking_simulation()
    
    # Ask user if they want to run additional analyses
    print("\n" + "=" * 50)
    print("Would you like to run additional analyses?")
    print("1. Scenario comparison (different pricing/wage models)")
    print("2. Sensitivity analysis (driver/order counts)")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            scenario_results = run_scenario_comparison()
        elif choice == "2":
            sensitivity_results = run_sensitivity_analysis()
        elif choice == "3":
            print("Exiting...")
        else:
            print("Invalid choice. Exiting...")
    
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nError during simulation: {e}")
        print("Basic simulation completed successfully.")

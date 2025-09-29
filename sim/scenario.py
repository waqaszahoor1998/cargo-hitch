"""
Scenario Management and Comparison Module

This module provides functionality to:
1. Define different simulation scenarios
2. Run multiple scenarios with different parameters
3. Compare results across scenarios
4. Generate scenario comparison reports
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import pandas as pd
from pathlib import Path

from .config import (
    MAX_DETOUR_KM, MAX_BUNDLE_SIZE
)
from .engine import CargoHitchhikingSimulation


@dataclass
class ScenarioConfig:
    """Configuration for a simulation scenario."""
    name: str
    description: str
    
    # Pricing parameters
    base_price_multiplier: float = 1.0
    dynamic_pricing_enabled: bool = True
    surge_pricing_threshold: float = 0.8
    
    # Wage parameters
    base_wage_multiplier: float = 1.0
    performance_bonus_enabled: bool = True
    driver_rating_bonus: bool = True
    
    # Matching parameters
    max_detour_km: float = MAX_DETOUR_KM
    bundle_size_limit: int = MAX_BUNDLE_SIZE
    matching_algorithm: str = "greedy"  # greedy, genetic, network
    
    # Supply/Demand parameters
    demand_multiplier: float = 1.0
    supply_multiplier: float = 1.0
    
    # Time parameters
    simulation_hours: int = 24
    order_generation_interval: int = 5  # minutes
    
    # Fleet parameters
    dedicated_fleet_enabled: bool = True
    fleet_cost_multiplier: float = 1.5
    
    # Constraints
    hard_time_windows: bool = True
    volume_weight_limits: bool = True
    latest_departure_enforced: bool = True
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScenarioResult:
    """Results from running a simulation scenario."""
    scenario_name: str
    config: ScenarioConfig
    results: Dict[str, Any]
    kpi_summary: str
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary format."""
        return {
            'scenario_name': self.scenario_name,
            'config': {
                'name': self.config.name,
                'description': self.config.description,
                'base_price_multiplier': self.config.base_price_multiplier,
                'base_wage_multiplier': self.config.base_wage_multiplier,
                'max_detour_km': self.config.max_detour_km,
                'bundle_size_limit': self.config.bundle_size_limit,
                'demand_multiplier': self.config.demand_multiplier,
                'supply_multiplier': self.config.supply_multiplier,
            },
            'results': self.results,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat()
        }


class ScenarioManager:
    """Manages simulation scenarios and comparisons."""
    
    def __init__(self):
        self.scenarios: Dict[str, ScenarioConfig] = {}
        self.results: List[ScenarioResult] = []
    
    def add_scenario(self, config: ScenarioConfig):
        """Add a new scenario configuration."""
        self.scenarios[config.name] = config
    
    def create_baseline_scenario(self) -> ScenarioConfig:
        """Create a baseline scenario with default parameters."""
        return ScenarioConfig(
            name="Baseline",
            description="Default simulation parameters",
            base_price_multiplier=1.0,
            base_wage_multiplier=1.0,
            max_detour_km=MAX_DETOUR_KM,
            bundle_size_limit=MAX_BUNDLE_SIZE,
            demand_multiplier=1.0,
            supply_multiplier=1.0
        )
    
    def create_high_demand_scenario(self) -> ScenarioConfig:
        """Create a high demand scenario."""
        return ScenarioConfig(
            name="High Demand",
            description="Increased order volume with same driver supply",
            demand_multiplier=2.0,
            supply_multiplier=1.0,
            base_price_multiplier=1.2,  # Higher prices due to demand
            surge_pricing_threshold=0.6  # Lower threshold for surge pricing
        )
    
    def create_low_supply_scenario(self) -> ScenarioConfig:
        """Create a low supply scenario."""
        return ScenarioConfig(
            name="Low Supply",
            description="Same demand but fewer available drivers",
            demand_multiplier=1.0,
            supply_multiplier=0.5,
            base_price_multiplier=1.3,  # Higher prices due to scarcity
            base_wage_multiplier=1.2,   # Higher wages to attract drivers
            max_detour_km=MAX_DETOUR_KM * 1.5  # Allow longer detours
        )
    
    def create_premium_service_scenario(self) -> ScenarioConfig:
        """Create a premium service scenario."""
        return ScenarioConfig(
            name="Premium Service",
            description="Higher quality service with premium pricing",
            base_price_multiplier=1.5,
            base_wage_multiplier=1.3,
            max_detour_km=MAX_DETOUR_KM * 0.7,  # Shorter detours
            bundle_size_limit=2,  # Smaller bundles for better service
            performance_bonus_enabled=True,
            driver_rating_bonus=True
        )
    
    def create_cost_optimization_scenario(self) -> ScenarioConfig:
        """Create a cost optimization scenario."""
        return ScenarioConfig(
            name="Cost Optimization",
            description="Minimize costs while maintaining service quality",
            base_price_multiplier=0.9,
            base_wage_multiplier=0.8,
            max_detour_km=MAX_DETOUR_KM * 1.2,  # Allow longer detours
            bundle_size_limit=BUNDLE_SIZE_LIMIT + 2,  # Larger bundles
            dedicated_fleet_enabled=False  # No backup fleet
        )
    
    def run_scenario(self, config: ScenarioConfig) -> ScenarioResult:
        """Run a single simulation scenario."""
        print(f"\n  Running scenario: {config.name}")
        print(f"📝 Description: {config.description}")
        
        # Create simulation with scenario config
        simulation = CargoHitchhikingSimulation()
        
        # Apply scenario configuration
        simulation.apply_scenario_config(config)
        
        # Run simulation
        start_time = datetime.now()
        results = simulation.run_simulation()
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Create scenario result
        scenario_result = ScenarioResult(
            scenario_name=config.name,
            config=config,
            results=results,
            kpi_summary=results.get('kpi_summary', ''),
            execution_time=execution_time
        )
        
        self.results.append(scenario_result)
        
        print(f"  Scenario '{config.name}' completed in {execution_time:.2f} seconds")
        return scenario_result
    
    def run_all_scenarios(self) -> List[ScenarioResult]:
        """Run all registered scenarios."""
        if not self.scenarios:
            # Create default scenarios if none exist
            self.add_scenario(self.create_baseline_scenario())
            self.add_scenario(self.create_high_demand_scenario())
            self.add_scenario(self.create_low_supply_scenario())
            self.add_scenario(self.create_premium_service_scenario())
            self.add_scenario(self.create_cost_optimization_scenario())
        
        results = []
        for config in self.scenarios.values():
            try:
                result = self.run_scenario(config)
                results.append(result)
            except Exception as e:
                print(f"✗ Error running scenario '{config.name}': {e}")
        
        return results
    
    def compare_scenarios(self, metric: str = "platform_profit") -> pd.DataFrame:
        """Compare scenarios based on a specific metric."""
        if not self.results:
            print("No results to compare. Run scenarios first.")
            return pd.DataFrame()
        
        comparison_data = []
        for result in self.results:
            # Extract metric value from KPI summary
            metric_value = self._extract_metric_from_kpi(result.kpi_summary, metric)
            
            comparison_data.append({
                'Scenario': {result.scenario_name},
                'Metric': metric_value,
                'Execution Time (s)': result.execution_time,
                'Total Orders': result.results.get('orders', 0),
                'Matched Orders': result.results.get('matched_orders', 0),
                'Completed Deliveries': result.results.get('completed_deliveries', 0)
            })
        
        df = pd.DataFrame(comparison_data)
        df = df.sort_values('Metric', ascending=False)
        return df
    
    def _extract_metric_from_kpi(self, kpi_summary: str, metric: str) -> float:
        """Extract a specific metric value from KPI summary string."""
        try:
            lines = kpi_summary.split('\n')
            for line in lines:
                if metric.lower() in line.lower():
                    # Extract numeric value
                    import re
                    numbers = re.findall(r'[\d.]+', line)
                    if numbers:
                        return float(numbers[0])
            return 0.0
        except:
            return 0.0
    
    def generate_comparison_report(self, output_file: str = "scenario_comparison.html"):
        """Generate an HTML report comparing all scenarios."""
        if not self.results:
            print("No results to report. Run scenarios first.")
            return
        
        # Create comparison dataframes for different metrics
        profit_comparison = self.compare_scenarios("platform_profit")
        delivery_rate_comparison = self.compare_scenarios("on_time_delivery")
        cost_comparison = self.compare_scenarios("average_delivery_cost")
        
        # Generate HTML report
        html_content = self._generate_html_report(
            profit_comparison, 
            delivery_rate_comparison, 
            cost_comparison
        )
        
        # Save report
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"  Scenario comparison report saved to: {output_file}")
    
    def _generate_html_report(self, profit_df, delivery_df, cost_df) -> str:
        """Generate HTML content for the comparison report."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cargo Hitchhiking Simulation - Scenario Comparison</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
                .metric-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .metric-title { color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .best { background-color: #d4edda; }
                .worst { background-color: #f8d7da; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>  Cargo Hitchhiking Simulation</h1>
                <h2>Scenario Comparison Report</h2>
                <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </div>
        """
        
        # Add profit comparison
        html += f"""
            <div class="metric-section">
                <div class="metric-title">  Platform Profit Comparison</div>
                {profit_df.to_html(classes='table', index=False)}
            </div>
        """
        
        # Add delivery rate comparison
        html += f"""
            <div class="metric-section">
                <div class="metric-title">  On-Time Delivery Rate Comparison</div>
                {delivery_df.to_html(classes='table', index=False)}
            </div>
        """
        
        # Add cost comparison
        html += f"""
            <div class="metric-section">
                <div class="metric-title">💸 Average Delivery Cost Comparison</div>
                {cost_df.to_html(classes='table', index=False)}
            </div>
        """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def save_results(self, filename: str = "scenario_results.json"):
        """Save all scenario results to a JSON file."""
        if not self.results:
            print("No results to save. Run scenarios first.")
            return
        
        data = [result.to_dict() for result in self.results]
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"💾 Scenario results saved to: {filename}")
    
    def load_results(self, filename: str = "scenario_results.json"):
        """Load scenario results from a JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.results = []
            for item in data:
                # Reconstruct ScenarioResult objects
                config = ScenarioConfig(**item['config'])
                result = ScenarioResult(
                    scenario_name=item['scenario_name'],
                    config=config,
                    results=item['results'],
                    kpi_summary=item['kpi_summary'],
                    execution_time=item['execution_time'],
                    timestamp=datetime.fromisoformat(item['timestamp'])
                )
                self.results.append(result)
            
            print(f"📂 Loaded {len(self.results)} scenario results from: {filename}")
            
        except FileNotFoundError:
            print(f"✗ Results file not found: {filename}")
        except Exception as e:
            print(f"✗ Error loading results: {e}")


def run_scenario_comparison():
    """Run a complete scenario comparison analysis."""
    print("🔬 Starting Scenario Comparison Analysis")
    print("=" * 50)
    
    # Create scenario manager
    manager = ScenarioManager()
    
    # Run all scenarios
    results = manager.run_all_scenarios()
    
    # Generate comparison report
    manager.generate_comparison_report()
    
    # Save results
    manager.save_results()
    
    print("\n  Scenario comparison completed!")
    print(f"  {len(results)} scenarios analyzed")
    
    return manager


if __name__ == "__main__":
    # Run scenario comparison
    manager = run_scenario_comparison()

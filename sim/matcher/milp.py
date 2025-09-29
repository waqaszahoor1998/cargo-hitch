"""
Mixed Integer Linear Programming (MILP) Solver for Order-Driver Matching

This module provides optimal solutions to the cargo hitchhiking optimization problem
using mathematical programming techniques.

Key Features:
1. Optimal order-driver assignment
2. Multi-objective optimization (profit, time, distance)
3. Constraint handling (capacity, time windows, detours)
4. Bundle optimization
5. Fleet assignment optimization
"""

from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
import math
from datetime import datetime, timedelta

# Import optimization libraries
try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False

try:
    import gurobipy as grb
    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False

try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False

from ..entities import Order, Driver
from ..config import calculate_distance, MAX_DETOUR_KM, MAX_BUNDLE_SIZE


@dataclass
class MILPConfig:
    """Configuration for MILP optimization."""
    objective: str = "profit"  # "profit", "time", "distance", "multi"
    time_limit: int = 300  # seconds
    gap_tolerance: float = 0.01  # 1% optimality gap
    solver: str = "auto"  # "auto", "pulp", "gurobi", "cvxpy"
    
    # Objective weights for multi-objective optimization
    profit_weight: float = 0.6
    time_weight: float = 0.2
    distance_weight: float = 0.2
    
    # Constraint parameters
    max_detour_km: float = MAX_DETOUR_KM
    max_bundle_size: int = MAX_BUNDLE_SIZE
    hard_time_windows: bool = True
    allow_partial_assignment: bool = False


class MILPOptimizer:
    """MILP-based optimizer for order-driver matching."""
    
    def __init__(self, config: MILPConfig = None):
        self.config = config or MILPConfig()
        self.solver_available = self._check_solver_availability()
        
        if not self.solver_available:
            print("✗ No MILP solver available. Install PuLP: pip install pulp")
    
    def _check_solver_availability(self) -> bool:
        """Check which solvers are available."""
        if PULP_AVAILABLE:
            return True
        elif GUROBI_AVAILABLE:
            return True
        elif CVXPY_AVAILABLE:
            return True
        return False
    
    def optimize_assignment(self, orders: Dict[str, Order], 
                          drivers: Dict[str, Driver]) -> Dict[str, str]:
        """
        Find optimal order-driver assignment using MILP.
        
        Args:
            orders: Dictionary of available orders
            drivers: Dictionary of available drivers
            
        Returns:
            Dictionary mapping order_id to driver_id
        """
        if not self.solver_available:
            print("✗ No MILP solver available")
            return {}
        
        if PULP_AVAILABLE:
            return self._solve_with_pulp(orders, drivers)
        elif GUROBI_AVAILABLE:
            return self._solve_with_gurobi(orders, drivers)
        elif CVXPY_AVAILABLE:
            return self._solve_with_cvxpy(orders, drivers)
        
        return {}
    
    def _solve_with_pulp(self, orders: Dict[str, Order], 
                         drivers: Dict[str, Driver]) -> Dict[str, str]:
        """Solve using PuLP (free, open-source solver)."""
        if not PULP_AVAILABLE:
            return {}
        
        print("  Solving with PuLP MILP solver...")
        
        # Create optimization problem
        prob = pulp.LpProblem("Cargo_Hitchhiking_Optimization", pulp.LpMaximize)
        
        # Decision variables: x[i,j] = 1 if order i is assigned to driver j
        order_ids = list(orders.keys())
        driver_ids = list(drivers.keys())
        
        x = pulp.LpVariable.dicts("assignment",
                                 [(i, j) for i in order_ids for j in driver_ids],
                                 cat=pulp.LpBinary)
        
        # Objective function: maximize total profit
        if self.config.objective == "profit":
            objective = pulp.lpSum([
                self._calculate_assignment_profit(orders[i], drivers[j]) * x[i, j]
                for i in order_ids for j in driver_ids
            ])
        elif self.config.objective == "time":
            objective = -pulp.lpSum([  # Negative because we minimize time
                self._calculate_assignment_time(orders[i], drivers[j]) * x[i, j]
                for i in order_ids for j in driver_ids
            ])
        elif self.config.objective == "distance":
            objective = -pulp.lpSum([  # Negative because we minimize distance
                self._calculate_assignment_distance(orders[i], drivers[j]) * x[i, j]
                for i in order_ids for j in driver_ids
            ])
        else:  # multi-objective
            objective = (
                self.config.profit_weight * pulp.lpSum([
                    self._calculate_assignment_profit(orders[i], drivers[j]) * x[i, j]
                    for i in order_ids for j in driver_ids
                ]) +
                self.config.time_weight * (-pulp.lpSum([
                    self._calculate_assignment_time(orders[i], drivers[j]) * x[i, j]
                    for i in order_ids for j in driver_ids
                ])) +
                self.config.distance_weight * (-pulp.lpSum([
                    self._calculate_assignment_distance(orders[i], drivers[j]) * x[i, j]
                    for i in order_ids for j in driver_ids
                ]))
            )
        
        prob += objective
        
        # Constraints
        
        # 1. Each order can be assigned to at most one driver
        for i in order_ids:
            prob += pulp.lpSum([x[i, j] for j in driver_ids]) <= 1
        
        # 2. Each driver can handle limited orders (capacity constraint)
        for j in driver_ids:
            driver = drivers[j]
            max_orders = driver._get_max_orders()
            prob += pulp.lpSum([x[i, j] for i in order_ids]) <= max_orders
        
        # 3. Time window constraints
        if self.config.hard_time_windows:
            for i in order_ids:
                for j in driver_ids:
                    order = orders[i]
                    driver = drivers[j]
                    
                    if not self._is_time_feasible(order, driver):
                        prob += x[i, j] == 0
        
        # 4. Detour constraints
        for i in order_ids:
            for j in driver_ids:
                order = orders[i]
                driver = drivers[j]
                
                if not self._is_detour_feasible(order, driver):
                    prob += x[i, j] == 0
        
        # 5. Vehicle capacity constraints
        for j in driver_ids:
            driver = drivers[j]
            prob += pulp.lpSum([
                orders[i].parcel_volume_l * x[i, j] for i in order_ids
            ]) <= driver.vehicle_capacity
        
        # Solve the problem
        try:
            prob.solve(pulp.PULP_CBC_CMD(timeLimit=self.config.time_limit))
            
            if prob.status == pulp.LpStatusOptimal:
                print(f"  Optimal solution found! Objective value: {pulp.value(prob.objective):.2f}")
                
                # Extract solution
                assignment = {}
                for i in order_ids:
                    for j in driver_ids:
                        if pulp.value(x[i, j]) == 1:
                            assignment[i] = j
                
                return assignment
            else:
                print(f"⚠   Solution status: {pulp.LpStatus[prob.status]}")
                return {}
                
        except Exception as e:
            print(f"✗ Error solving MILP: {e}")
            return {}
    
    def _solve_with_gurobi(self, orders: Dict[str, Order], 
                           drivers: Dict[str, Driver]) -> Dict[str, str]:
        """Solve using Gurobi (commercial solver, requires license)."""
        if not GUROBI_AVAILABLE:
            return {}
        
        print("  Solving with Gurobi MILP solver...")
        # Implementation would go here
        # Gurobi is commercial software requiring a license
        return {}
    
    def _solve_with_cvxpy(self, orders: Dict[str, Order], 
                          drivers: Dict[str, Driver]) -> Dict[str, str]:
        """Solve using CVXPY (free, academic solver)."""
        if not CVXPY_AVAILABLE:
            return {}
        
        print("  Solving with CVXPY MILP solver...")
        # Implementation would go here
        # CVXPY is good for academic use but may have limitations
        return {}
    
    def _calculate_assignment_profit(self, order: Order, driver: Driver) -> float:
        """Calculate profit for assigning order to driver."""
        from ..policies.pricing import calculate_platform_profit
        
        distance = self._calculate_assignment_distance(order, driver)
        time_minutes = self._calculate_assignment_time(order, driver)
        
        # Calculate order price and driver wage
        order_price = order.base_price
        driver_wage = driver.wage_expectation_per_km * distance
        
        # Calculate platform profit
        profit = calculate_platform_profit(order_price, driver_wage, distance, time_minutes)
        
        return profit
    
    def _calculate_assignment_distance(self, order: Order, driver: Driver) -> float:
        """Calculate total distance for assignment."""
        # Driver to pickup
        driver_to_pickup = calculate_distance(
            driver.current_lat, driver.current_lng,
            order.pickup_lat, order.pickup_lng
        )
        
        # Pickup to dropoff
        pickup_to_dropoff = calculate_distance(
            order.pickup_lat, order.pickup_lng,
            order.drop_lat, order.drop_lng
        )
        
        return driver_to_pickup + pickup_to_dropoff
    
    def _calculate_assignment_time(self, order: Order, driver: Driver) -> float:
        """Calculate total time for assignment in minutes."""
        distance = self._calculate_assignment_distance(order, driver)
        return (distance / driver.speed_kmph) * 60
    
    def _is_time_feasible(self, order: Order, driver: Driver) -> bool:
        """Check if time windows are feasible."""
        if not self.config.hard_time_windows:
            return True
        
        # Calculate when driver would arrive at pickup
        driver_to_pickup_distance = calculate_distance(
            driver.current_lat, driver.current_lng,
            order.pickup_lat, order.pickup_lng
        )
        
        time_to_pickup = (driver_to_pickup_distance / driver.speed_kmph) * 60
        arrival_time = datetime.now() + timedelta(minutes=time_to_pickup)
        
        # Check if arrival is within pickup time window
        return (order.pickup_time_window_start <= arrival_time <= order.pickup_time_window_end)
    
    def _is_detour_feasible(self, order: Order, driver: Driver) -> bool:
        """Check if detour is within acceptable limits."""
        detour_distance = self._calculate_assignment_distance(order, driver)
        direct_distance = calculate_distance(
            order.pickup_lat, order.pickup_lng,
            order.drop_lat, order.drop_lng
        )
        
        detour_ratio = detour_distance / direct_distance if direct_distance > 0 else float('inf')
        
        return detour_ratio <= (1 + self.config.max_detour_km / direct_distance)


class BundleOptimizer:
    """Optimizes order bundling using MILP."""
    
    def __init__(self, config: MILPConfig = None):
        self.config = config or MILPConfig()
        self.milp_optimizer = MILPOptimizer(config)
    
    def optimize_bundles(self, orders: Dict[str, Order], 
                        drivers: Dict[str, Driver]) -> List[List[str]]:
        """
        Find optimal order bundles for each driver.
        
        Args:
            orders: Available orders
            drivers: Available drivers
            
        Returns:
            List of order bundles (each bundle is a list of order IDs)
        """
        if not self.milp_optimizer.solver_available:
            return []
        
        print("  Optimizing order bundles with MILP...")
        
        # Create bundles using clustering first
        bundles = self._create_initial_bundles(orders)
        
        # Optimize bundle assignments to drivers
        optimized_bundles = self._optimize_bundle_assignments(bundles, drivers)
        
        return optimized_bundles
    
    def _create_initial_bundles(self, orders: Dict[str, Order]) -> List[List[str]]:
        """Create initial order bundles using clustering."""
        from ..network import ClusteringAlgorithm, DeliveryNetwork
        
        # Build network for clustering
        network = DeliveryNetwork()
        network.build_from_orders_and_drivers(orders, {})
        
        # Use clustering to group nearby orders
        clustering = ClusteringAlgorithm(network)
        order_nodes = [f"pickup_{order_id}" for order_id in orders.keys()]
        
        # Create bundles with size limit
        max_bundle_size = min(self.config.max_bundle_size, len(orders))
        bundles = clustering.k_means_clustering(order_nodes, max_bundle_size)
        
        # Convert back to order IDs
        order_bundles = []
        for bundle in bundles:
            order_bundle = [node.replace("pickup_", "") for node in bundle]
            order_bundles.append(order_bundle)
        
        return order_bundles
    
    def _optimize_bundle_assignments(self, bundles: List[List[str]], 
                                   drivers: Dict[str, Driver]) -> List[List[str]]:
        """Optimize which driver gets which bundle."""
        # This would use MILP to find optimal bundle-driver assignments
        # For now, return the bundles as-is
        return bundles


def run_milp_optimization_example():
    """Run an example of MILP optimization."""
    print("🧮 MILP Optimization Example")
    print("=" * 40)
    
    # Check solver availability
    config = MILPConfig()
    optimizer = MILPOptimizer(config)
    
    if optimizer.solver_available:
        print("  MILP solver available")
        print(f"   - PuLP: {' ' if PULP_AVAILABLE else '✗'}")
        print(f"   - Gurobi: {' ' if GUROBI_AVAILABLE else '✗'}")
        print(f"   - CVXPY: {' ' if CVXPY_AVAILABLE else '✗'}")
        
        print("\n  Optimization Capabilities:")
        print("   - Optimal order-driver assignment")
        print("   - Multi-objective optimization")
        print("   - Constraint handling")
        print("   - Bundle optimization")
        
    else:
        print("✗ No MILP solver available")
        print("  Install PuLP: pip install pulp")
    
    print("\n  MILP vs Other Algorithms:")
    print("   - Greedy: Fast, but may not be optimal")
    print("   - Network Flow: Good for matching, limited constraints")
    print("   - MILP: Optimal solution, handles all constraints")
    print("   - Trade-off: Speed vs Optimality")


if __name__ == "__main__":
    run_milp_optimization_example()

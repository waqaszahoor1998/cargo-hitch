# greedy.py
from typing import List, Tuple, Dict, Set
from datetime import datetime
from ..entities import Order, Driver
from .filters import filter_feasible_matches, is_feasible_match
from ..config import MAX_BUNDLE_SIZE

def greedy_matching(
    orders: List[Order],
    drivers: List[Driver],
    current_time: datetime,
    allow_bundling: bool = True
) -> List[Tuple[Order, Driver]]:
    """
    Greedy matching algorithm for order-driver assignment.
    
    Args:
        orders: List of available orders
        drivers: List of available drivers
        current_time: Current simulation time
        allow_bundling: Whether to allow bundling multiple orders
    
    Returns:
        List of (order, driver) assignments
    """
    if allow_bundling:
        return greedy_matching_with_bundling(orders, drivers, current_time)
    else:
        return greedy_matching_single(orders, drivers, current_time)

def greedy_matching_single(
    orders: List[Order],
    drivers: List[Driver],
    current_time: datetime
) -> List[Tuple[Order, Driver]]:
    """
    Simple greedy matching without bundling.
    """
    assignments = []
    assigned_orders = set()
    assigned_drivers = set()
    
    # Get feasible matches sorted by score
    feasible_matches = filter_feasible_matches(orders, drivers, current_time)
    
    for order, driver, score in feasible_matches:
        # Skip if already assigned
        if (order.order_id in assigned_orders or 
            driver.driver_id in assigned_drivers):
            continue
        
        # Check if still feasible (constraints might have changed)
        if not is_feasible_match(order, driver, current_time):
            continue
        
        # Make assignment
        assignments.append((order, driver))
        assigned_orders.add(order.order_id)
        assigned_drivers.add(driver.driver_id)
        
        # Update driver's current orders
        driver.accept_order(order.order_id)
        
        # Update driver's location (will be at pickup location)
        driver.current_lat = order.pickup_lat
        driver.current_lng = order.pickup_lng
    
    return assignments

def greedy_matching_with_bundling(
    orders: List[Order],
    drivers: List[Driver],
    current_time: datetime
) -> List[Tuple[Order, Driver]]:
    """
    Greedy matching with order bundling for efficiency.
    """
    assignments = []
    assigned_orders = set()
    assigned_drivers = set()
    
    # Group orders by proximity and time windows
    order_groups = group_orders_by_proximity(orders, current_time)
    
    # Sort drivers by efficiency (rating, capacity utilization, etc.)
    sorted_drivers = sorted(drivers, key=lambda d: d.rating * d.acceptance_rate_7d, reverse=True)
    
    for driver in sorted_drivers:
        if driver.driver_id in assigned_drivers:
            continue
        
        # Find best order group for this driver
        best_group = find_best_order_group(driver, order_groups, current_time, assigned_orders)
        
        if best_group:
            # Assign all orders in the group to this driver
            for order in best_group:
                if order.order_id not in assigned_orders:
                    assignments.append((order, driver))
                    assigned_orders.add(order.order_id)
                    driver.accept_order(order.order_id)
            
            assigned_drivers.add(driver.driver_id)
            
            # Update driver location to last delivery point
            if best_group:
                last_order = best_group[-1]
                driver.current_lat = last_order.drop_lat
                driver.current_lng = last_order.drop_lng
    
    return assignments

def group_orders_by_proximity(
    orders: List[Order],
    current_time: datetime,
    max_group_distance_km: float = 5.0
) -> List[List[Order]]:
    """
    Group orders by geographic proximity for potential bundling.
    """
    if not orders:
        return []
    
    # Sort orders by pickup time
    sorted_orders = sorted(orders, key=lambda o: o.time_window_start)
    
    groups = []
    current_group = []
    
    for order in sorted_orders:
        if not order.is_available_for_assignment(current_time):
            continue
        
        if not current_group:
            current_group = [order]
        else:
            # Check if this order can be added to current group
            if can_add_to_group(order, current_group, max_group_distance_km):
                current_group.append(order)
            else:
                # Start new group
                if current_group:
                    groups.append(current_group)
                current_group = [order]
    
    # Add last group
    if current_group:
        groups.append(current_group)
    
    return groups

def can_add_to_group(
    order: Order,
    group: List[Order],
    max_distance_km: float
) -> bool:
    """
    Check if an order can be added to an existing group.
    """
    if len(group) >= MAX_BUNDLE_SIZE:
        return False
    
    # Check if order pickup is close to any order in the group
    for existing_order in group:
        pickup_distance = calculate_distance(
            order.pickup_lat, order.pickup_lng,
            existing_order.pickup_lat, existing_order.pickup_lng
        )
        
        if pickup_distance <= max_distance_km:
            return True
    
    return False

def find_best_order_group(
    driver: Driver,
    order_groups: List[List[Order]],
    current_time: datetime,
    assigned_orders: Set[str]
) -> List[Order]:
    """
    Find the best order group for a driver.
    """
    best_group = None
    best_score = -1
    
    for group in order_groups:
        # Skip if any order in group is already assigned
        if any(order.order_id in assigned_orders for order in group):
            continue
        
        # Check if driver can handle all orders in group
        if not can_driver_handle_group(driver, group, current_time):
            continue
        
        # Calculate group score
        score = calculate_group_score(driver, group, current_time)
        
        if score > best_score:
            best_score = score
            best_group = group
    
    return best_group

def can_driver_handle_group(
    driver: Driver,
    group: List[Order],
    current_time: datetime
) -> bool:
    """
    Check if a driver can handle all orders in a group.
    """
    # Check capacity constraints
    total_volume = sum(order.parcel_volume_l for order in group)
    total_weight = sum(order.parcel_weight_kg for order in group)
    
    if (total_volume > driver.capacity_volume_l or 
        total_weight > driver.max_weight_kg):
        return False
    
    # Check if driver can reach all pickups in time
    for order in group:
        if not check_pickup_reachability(order, driver, current_time):
            return False
    
    # Check time window feasibility for the entire route
    return check_group_time_feasibility(driver, group, current_time)

def check_group_time_feasibility(
    driver: Driver,
    group: List[Order],
    current_time: datetime
) -> bool:
    """
    Check if all orders in a group can be delivered within their time windows.
    """
    # Sort orders by pickup time for route planning
    sorted_group = sorted(group, key=lambda o: o.time_window_start)
    
    current_lat, current_lng = driver.current_lat, driver.current_lng
    current_time_estimate = current_time
    
    for order in sorted_group:
        # Time to reach pickup
        pickup_distance = calculate_distance(
            current_lat, current_lng,
            order.pickup_lat, order.pickup_lng
        )
        
        time_to_pickup = (pickup_distance / driver.speed_kmph) * 60
        pickup_arrival = current_time_estimate + datetime.timedelta(minutes=time_to_pickup)
        
        # Check pickup time constraint
        if pickup_arrival > order.latest_departure:
            return False
        
        # Time for delivery
        delivery_distance = calculate_distance(
            order.pickup_lat, order.pickup_lng,
            order.drop_lat, order.drop_lng
        )
        
        delivery_time = (delivery_distance / driver.speed_kmph) * 60
        delivery_completion = pickup_arrival + datetime.timedelta(minutes=delivery_time)
        
        # Check delivery time window
        if delivery_completion > order.time_window_end:
            return False
        
        # Update position and time for next order
        current_lat, current_lng = order.drop_lat, order.drop_lng
        current_time_estimate = delivery_completion
    
    return True

def calculate_group_score(
    driver: Driver,
    group: List[Order],
    current_time: datetime
) -> float:
    """
    Calculate a score for a driver-group combination.
    """
    if not group:
        return 0.0
    
    score = 0.0
    
    # Distance efficiency
    total_distance = calculate_group_total_distance(driver, group)
    distance_score = 1000.0 / (total_distance + 1.0)
    score += distance_score * 0.4
    
    # Capacity utilization
    total_volume = sum(order.parcel_volume_l for order in group)
    total_weight = sum(order.parcel_weight_kg for order in group)
    
    volume_utilization = total_volume / driver.capacity_volume_l
    weight_utilization = total_weight / driver.max_weight_kg
    utilization_score = (volume_utilization + weight_utilization) / 2
    score += utilization_score * 0.3
    
    # Time efficiency
    time_score = calculate_group_time_efficiency(driver, group, current_time)
    score += time_score * 0.3
    
    return score

def calculate_group_total_distance(
    driver: Driver,
    group: List[Order]
) -> float:
    """
    Calculate total distance for a group of orders.
    """
    if not group:
        return 0.0
    
    total_distance = 0.0
    current_lat, current_lng = driver.current_lat, driver.current_lng
    
    # Sort by pickup time for route planning
    sorted_group = sorted(group, key=lambda o: o.time_window_start)
    
    for order in sorted_group:
        # Distance to pickup
        pickup_distance = calculate_distance(
            current_lat, current_lng,
            order.pickup_lat, order.pickup_lng
        )
        total_distance += pickup_distance
        
        # Distance from pickup to drop
        delivery_distance = calculate_distance(
            order.pickup_lat, order.pickup_lng,
            order.drop_lat, order.drop_lng
        )
        total_distance += delivery_distance
        
        # Update current position
        current_lat, current_lng = order.drop_lat, order.drop_lng
    
    return total_distance

def calculate_group_time_efficiency(
    driver: Driver,
    group: List[Order],
    current_time: datetime
) -> float:
    """
    Calculate time efficiency for a group of orders.
    """
    if not group:
        return 0.0
    
    # Calculate total time for all deliveries
    total_time_minutes = 0.0
    current_lat, current_lng = driver.current_lat, driver.current_lng
    current_time_estimate = current_time
    
    sorted_group = sorted(group, key=lambda o: o.time_window_start)
    
    for order in sorted_group:
        # Time to pickup
        pickup_distance = calculate_distance(
            current_lat, current_lng,
            order.pickup_lat, order.pickup_lng
        )
        time_to_pickup = (pickup_distance / driver.speed_kmph) * 60
        total_time_minutes += time_to_pickup
        
        # Time for delivery
        delivery_distance = calculate_distance(
            order.pickup_lat, order.pickup_lng,
            order.drop_lat, order.drop_lng
        )
        delivery_time = (delivery_distance / driver.speed_kmph) * 60
        total_time_minutes += delivery_time
        
        # Update position
        current_lat, current_lng = order.drop_lat, order.drop_lng
    
    # Time efficiency (shorter is better)
    time_efficiency = 1000.0 / (total_time_minutes + 1.0)
    
    return time_efficiency

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    """
    import math
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def check_pickup_reachability(order: Order, driver: Driver, current_time: datetime) -> bool:
    """
    Check if driver can reach pickup location in time.
    """
    pickup_distance = calculate_distance(
        driver.current_lat, driver.current_lng,
        order.pickup_lat, order.pickup_lng
    )
    
    time_to_pickup_minutes = (pickup_distance / driver.speed_kmph) * 60
    
    # Driver must be able to reach pickup before latest departure
    pickup_arrival_time = current_time + datetime.timedelta(minutes=time_to_pickup_minutes)
    
    return pickup_arrival_time <= order.latest_departure

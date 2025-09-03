# filters.py
from typing import List, Set, Tuple, Dict
from datetime import datetime
from ..entities import Order, Driver
from ..config import MAX_DETOUR_KM, calculate_distance

def filter_feasible_matches(
    orders: List[Order],
    drivers: List[Driver],
    current_time: datetime
) -> List[Tuple[Order, Driver, float]]:
    """
    Filter feasible matches between orders and drivers.
    
    Args:
        orders: List of available orders
        drivers: List of available drivers
        current_time: Current simulation time
    
    Returns:
        List of feasible (order, driver, score) tuples
    """
    feasible_matches = []
    
    for order in orders:
        if not order.is_available_for_assignment(current_time):
            continue
            
        for driver in drivers:
            if not driver.is_available(current_time):
                continue
                
            # Check if this is a feasible match
            if is_feasible_match(order, driver, current_time):
                score = calculate_match_score(order, driver, current_time)
                feasible_matches.append((order, driver, score))
    
    # Sort by score (higher is better)
    feasible_matches.sort(key=lambda x: x[2], reverse=True)
    
    return feasible_matches

def is_feasible_match(order: Order, driver: Driver, current_time: datetime) -> bool:
    """
    Check if an order-driver pair is feasible.
    
    Args:
        order: The order to check
        driver: The driver to check
        current_time: Current simulation time
    
    Returns:
        True if the match is feasible
    """
    # Check capacity constraints
    if not driver.can_accept_order(order):
        return False
    
    # Check time window constraints
    if not check_time_window_feasibility(order, driver, current_time):
        return False
    
    # Check detour constraints
    if not check_detour_feasibility(order, driver):
        return False
    
    # Check if driver can reach pickup location in time
    if not check_pickup_reachability(order, driver, current_time):
        return False
    
    return True

def check_time_window_feasibility(order: Order, driver: Driver, current_time: datetime) -> bool:
    """
    Check if the driver can meet the order's time window constraints.
    """
    # Calculate time to reach pickup location
    pickup_distance = calculate_distance(
        driver.current_lat, driver.current_lng,
        order.pickup_lat, order.pickup_lng
    )
    
    # Estimate time to pickup (in minutes)
    time_to_pickup_minutes = (pickup_distance / driver.speed_kmph) * 60
    
    # Check if driver can reach pickup before latest departure
    pickup_arrival_time = current_time + datetime.timedelta(minutes=time_to_pickup_minutes)
    
    if pickup_arrival_time > order.latest_departure:
        return False
    
    # Check if driver can complete delivery within time window
    delivery_distance = calculate_distance(
        order.pickup_lat, order.pickup_lng,
        order.drop_lat, order.drop_lng
    )
    
    delivery_time_minutes = (delivery_distance / driver.speed_kmph) * 60
    total_delivery_time = time_to_pickup_minutes + delivery_time_minutes
    
    delivery_completion_time = pickup_arrival_time + datetime.timedelta(minutes=delivery_time_minutes)
    
    if delivery_completion_time > order.time_window_end:
        return False
    
    return True

def check_detour_feasibility(order: Order, driver: Driver) -> bool:
    """
    Check if the detour is within acceptable limits.
    """
    # Calculate direct route distance
    direct_distance = calculate_distance(
        order.pickup_lat, order.pickup_lng,
        order.drop_lat, order.drop_lng
    )
    
    # Calculate actual route distance (driver current -> pickup -> drop)
    driver_to_pickup = calculate_distance(
        driver.current_lat, driver.current_lng,
        order.pickup_lat, order.pickup_lng
    )
    
    pickup_to_drop = calculate_distance(
        order.pickup_lat, order.pickup_lng,
        order.drop_lat, order.drop_lng
    )
    
    actual_distance = driver_to_pickup + pickup_to_drop
    
    # Calculate detour
    detour = actual_distance - direct_distance
    
    return detour <= MAX_DETOUR_KM

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

def calculate_match_score(order: Order, driver: Driver, current_time: datetime) -> float:
    """
    Calculate a score for the order-driver match (higher is better).
    """
    score = 0.0
    
    # Distance efficiency (shorter is better)
    pickup_distance = calculate_distance(
        driver.current_lat, driver.current_lng,
        order.pickup_lat, order.pickup_lng
    )
    
    delivery_distance = calculate_distance(
        order.pickup_lat, order.pickup_lng,
        order.drop_lat, order.drop_lng
    )
    
    total_distance = pickup_distance + delivery_distance
    
    # Distance score (inverse of distance)
    distance_score = 100.0 / (total_distance + 1.0)
    score += distance_score * 0.4
    
    # Driver rating bonus
    rating_score = (driver.rating - 3.0) / 2.0  # Normalize to 0-1
    score += rating_score * 0.2
    
    # Acceptance rate bonus
    acceptance_score = driver.acceptance_rate_7d
    score += acceptance_score * 0.1
    
    # Time urgency bonus (orders closer to expiry get higher priority)
    time_until_expiry = (order.latest_departure - current_time).total_seconds() / 3600  # hours
    urgency_score = max(0, 1.0 - time_until_expiry / 24.0)  # Higher for urgent orders
    score += urgency_score * 0.2
    
    # Capacity utilization bonus
    volume_utilization = order.parcel_volume_l / driver.capacity_volume_l
    weight_utilization = order.parcel_weight_kg / driver.max_weight_kg
    utilization_score = (volume_utilization + weight_utilization) / 2
    score += utilization_score * 0.1
    
    return score

def filter_orders_by_constraints(
    orders: List[Order],
    constraints: Dict
) -> List[Order]:
    """
    Filter orders based on given constraints.
    
    Args:
        orders: List of orders to filter
        constraints: Dictionary of constraints
    
    Returns:
        Filtered list of orders
    """
    filtered_orders = []
    
    for order in orders:
        # Check size constraints
        if 'max_size' in constraints:
            if order.parcel_size_class.value not in constraints['max_size']:
                continue
        
        # Check service level constraints
        if 'service_levels' in constraints:
            if order.service_level.value not in constraints['service_levels']:
                continue
        
        # Check time constraints
        if 'max_delivery_time' in constraints:
            delivery_time = (order.time_window_end - order.time_window_start).total_seconds() / 3600
            if delivery_time > constraints['max_delivery_time']:
                continue
        
        filtered_orders.append(order)
    
    return filtered_orders

def filter_drivers_by_constraints(
    drivers: List[Driver],
    constraints: Dict
) -> List[Driver]:
    """
    Filter drivers based on given constraints.
    
    Args:
        drivers: List of drivers to filter
        constraints: Dictionary of constraints
    
    Returns:
        Filtered list of drivers
    """
    filtered_drivers = []
    
    for driver in drivers:
        # Check vehicle type constraints
        if 'vehicle_types' in constraints:
            if driver.vehicle_type.value not in constraints['vehicle_types']:
                continue
        
        # Check capacity constraints
        if 'min_capacity_volume' in constraints:
            if driver.capacity_volume_l < constraints['min_capacity_volume']:
                continue
        
        if 'min_capacity_weight' in constraints:
            if driver.max_weight_kg < constraints['min_capacity_weight']:
                continue
        
        # Check rating constraints
        if 'min_rating' in constraints:
            if driver.rating < constraints['min_rating']:
                continue
        
        # Check availability constraints
        if 'min_acceptance_rate' in constraints:
            if driver.acceptance_rate_7d < constraints['min_acceptance_rate']:
                continue
        
        filtered_drivers.append(driver)
    
    return filtered_drivers

# pricing.py
from typing import Dict, Tuple, Optional
from datetime import datetime
import math
from ..config import (
    SIZE_BASE_PRICES, SERVICE_LEVEL_FACTORS, TIME_SLOT_DISCOUNTS,
    WAGE_MODELS, COMMISSION_RATE, get_time_slot, get_grid_cell, 
    get_surge_multiplier, calculate_distance
)

def calculate_order_price(
    order: 'Order',
    current_time: datetime,
    pricing_model: str = "dynamic",
    base_distance_km: Optional[float] = None
) -> float:
    """
    Calculate the final price for an order.
    
    Args:
        order: The order object
        current_time: Current simulation time
        pricing_model: "fixed" or "dynamic"
        base_distance_km: Pre-calculated distance (optional)
    
    Returns:
        Final price for the order
    """
    if base_distance_km is None:
        base_distance_km = calculate_distance(
            order.pickup_lat, order.pickup_lng,
            order.drop_lat, order.drop_lng
        )
    
    # Base price calculation
    size_price = SIZE_BASE_PRICES.get(order.parcel_size_class.value, 1.0)
    base_price = size_price * base_distance_km
    
    if pricing_model == "fixed":
        return base_price
    
    # Dynamic pricing
    time_slot = get_time_slot(current_time)
    grid_cell = get_grid_cell(order.pickup_lat, order.pickup_lng)
    surge_multiplier = get_surge_multiplier(grid_cell, time_slot)
    
    # Service level factor
    service_factor = SERVICE_LEVEL_FACTORS.get(order.service_level.value, 1.0)
    
    # Time slot discounts
    time_discount = 0.0
    if order.service_level.value in TIME_SLOT_DISCOUNTS:
        time_discount = TIME_SLOT_DISCOUNTS[order.service_level.value]
    
    # Calculate final price
    final_price = base_price * surge_multiplier * service_factor * (1 - time_discount)
    
    return max(final_price, base_price * 0.5)  # Minimum 50% of base price

def calculate_driver_wage(
    distance_km: float,
    time_minutes: float,
    wage_model: str = "fixed",
    driver_rating: float = 4.5,
    surge_multiplier: float = 1.0
) -> float:
    """
    Calculate driver wage for a delivery.
    
    Args:
        distance_km: Distance traveled in kilometers
        time_minutes: Time taken in minutes
        wage_model: "fixed" or "dynamic"
        driver_rating: Driver's rating (1.0 to 5.0)
        surge_multiplier: Current surge multiplier
    
    Returns:
        Driver wage for the delivery
    """
    if wage_model == "fixed":
        model = WAGE_MODELS["fixed"]
        wage = (distance_km * model["base_per_km"] + 
                time_minutes * model["base_per_min"])
    else:
        model = WAGE_MODELS["dynamic"]
        base_wage = (distance_km * model["base_per_km"] + 
                     time_minutes * model["base_per_min"])
        
        # Apply surge multiplier
        surge_bonus = base_wage * (surge_multiplier - 1.0) * model["surge_multiplier"]
        
        # Rating bonus
        rating_bonus = base_wage * (driver_rating - 4.0) * model["rating_bonus"]
        
        wage = base_wage + surge_bonus + rating_bonus
    
    return max(wage, 1.0)  # Minimum wage of 1.0

def calculate_platform_profit(
    order_price: float,
    driver_wage: float,
    commission_rate: float = None
) -> float:
    """
    Calculate platform profit for an order.
    
    Args:
        order_price: Final price charged to customer
        driver_wage: Wage paid to driver
        commission_rate: Platform commission rate (default from config)
    
    Returns:
        Platform profit
    """
    if commission_rate is None:
        commission_rate = COMMISSION_RATE
    
    # Platform takes commission from order price
    commission_earnings = order_price * commission_rate
    
    # Net profit is commission minus any additional costs
    # For now, assuming commission is the main revenue source
    net_profit = commission_earnings
    
    return net_profit

def calculate_detour_cost(
    driver_current_lat: float,
    driver_current_lng: float,
    pickup_lat: float,
    pickup_lng: float,
    drop_lat: float,
    drop_lng: float,
    driver_speed_kmph: float
) -> Tuple[float, float]:
    """
    Calculate the additional cost and time due to detour.
    
    Args:
        driver_current_lat, driver_current_lng: Driver's current location
        pickup_lat, pickup_lng: Order pickup location
        drop_lat, drop_lng: Order delivery location
        driver_speed_kmph: Driver's speed in km/h
    
    Returns:
        Tuple of (detour_distance_km, detour_time_minutes)
    """
    # Direct route: pickup -> drop
    direct_distance = calculate_distance(pickup_lat, pickup_lng, drop_lat, drop_lng)
    
    # Actual route: driver_current -> pickup -> drop
    driver_to_pickup = calculate_distance(
        driver_current_lat, driver_current_lng, pickup_lat, pickup_lng
    )
    pickup_to_drop = calculate_distance(pickup_lat, pickup_lng, drop_lat, drop_lng)
    actual_distance = driver_to_pickup + pickup_to_drop
    
    # Detour is the additional distance
    detour_distance = actual_distance - direct_distance
    
    # Calculate detour time
    detour_time_minutes = (detour_distance / driver_speed_kmph) * 60
    
    return detour_distance, detour_time_minutes

def calculate_bundle_efficiency(
    orders: list,
    driver: 'Driver'
) -> float:
    """
    Calculate efficiency score for bundling multiple orders.
    
    Args:
        orders: List of orders to be bundled
        driver: Driver who would handle the bundle
    
    Returns:
        Efficiency score (higher is better)
    """
    if not orders:
        return 0.0
    
    # Calculate total volume and weight
    total_volume = sum(order.parcel_volume_l for order in orders)
    total_weight = sum(order.parcel_weight_kg for order in orders)
    
    # Check capacity constraints
    if (total_volume > driver.capacity_volume_l or 
        total_weight > driver.max_weight_kg):
        return 0.0
    
    # Calculate route efficiency
    # For simplicity, assume orders are sorted by pickup time
    total_distance = 0.0
    current_lat, current_lng = driver.current_lat, driver.current_lng
    
    for order in orders:
        # Distance to pickup
        pickup_distance = calculate_distance(
            current_lat, current_lng, order.pickup_lat, order.pickup_lng
        )
        total_distance += pickup_distance
        
        # Distance from pickup to drop
        delivery_distance = calculate_distance(
            order.pickup_lat, order.pickup_lng, order.drop_lat, order.drop_lng
        )
        total_distance += delivery_distance
        
        # Update current position
        current_lat, current_lng = order.drop_lat, order.drop_lng
    
    # Efficiency is inverse of total distance (lower distance = higher efficiency)
    efficiency = 1000.0 / (total_distance + 1.0)  # Add 1 to avoid division by zero
    
    # Bonus for utilizing capacity well
    volume_utilization = total_volume / driver.capacity_volume_l
    weight_utilization = total_weight / driver.max_weight_kg
    utilization_bonus = (volume_utilization + weight_utilization) / 2
    
    efficiency *= (1 + utilization_bonus)
    
    return efficiency

def get_dynamic_pricing_parameters(
    current_time: datetime,
    location_lat: float,
    location_lng: float,
    demand_level: float = 1.0
) -> Dict[str, float]:
    """
    Get dynamic pricing parameters for a specific time and location.
    
    Args:
        current_time: Current simulation time
        location_lat, location_lng: Location coordinates
        demand_level: Current demand level (0.0 to 2.0)
    
    Returns:
        Dictionary of pricing parameters
    """
    time_slot = get_time_slot(current_time)
    grid_cell = get_grid_cell(location_lat, location_lng)
    
    # Base surge multiplier
    base_surge = get_surge_multiplier(grid_cell, time_slot)
    
    # Adjust based on demand level
    demand_adjusted_surge = base_surge * (0.8 + 0.4 * demand_level)
    
    # Time-based adjustments
    hour = current_time.hour
    if 7 <= hour <= 9:  # Morning rush
        time_factor = 1.2
    elif 17 <= hour <= 19:  # Evening rush
        time_factor = 1.3
    else:
        time_factor = 1.0
    
    final_surge = demand_adjusted_surge * time_factor
    
    return {
        "surge_multiplier": final_surge,
        "time_factor": time_factor,
        "demand_factor": demand_level,
        "base_surge": base_surge
    }

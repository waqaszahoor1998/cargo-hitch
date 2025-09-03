# ============================================================================
# CARGO HITCHHIKING SIMULATION CONFIGURATION
# ============================================================================
# This file contains all the settings and constants used in the simulation
# It defines how the simulation behaves and what parameters it uses

from datetime import datetime, timedelta
from typing import Dict, Tuple
import math

# ============================================================================
# SIMULATION TIME PARAMETERS
# ============================================================================
# These define when the simulation runs and how often it updates

SIMULATION_START_TIME = datetime(2024, 1, 1, 8, 0)  # 8 AM - simulation starts
SIMULATION_END_TIME = datetime(2024, 1, 1, 20, 0)   # 8 PM - simulation ends
TICK_INTERVAL_MINUTES = 15  # How often the simulation updates (every 15 minutes)

# ============================================================================
# ISLAMABAD GEOGRAPHIC SETTINGS
# ============================================================================
# Real coordinates for Islamabad, Pakistan
# These are used to generate realistic pickup and dropoff locations

ISLAMABAD_CENTER = (33.7294, 73.0931)  # Center of Islamabad (latitude, longitude)
CITY_RADIUS_KM = 25.0  # How far from center orders can be (25km radius)

# ============================================================================
# SURGE PRICING CONFIGURATION
# ============================================================================
# This system adjusts prices based on time of day and location
# Higher demand times get higher prices

GRID_SIZE_KM = 5.0  # Size of each pricing grid cell (5km x 5km)

# Time slots for different pricing periods
TIME_SLOTS = {
    "morning": (8, 10),      # 8 AM - 10 AM (rush hour)
    "midday": (10, 16),      # 10 AM - 4 PM (normal hours)
    "evening": (16, 20),     # 4 PM - 8 PM (rush hour)
    "night": (20, 8)         # 8 PM - 8 AM next day (off-peak)
}

# Price multipliers for different time slots
# Higher numbers = higher prices during that time
SURGE_MULTIPLIERS = {
    "morning": 1.3,    # 30% higher prices in morning rush
    "midday": 1.0,     # Normal prices during day
    "evening": 1.4,    # 40% higher prices in evening rush
    "night": 0.8       # 20% lower prices at night
}

# ============================================================================
# SERVICE LEVEL PRICING
# ============================================================================
# Different delivery speeds cost different amounts
# Faster delivery = higher price

SERVICE_LEVEL_FACTORS = {
    "same_day": 1.2,    # Same day delivery costs 20% more
    "next_day": 1.0,    # Next day delivery is standard price
    "flex": 0.8         # Flexible delivery gets 20% discount
}

# ============================================================================
# PARCEL SIZE PRICING
# ============================================================================
# Base price per kilometer for different package sizes
# Larger packages cost more to deliver

SIZE_BASE_PRICES = {
    "XS": 0.5,   # Extra Small packages (Rs 0.5 per km)
    "S": 0.8,    # Small packages (Rs 0.8 per km)
    "M": 1.2,    # Medium packages (Rs 1.2 per km) - base rate
    "L": 1.8,    # Large packages (Rs 1.8 per km)
    "XL": 2.5    # Extra Large packages (Rs 2.5 per km)
}

# ============================================================================
# DRIVER WAGE MODELS
# ============================================================================
# How much drivers get paid for deliveries
# Two models: fixed rates or dynamic rates based on conditions

WAGE_MODELS = {
    "fixed": {
        "base_per_km": 0.4,    # Rs 0.4 per kilometer
        "base_per_min": 0.02   # Rs 0.02 per minute
    },
    "dynamic": {
        "base_per_km": 0.3,           # Base Rs 0.3 per kilometer
        "base_per_min": 0.015,        # Base Rs 0.015 per minute
        "surge_multiplier": 1.2,      # 20% bonus during surge times
        "rating_bonus": 0.1           # 10% bonus for high-rated drivers
    }
}

# ============================================================================
# PLATFORM BUSINESS SETTINGS
# ============================================================================
# How the platform makes money and operates

COMMISSION_RATE = 0.15  # Platform takes 15% commission from each delivery

# Pricing models available
PRICE_MODELS = {
    "fixed": "fixed",      # Fixed prices regardless of conditions
    "dynamic": "dynamic"   # Prices change based on demand and time
}

# ============================================================================
# TIME SLOT DISCOUNTS
# ============================================================================
# Discounts for choosing slower delivery options

TIME_SLOT_DISCOUNTS = {
    "next_day": 0.1,   # 10% discount for next-day delivery
    "flex": 0.2        # 20% discount for flexible delivery
}

# ============================================================================
# NETWORK AND TRAFFIC PARAMETERS
# ============================================================================
# How fast vehicles move and how traffic affects them

AVERAGE_SPEED_KMH = 30.0  # Average speed in kilometers per hour

# Traffic factors for different times of day
# Lower numbers = slower due to traffic
TRAFFIC_FACTORS = {
    "morning": 0.7,    # 30% slower due to morning traffic
    "midday": 0.9,     # 10% slower during day
    "evening": 0.6,    # 40% slower due to evening traffic
    "night": 1.1       # 10% faster at night (less traffic)
}

# ============================================================================
# MATCHING CONSTRAINTS
# ============================================================================
# Rules that limit which orders can be matched to which drivers

MAX_DETOUR_KM = 30.0  # Maximum extra distance driver can travel (30km)
MAX_BUNDLE_SIZE = 5   # Maximum orders one driver can carry at once
ASSIGNMENT_TIME_LIMIT_SECONDS = 2.0  # How long matching algorithm can run

# ============================================================================
# FLEET CONFIGURATION
# ============================================================================
# Settings for dedicated fleet vehicles (backup delivery system)

FLEET_CONFIG = {
    "num_vehicles": 10,           # Number of fleet vehicles
    "capacity_volume_l": 500.0,   # 500 liters capacity per vehicle
    "max_weight_kg": 200.0,       # 200kg weight limit per vehicle
    "cost_per_km": 2.0,           # Rs 2 per kilometer for fleet
    "cost_per_min": 0.1           # Rs 0.1 per minute for fleet
}

# ============================================================================
# DRIVER GENERATION PARAMETERS
# ============================================================================
# How many drivers to create and what types

DRIVER_GENERATION = {
    "total_drivers": 150,  # Total number of drivers in simulation
    
    # What types of vehicles drivers use
    "vehicle_distribution": {
        "bike": 0.1,        # 10% of drivers use bikes
        "motorbike": 0.3,   # 30% of drivers use motorbikes
        "car": 0.4,         # 40% of drivers use cars
        "van": 0.2          # 20% of drivers use vans
    },
    
    # When drivers are available to work
    "availability_patterns": {
        "morning_shift": (8, 12),    # 8 AM to 12 PM
        "afternoon_shift": (12, 16), # 12 PM to 4 PM
        "evening_shift": (16, 20),   # 4 PM to 8 PM
        "full_day": (8, 20)          # 8 AM to 8 PM
    }
}

# ============================================================================
# ORDER GENERATION PARAMETERS
# ============================================================================
# How many orders to create and what types

ORDER_GENERATION = {
    "total_orders": 200,  # Total number of orders in simulation
    
    # What sizes of packages people order
    "size_distribution": {
        "XS": 0.2,  # 20% of orders are extra small
        "S": 0.3,   # 30% of orders are small
        "M": 0.3,   # 30% of orders are medium
        "L": 0.15,  # 15% of orders are large
        "XL": 0.05  # 5% of orders are extra large
    },
    
    # What delivery speeds people choose
    "service_level_distribution": {
        "same_day": 0.4,   # 40% want same-day delivery
        "next_day": 0.4,   # 40% want next-day delivery
        "flex": 0.2        # 20% want flexible delivery
    },
    
    # How long delivery windows are
    "time_window_distribution": {
        "1_hour": 0.3,   # 30% have 1-hour delivery windows
        "2_hours": 0.4,  # 40% have 2-hour delivery windows
        "4_hours": 0.2,  # 20% have 4-hour delivery windows
        "8_hours": 0.1   # 10% have 8-hour delivery windows
    }
}

# ============================================================================
# KPI TARGETS (KEY PERFORMANCE INDICATORS)
# ============================================================================
# Goals for how well the system should perform

KPI_TARGETS = {
    "match_rate": 0.85,           # 85% of orders should be matched to drivers
    "on_time_delivery": 0.90,     # 90% of deliveries should be on time
    "max_avg_cost": 15.0,         # Average delivery cost should be under Rs 15
    "min_profit_margin": 0.20,    # At least 20% profit margin
    "max_fleet_usage": 0.30       # Use dedicated fleet for max 30% of deliveries
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
# Helper functions used throughout the simulation

def get_time_slot(current_time: datetime) -> str:
    """
    Get the current time slot for surge pricing.
    
    Args:
        current_time: Current simulation time
        
    Returns:
        Time slot name: "morning", "midday", "evening", or "night"
    """
    hour = current_time.hour
    
    if 8 <= hour < 10:
        return "morning"
    elif 10 <= hour < 16:
        return "midday"
    elif 16 <= hour < 20:
        return "evening"
    else:
        return "night"

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    This is the standard way to calculate distances on Earth's surface.
    It accounts for the fact that Earth is round, not flat.
    
    Args:
        lat1, lng1: Latitude and longitude of first point
        lat2, lng2: Latitude and longitude of second point
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def get_grid_cell(lat: float, lng: float) -> Tuple[int, int]:
    """
    Get grid cell coordinates for surge pricing.
    
    Divides the city into a grid for location-based pricing.
    Each grid cell is 5km x 5km.
    
    Args:
        lat, lng: Latitude and longitude of location
        
    Returns:
        Grid cell coordinates (row, column)
    """
    # Convert to grid coordinates relative to Islamabad center
    center_lat, center_lng = ISLAMABAD_CENTER
    
    # Calculate grid cell (simplified)
    lat_offset = lat - center_lat
    lng_offset = lng - center_lng
    
    # Convert to grid coordinates
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 * cos(latitude) km
    grid_lat = int(lat_offset / (GRID_SIZE_KM / 111.0))
    grid_lng = int(lng_offset / (GRID_SIZE_KM / (111.0 * math.cos(math.radians(center_lat)))))
    
    return grid_lat, grid_lng

def get_surge_multiplier(grid_cell: Tuple[int, int], time_slot: str) -> float:
    """
    Get surge multiplier for a specific grid cell and time slot.
    
    This determines how much prices increase based on location and time.
    
    Args:
        grid_cell: Grid cell coordinates (row, column)
        time_slot: Time slot ("morning", "midday", "evening", "night")
        
    Returns:
        Price multiplier (1.0 = normal price, 1.3 = 30% higher, etc.)
    """
    # Base surge from time slot
    base_surge = SURGE_MULTIPLIERS.get(time_slot, 1.0)
    
    # In a real system, you would add location-based surge here
    # For now, return base surge
    return base_surge

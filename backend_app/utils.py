"""
Auxiliary functions for the backend
"""
from typing import Tuple
import uuid
import math

_EARTH_RADIUS_KM = 6371.0088


def is_valid_uuid(uuid_str: str) -> bool:
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def geodesic_km(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> float:
    """Calculate the geodesic distance between two points on the Earth's surface.

    Args:
        point_a (Tuple[float, float]): (latitude, longitude) of the first point.
        point_b (Tuple[float, float]): (latitude, longitude) of the second point.

    Returns:
        float: Distance in kilometers.
    """
    lat1, lon1 = point_a
    lat2, lon2 = point_b

    # Convert degrees to radians
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δφ = φ2 - φ1
    Δλ = math.radians(lon2 - lon1)
    
    # Haversine formula
    sin_dφ = math.sin(Δφ / 2)
    sin_dλ = math.sin(Δλ / 2)
    a = sin_dφ**2 + math.cos(φ1) * math.cos(φ2) * sin_dλ**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return _EARTH_RADIUS_KM * c

"""
Auxiliary functions for the backend
"""
from typing import Tuple
import uuid
import math
from datetime import datetime

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


def get_color_palette(n_colors: int) -> list:
    """Generate a color palette """
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    if n_colors <= len(colors):
        return colors[:n_colors]
    # Generate additional colors if needed
    import colorsys
    additional_colors = []
    for i in range(n_colors - len(colors)):
        hue = i / (n_colors - len(colors))
        rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        additional_colors.append(hex_color)

    return colors + additional_colors


def extract_fields(data: dict):
    """ Extract unit_id (or units_id), start_date, end_date from data dict """
    unit_id = data.get('unit_id') or data.get('units_id')
    try:
        start_date = datetime.fromisoformat(data.get("start_time"))
    except TypeError:
        start_date = None
    try:
        end_date = datetime.fromisoformat(data.get("end_time"))
    except TypeError:
        end_date = None
    return unit_id, start_date, end_date

from math import sin, cos, sqrt, atan2, radians
from typing import Tuple

class GeolocationValidator:
    def __init__(self, campus_lat: float, campus_lng: float, allowed_radius: float):
        self.campus_lat = radians(campus_lat)
        self.campus_lng = radians(campus_lng)
        self.allowed_radius = allowed_radius  # in meters
        self.R = 6371000  # Earth's radius in meters

    def calculate_distance(self, lat2: float, lng2: float) -> float:
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)

        dlat = lat2_rad - self.campus_lat
        dlng = lng2_rad - self.campus_lng

        a = sin(dlat/2)**2 + cos(self.campus_lat) * cos(lat2_rad) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = self.R * c

        return distance

    async def validate_location(self, latitude: float, longitude: float) -> Tuple[bool, float]:
        distance = self.calculate_distance(latitude, longitude)
        is_valid = distance <= self.allowed_radius
        return is_valid, distance
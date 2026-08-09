import math


class GeoService:
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
        r = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return int(round(r * c))

    @staticmethod
    def calculate_walking_time_minutes(distance_meters: int, speed_m_per_min: float = 80.0) -> int:
        if distance_meters <= 0:
            return 1
        return max(1, math.ceil(distance_meters / speed_m_per_min))

    @staticmethod
    def build_google_maps_url(lat: float, lon: float) -> str:
        return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"

from app.services.geo import GeoService


def test_haversine_distance() -> None:
    dist = GeoService.haversine_distance(51.5033, -0.1195, 51.5007, -0.1246)
    assert 440 <= dist <= 500


def test_calculate_walking_time_minutes() -> None:
    walk_min = GeoService.calculate_walking_time_minutes(480)
    assert walk_min == 6

    walk_short = GeoService.calculate_walking_time_minutes(50)
    assert walk_short == 1

import math

from backend_app.utils import is_valid_uuid, geodesic_km


def test_is_valid_uuid():
    assert is_valid_uuid("123e4567-e89b-12d3-a456-426614174000")
    assert not is_valid_uuid("invalid-uuid-string")
    assert not is_valid_uuid("")
    assert not is_valid_uuid(None)


def test_geodesic_km():
    assert geodesic_km((0, 0), (0, 0)) == 0.0
    d = geodesic_km((0, 0), (1, 0))
    assert 110 < d < 112
    assert math.isclose(geodesic_km((0, 0), (0, 1)), 111.32, rel_tol=1e-2)



import math

from backend_app.utils import is_valid_uuid, geodesic_km, get_color_palette


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


def test_get_color_palette_base_branch():
    """Covers the early return branch of get_color_palette when requested colors <= base palette size."""
    palette = get_color_palette(5)
    assert palette == [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'
    ]
    assert len(palette) == 5


def test_get_color_palette_extension():
    # Request more colors than base list to trigger extension branch
    colors = get_color_palette(15)
    assert len(colors) == 15
    assert len(set(colors)) == 15

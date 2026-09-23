from hypothesis import given, strategies as st
from vajra_core.grid.spec import GridSpec
from vajra_core.grid.tiling import TileConfig, coord_to_rc, rc_to_coord, rc_to_tile_id, tile_id_to_rc_bounds
import pytest
import math

test_spec = GridSpec(
    id="test_grid",
    crs="EPSG:4326",
    xmin=0.0,
    ymin=0.0,
    xmax=10.0,
    ymax=10.0,
    dx=0.1,
    dy=0.1
)

@given(
    x=st.floats(min_value=0.0, max_value=9.99),
    y=st.floats(min_value=0.0, max_value=9.99)
)
def test_coord_to_rc_roundtrip(x, y):
    r, c = coord_to_rc(x, y, test_spec)
    assert 0 <= r < test_spec.height
    assert 0 <= c < test_spec.width
    
    rx, ry = rc_to_coord(r, c, test_spec)
    # The coordinate from rc_to_coord should be the center of the cell
    assert abs(rx - x) <= test_spec.dx
    assert abs(ry - y) <= test_spec.dy

def test_tiling():
    cfg = TileConfig(size=256, overlap=16)
    tile_id = rc_to_tile_id(100, 100, cfg)
    assert tile_id == "0_0"
    
    r_s, r_e, c_s, c_e = tile_id_to_rc_bounds("0_0", cfg)
    assert r_s == 0
    assert c_s == 0
    assert r_e == 256
    assert c_e == 256
    
    # Overlap step = 256 - 16 = 240
    tile_id2 = rc_to_tile_id(240, 240, cfg)
    assert tile_id2 == "1_1"

def test_h3():
    try:
        from vajra_core.grid.h3_idx import latlon_to_h3, h3_to_latlon, get_h3_neighbors
        lat, lon = 20.0, 80.0
        h3_id = latlon_to_h3(lat, lon, 7)
        rlat, rlon = h3_to_latlon(h3_id)
        # H3 center is close to original
        assert abs(lat - rlat) < 0.1
        assert abs(lon - rlon) < 0.1
        
        neighbors = get_h3_neighbors(h3_id)
        assert len(neighbors) == 7 # Cell itself + 6 neighbors
    except ImportError:
        pytest.skip("h3 is not properly built on this system")

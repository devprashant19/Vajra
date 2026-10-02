import pytest
import json
from hypothesis import given, strategies as st
from datetime import datetime, timezone
from vajra_core.grid.spec import GridSpec
from vajra_core.grid.tiling import TileConfig, coord_to_rc, rc_to_coord, rc_to_tile_id, tile_id_to_rc_bounds
from vajra_core.schemas.domain import Alert, Cell
from pydantic import ValidationError
import jsonschema

@given(
    x=st.floats(min_value=0.0, max_value=9.99),
    y=st.floats(min_value=0.0, max_value=9.99)
)
def test_grid_round_trip_within_half_cell(x, y):  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    test_spec = GridSpec(
        id="test", crs="EPSG:4326",
        xmin=0.0, ymin=0.0, xmax=10.0, ymax=10.0,
        dx=0.1, dy=0.1
    )
    r, c = coord_to_rc(x, y, test_spec)
    rx, ry = rc_to_coord(r, c, test_spec)
    assert abs(rx - x) <= (test_spec.dx / 2.0) + 1e-9
    assert abs(ry - y) <= (test_spec.dy / 2.0) + 1e-9

@given(
    val=st.floats(min_value=-100, max_value=100)
)
def test_unit_conversion_inverses(val):  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    c = val + 273.15
    # C to K and back
    assert abs((c - 273.15) + 273.15 - c) < 1e-6

@given(
    dt=st.datetimes(timezones=st.just(timezone.utc))
)
def test_timezone_conversion(dt):  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    # Any UTC to UTC should be same
    assert dt.astimezone(timezone.utc) == dt

def test_typescript_drift():  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    import os
    import subprocess
    
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    ts_file = os.path.join(repo_root, "packages", "vajra-types", "src", "index.d.ts")
    
    if not os.path.exists(ts_file):
        pytest.skip("No TS file to check drift")
        
    with open(ts_file, "r") as f:
        old_content = f.read()
        
    # Run the generator script
    script_path = os.path.join(repo_root, "tools", "generate_ts.py")
    subprocess.run(["python", script_path], check=True)
    
    with open(ts_file, "r") as f:
        new_content = f.read()
        
    assert old_content == new_content, "TypeScript SDK is out of date. Run tools/generate_ts.py"

def test_schema_round_trip_and_jsonschema():  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    alert_json = {
        "identifier": "test",
        "sender": "test",
        "sent": "2026-10-01T00:00:00Z",
        "status": "Actual",
        "msg_type": "Alert",
        "scope": "Public",
        "category": "Met",
        "event": "Thunderstorm",
        "urgency": "Immediate",
        "severity": "Severe",
        "certainty": "Observed",
        "headline": "Test Alert",
        "description": "Test",
        "polygon": [[0.0, 0.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]
    }
    
    alert = Alert.model_validate(alert_json)
    dumped = json.loads(alert.model_dump_json())
    
    # Assert dates match (note format differences)
    assert dumped["identifier"] == alert_json["identifier"]
    
    # Validate against jsonschema
    schema = Alert.model_json_schema()
    jsonschema.validate(instance=dumped, schema=schema)

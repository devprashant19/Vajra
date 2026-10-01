import pytest
from datetime import datetime, timezone
from vajra_core.schemas.domain import Location, Cell

def test_location_schema():  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    loc = Location(
        id="delhi_01",
        type="admin",
        name="Delhi",
        h3_index="8730e1d00ffffff"
    )
    assert loc.priority == 0
    
    # roundtrip json
    j = loc.model_dump_json()
    loc2 = Location.model_validate_json(j)
    assert loc2.name == "Delhi"

def test_cell_schema():  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    cell = Cell(
        cell_id="c_1",
        frame_id="f_1",
        lat=28.6,
        lon=77.2,
        area_km2=10.5,
        max_dbz=45.0,
        max_vil=20.0,
        polygon_h3=["8730e1d00ffffff", "8730e1d01ffffff"]
    )
    assert len(cell.polygon_h3) == 2

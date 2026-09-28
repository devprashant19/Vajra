import h3 # type: ignore

def latlon_to_h3(lat: float, lon: float, resolution: int = 7) -> str:
    """Convert a lat/lon to an H3 index at the given resolution."""
    return h3.latlng_to_cell(lat, lon, resolution)

def h3_to_latlon(h3_id: str) -> tuple[float, float]:
    """Convert an H3 index to its center lat/lon."""
    return h3.cell_to_latlng(h3_id)

def get_h3_neighbors(h3_id: str) -> set[str]:
    """Get the immediate neighbors of an H3 cell."""
    return set(h3.grid_disk(h3_id, 1))

def get_h3_polygon(h3_id: str) -> list[tuple[float, float]]:
    """Get the boundary polygon of an H3 cell as [(lat, lon), ...]."""
    return h3.cell_to_boundary(h3_id)

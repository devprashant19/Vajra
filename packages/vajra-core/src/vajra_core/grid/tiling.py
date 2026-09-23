from typing import Tuple, List, Optional
from pydantic import BaseModel
import math

from .spec import GridSpec

class TileConfig(BaseModel):
    size: int = 256
    overlap: int = 16

def coord_to_rc(x: float, y: float, spec: GridSpec) -> Tuple[int, int]:
    """Convert a geographical or projected coordinate to row, col index in the grid."""
    col = int(math.floor((x - spec.xmin) / spec.dx))
    # Y is usually top-down in image space, but grid is bottom-up (ymin to ymax)
    # Row 0 is at ymin
    row = int(math.floor((y - spec.ymin) / spec.dy))
    return (row, col)

def rc_to_coord(row: int, col: int, spec: GridSpec) -> Tuple[float, float]:
    """Convert a row, col index to the coordinate (x, y) of the cell's center."""
    x = spec.xmin + (col + 0.5) * spec.dx
    y = spec.ymin + (row + 0.5) * spec.dy
    return (x, y)

def rc_to_tile_id(row: int, col: int, config: TileConfig) -> str:
    """Get the global tile ID for a specific row and col."""
    step = config.size - config.overlap
    tile_row = math.floor(row / step)
    tile_col = math.floor(col / step)
    return f"{tile_row}_{tile_col}"

def tile_id_to_rc_bounds(tile_id: str, config: TileConfig) -> Tuple[int, int, int, int]:
    """Get the row_start, row_end, col_start, col_end bounds for a tile ID."""
    parts = tile_id.split("_")
    tile_row = int(parts[0])
    tile_col = int(parts[1])
    step = config.size - config.overlap
    
    r_start = tile_row * step
    r_end = r_start + config.size
    c_start = tile_col * step
    c_end = c_start + config.size
    
    return (r_start, r_end, c_start, c_end)

def get_neighbors(tile_id: str) -> List[str]:
    """Get the 8 neighbors of a tile."""
    parts = tile_id.split("_")
    r, c = int(parts[0]), int(parts[1])
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            neighbors.append(f"{r+dr}_{c+dc}")
    return neighbors

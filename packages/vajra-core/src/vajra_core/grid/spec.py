from pydantic import BaseModel
from typing import Tuple

class GridSpec(BaseModel):
    """
    Specification for a regular grid.
    Can represent geographic (EPSG:4326) or projected metric grids.
    """
    id: str
    crs: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    dx: float
    dy: float

    @property
    def width(self) -> int:
        return int(round((self.xmax - self.xmin) / self.dx))

    @property
    def height(self) -> int:
        return int(round((self.ymax - self.ymin) / self.dy))

    @property
    def shape(self) -> Tuple[int, int]:
        """Returns (height, width) for numpy/xarray dimensions"""
        return (self.height, self.width)


# EPSG:4326 National Grid for India
# Bounds: 68E to 98E, 6N to 38N
# Resolution: 0.02 degrees (~2.2 km)
NATIONAL_GRID = GridSpec(
    id="national_0.02deg",
    crs="EPSG:4326",
    xmin=68.0,
    ymin=6.0,
    xmax=98.0,
    ymax=38.0,
    dx=0.02,
    dy=0.02
)

# Regional Grid
# Resolution: 0.01 degrees (~1.1 km)
REGIONAL_GRID = GridSpec(
    id="regional_0.01deg",
    crs="EPSG:4326",
    xmin=68.0,
    ymin=6.0,
    xmax=98.0,
    ymax=38.0,
    dx=0.01,
    dy=0.01
)

# EPSG:7755 (India LCC) equivalent metric grid (Approximate bounds)
NATIONAL_METRIC_GRID = GridSpec(
    id="national_2km_epsg7755",
    crs="EPSG:7755",
    xmin=-1500000.0,
    ymin=-1500000.0,
    xmax=1500000.0,
    ymax=2000000.0,
    dx=2000.0,
    dy=2000.0
)

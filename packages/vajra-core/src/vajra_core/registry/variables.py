from pydantic import BaseModel
from typing import Optional, Dict

class VariableSpec(BaseModel):
    name: str
    unit: str
    min_val: float
    max_val: float
    source_group: str
    dtype: str
    fill_value: float

REGISTRY: Dict[str, VariableSpec] = {
    # Radar
    "reflectivity": VariableSpec(
        name="reflectivity", unit="dBZ", min_val=-32.0, max_val=95.0, 
        source_group="radar", dtype="float32", fill_value=-999.0
    ),
    "vil": VariableSpec(
        name="vertically_integrated_liquid", unit="kg/m2", min_val=0.0, max_val=150.0, 
        source_group="radar", dtype="float32", fill_value=-999.0
    ),
    "echo_top": VariableSpec(
        name="echo_top", unit="km", min_val=0.0, max_val=25.0, 
        source_group="radar", dtype="float32", fill_value=-999.0
    ),
    
    # Satellite
    "bt_108": VariableSpec(
        name="brightness_temp_108", unit="K", min_val=150.0, max_val=350.0, 
        source_group="satellite", dtype="float32", fill_value=-999.0
    ),
    "bt_120": VariableSpec(
        name="brightness_temp_120", unit="K", min_val=150.0, max_val=350.0, 
        source_group="satellite", dtype="float32", fill_value=-999.0
    ),
    "btd": VariableSpec(
        name="brightness_temp_difference", unit="K", min_val=-20.0, max_val=20.0, 
        source_group="satellite", dtype="float32", fill_value=-999.0
    ),
    "cooling_rate": VariableSpec(
        name="cooling_rate", unit="K/15min", min_val=-50.0, max_val=50.0, 
        source_group="satellite", dtype="float32", fill_value=-999.0
    ),

    # Lightning
    "flash_density": VariableSpec(
        name="flash_density", unit="flashes/km2/10min", min_val=0.0, max_val=100.0, 
        source_group="lightning", dtype="float32", fill_value=-1.0
    ),

    # NWP Thermodynamics
    "cape": VariableSpec(
        name="cape", unit="J/kg", min_val=0.0, max_val=8000.0, 
        source_group="nwp", dtype="float32", fill_value=-999.0
    ),
    "cin": VariableSpec(
        name="cin", unit="J/kg", min_val=-2000.0, max_val=0.0, 
        source_group="nwp", dtype="float32", fill_value=-999.0
    ),
    "shear_0_6km": VariableSpec(
        name="shear_0_6km", unit="m/s", min_val=0.0, max_val=100.0, 
        source_group="nwp", dtype="float32", fill_value=-999.0
    ),
    "pwat": VariableSpec(
        name="precipitable_water", unit="mm", min_val=0.0, max_val=150.0, 
        source_group="nwp", dtype="float32", fill_value=-999.0
    ),
    "freezing_level": VariableSpec(
        name="freezing_level", unit="m", min_val=0.0, max_val=8000.0, 
        source_group="nwp", dtype="float32", fill_value=-999.0
    ),
    "dcape": VariableSpec(
        name="dcape", unit="J/kg", min_val=0.0, max_val=3000.0, 
        source_group="nwp", dtype="float32", fill_value=-999.0
    ),

    # Precipitation
    "rain_rate": VariableSpec(
        name="rain_rate", unit="mm/h", min_val=0.0, max_val=500.0, 
        source_group="gauge", dtype="float32", fill_value=-999.0
    ),
}

def get_variable(name: str) -> Optional[VariableSpec]:
    return REGISTRY.get(name)

# Unit Conversion Helpers
def celsius_to_kelvin(c: float) -> float:
    return c + 273.15

def kelvin_to_celsius(k: float) -> float:
    return k - 273.15

def knots_to_ms(knots: float) -> float:
    return knots * 0.514444

def ms_to_knots(ms: float) -> float:
    return ms * 1.94384

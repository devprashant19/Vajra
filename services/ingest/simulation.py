import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent
from services.ingest.base import BaseSourceConnector

class SimulatedSource(BaseSourceConnector):
    SCENARIOS = [
        "SIMULATED-Kolkata-NorWester",
        "SIMULATED-Himalaya-Cloudburst",
        "SIMULATED-Vidarbha-Hail",
        "SIMULATED-Delhi-DustStorm"
    ]
    
    def __init__(self, scenario_name: str, seed: int = 42):
        if scenario_name not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario {scenario_name}")
        super().__init__(scenario_name, is_simulated=True)
        self.scenario = scenario_name
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.nx = 256
        self.ny = 256
        self.dx_km = 2.0
        self.n_frames = 25 # 4 hours at 10 min
        self.dt_min = 10
        
        centers = {
            "SIMULATED-Kolkata-NorWester": (22.57, 88.36),
            "SIMULATED-Himalaya-Cloudburst": (31.10, 77.17),
            "SIMULATED-Vidarbha-Hail": (21.15, 79.09),
            "SIMULATED-Delhi-DustStorm": (28.61, 77.23)
        }
        self.center_lat, self.center_lon = centers.get(self.scenario, (20.0, 80.0))
        self.blobs = []
        self._init_blobs()
        self.locations = self._init_locations()

    def _init_blobs(self):
        num_blobs = self.rng.integers(3, 8)
        for i in range(num_blobs):
            self.blobs.append({
                "id": f"cell_{i}",
                "x": self.rng.uniform(20, 230),
                "y": self.rng.uniform(20, 230),
                "vx": self.rng.uniform(0.5, 2.0),
                "vy": self.rng.uniform(0.5, 2.0),
                "radius": self.rng.uniform(5.0, 15.0),
                "intensity": self.rng.uniform(30.0, 50.0),
                "growth_rate": self.rng.uniform(-0.5, 1.0),
                "active": True
            })

    def _init_locations(self) -> List[Dict[str, Any]]:
        locations = []
        for i in range(40):
            loc_lat = self.center_lat + self.rng.uniform(-1.0, 1.0)
            loc_lon = self.center_lon + self.rng.uniform(-1.0, 1.0)
            locations.append({
                "id": f"loc_{i}",
                "name": f"Example Asset {i}",
                "lat": loc_lat,
                "lon": loc_lon,
                "type": self.rng.choice(["district_hq", "airport", "substation"])
            })
        return locations

    def generate_frame(self, t_idx: int, frame_time: datetime) -> Dict[str, Any]:
        dbz = np.zeros((self.ny, self.nx))
        ir = np.full((self.ny, self.nx), 280.0)
        flash = np.zeros((self.ny, self.nx))
        vil = np.zeros((self.ny, self.nx))
        rain_rate = np.zeros((self.ny, self.nx))
        
        cape = np.full((self.ny, self.nx), 2000.0 + self.rng.uniform(-200, 200, (self.ny, self.nx)))
        cin = np.full((self.ny, self.nx), -50.0)
        dcape = np.full((self.ny, self.nx), 800.0)
        freezing_level = np.full((self.ny, self.nx), 4500.0)
        
        current_tracks = []
        
        for blob in self.blobs:
            if not blob["active"]:
                continue
                
            blob["x"] += (blob["vx"] * self.dt_min) / self.dx_km
            blob["y"] += (blob["vy"] * self.dt_min) / self.dx_km
            
            blob["intensity"] += blob["growth_rate"]
            if blob["intensity"] > 65:
                blob["growth_rate"] = -abs(blob["growth_rate"])
            if blob["intensity"] < 20:
                blob["active"] = False
                continue
                
            if blob["intensity"] > 55 and self.rng.random() < 0.05:
                self.blobs.append({
                    "id": f"cell_{len(self.blobs)}",
                    "x": blob["x"] + 5,
                    "y": blob["y"] - 5,
                    "vx": blob["vx"] + self.rng.uniform(-0.5, 0.5),
                    "vy": blob["vy"] + self.rng.uniform(-0.5, 0.5),
                    "radius": blob["radius"] * 0.7,
                    "intensity": blob["intensity"] - 10,
                    "growth_rate": self.rng.uniform(0.1, 0.5),
                    "active": True
                })
                blob["intensity"] -= 5
            
            y_idx, x_idx = np.ogrid[:self.ny, :self.nx]
            dist = np.sqrt((x_idx - blob["x"])**2 + (y_idx - blob["y"])**2)
            mask = dist <= blob["radius"]
            profile = blob["intensity"] * np.exp(-0.5 * (dist / (blob["radius"]/2))**2)
            
            dbz = np.maximum(dbz, profile)
            ir = np.where(mask, 280.0 - profile * 1.5, ir)
            vil = np.maximum(vil, profile * 0.5)
            flash = np.where(mask & (profile > 40), flash + self.rng.integers(0, 5, (self.ny, self.nx)), flash)
            rain_rate = np.maximum(rain_rate, profile * 0.3)
            
            current_tracks.append({
                "id": blob["id"],
                "x_px": blob["x"],
                "y_px": blob["y"],
                "intensity": blob["intensity"]
            })
            
        return {
            "time": frame_time.isoformat(),
            "dbz": dbz,
            "ir": ir,
            "flash": flash,
            "vil": vil,
            "rain_rate": rain_rate,
            "cape": cape,
            "cin": cin,
            "dcape": dcape,
            "freezing_level": freezing_level,
            "tracks": current_tracks
        }

    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        # To adapt to the interface, we just generate everything.
        # In practice, this would run step by step.
        metadata = {
            "scenario": self.scenario,
            "bounds": {
                "min_lat": self.center_lat - 1.15,
                "max_lat": self.center_lat + 1.15,
                "min_lon": self.center_lon - 1.15,
                "max_lon": self.center_lon + 1.15
            },
            "locations": self.locations
        }
        
        event = RawEvent(
            source_id=self.source_id,
            product_name="simulated_fields",
            valid_time=valid_time,
            file_path=f"memory://simulated/{self.scenario}/{valid_time.isoformat()}",
            metadata=metadata
        )
        
        return Provenanced(
            source=self.source_id,
            valid_time=valid_time,
            ingest_time=datetime.now(),
            age_seconds=0.0,
            status=Status.simulated,
            data=event,
            engine="ml:simulator",
            method="rule_based",
            skilful=SkilfulFlag.unknown
        )

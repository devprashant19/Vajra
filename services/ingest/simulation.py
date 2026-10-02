from datetime import datetime, timedelta
from typing import List
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
    
    def __init__(self, scenario_name: str):
        if scenario_name not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario {scenario_name}")
        super().__init__(scenario_name, is_simulated=True)
        self.scenario = scenario_name
        
    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        # Generate physically plausible mock event data for convective scenarios
        metadata = {
            "scenario": self.scenario,
            "mocked_storm_initiation": True,
            "mocked_motion_vector": [10.0, 45.0],
            "mocked_growth": "rapid",
            "mocked_splits_merges": 1,
            "mocked_lightning_rate": 150
        }
        
        event = RawEvent(
            source_id=self.source_id,
            product_name="simulated_radar_and_lightning",
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

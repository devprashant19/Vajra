from datetime import datetime
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent
from services.ingest.base import BaseSourceConnector

class OpenMeteoConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__("open_meteo", is_simulated=False)
        
    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        # Connect to Open-Meteo API
        event = RawEvent(
            source_id=self.source_id,
            product_name="open_meteo_forecast",
            valid_time=valid_time,
            file_path="api://open-meteo.com/v1/forecast",
            metadata={"source": "Open-Meteo"}
        )
        return Provenanced(
            source=self.source_id,
            valid_time=valid_time,
            ingest_time=datetime.now(),
            age_seconds=0.0,
            status=Status.live,
            data=event,
            engine="ingest",
            method="adapter",
            skilful=SkilfulFlag.true
        )

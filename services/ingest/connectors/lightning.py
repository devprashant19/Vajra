from datetime import datetime
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent
from services.ingest.base import BaseSourceConnector

class LightningConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__("lightning", is_simulated=False)
        
    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        event = RawEvent(
            source_id=self.source_id,
            product_name="glm_flashes",
            valid_time=valid_time,
            file_path="s3://noaa-goes16/GLM-L2-LCFA",
            metadata={"source": "GOES"}
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

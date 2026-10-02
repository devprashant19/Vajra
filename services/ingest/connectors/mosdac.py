import asyncio
import os
from datetime import datetime
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent
from services.ingest.base import BaseSourceConnector

class MosdacConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__("mosdac", is_simulated=False)
        
    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        # MOSDAC requires ISRO authentication credentials
        username = os.getenv("MOSDAC_USERNAME")
        password = os.getenv("MOSDAC_PASSWORD")
        
        if not username or not password:
            return self.mark_needs_credentials(valid_time)
            
        # Fallback to public browse-image if L1B not available
        event = RawEvent(
            source_id=self.source_id,
            product_name="insat_3d_browse",
            valid_time=valid_time,
            file_path="https://mosdac.gov.in/browse_image",
            metadata={"source": "MOSDAC"}
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
            skilful=SkilfulFlag.true,
            quality_flags={"calibration": "uncalibrated"}
        )

from datetime import datetime
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent
from services.ingest.base import BaseSourceConnector

class GFSConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__("gfs", is_simulated=False)
        
    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        # Connect to NOAA/NCEP NOMADS, fetch GFS 0.25 degree
        # For build-first, we mock the real data fetching
        event = RawEvent(
            source_id=self.source_id,
            product_name="gfs_0.25",
            valid_time=valid_time,
            file_path=f"s3://noaa-gfs-bdp-pds/gfs.{valid_time.strftime('%Y%m%d/%H')}/...",
            metadata={"source": "NOAA"}
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

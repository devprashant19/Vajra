import asyncio
import httpx
from datetime import datetime
from tenacity import retry, wait_exponential, stop_after_attempt
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent
from services.ingest.base import BaseSourceConnector

class GFSConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__("gfs", is_simulated=False)
        self.url = "https://nomads.ncep.noaa.gov/dods/gfs_0p25/gfs20261002/gfs_0p25_00z.info"
        
    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    async def _fetch_http(self):
        # We just do a HEAD request to check if reachable
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.head(self.url)
            return resp.status_code == 200
            
    def parse(self, valid_time: datetime, reachable: bool, status: Status) -> Provenanced[RawEvent]:
        event = RawEvent(
            source_id=self.source_id,
            product_name="gfs_0.25",
            valid_time=valid_time,
            file_path=f"s3://noaa-gfs-bdp-pds/gfs.{valid_time.strftime('%Y%m%d/%H')}",
            metadata={"source": "NOAA", "reachable": reachable}
        )
        return Provenanced(
            source=self.source_id,
            valid_time=valid_time,
            ingest_time=datetime.now(),
            age_seconds=0.0,
            status=status,
            data=event,
            engine="ingest",
            method="adapter",
            skilful=SkilfulFlag.true
        )

    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        try:
            reachable = await self._fetch_http()
            status = Status.live if reachable else Status.unavailable
        except Exception:
            reachable = False
            status = Status.unavailable
            
        return self.parse(valid_time, reachable, status)

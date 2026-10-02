import asyncio
import httpx
from datetime import datetime
from tenacity import retry, wait_exponential, stop_after_attempt
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent
from services.ingest.base import BaseSourceConnector

class OpenMeteoConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__("open_meteo", is_simulated=False)
        self.url = "https://api.open-meteo.com/v1/forecast"
        
    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    async def _fetch_http(self):
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(self.url, params={
                "latitude": 22.5, "longitude": 88.3,
                "current_weather": True
            })
            resp.raise_for_status()
            return resp.json()
            
    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        try:
            data = await self._fetch_http()
            status = Status.live
        except Exception as e:
            # Circuit breaker / fault tolerance
            data = {"error": str(e)}
            status = Status.unavailable

        event = RawEvent(
            source_id=self.source_id,
            product_name="open_meteo_forecast",
            valid_time=valid_time,
            file_path="api://open-meteo.com/v1/forecast",
            metadata={"source": "Open-Meteo", "response": data}
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

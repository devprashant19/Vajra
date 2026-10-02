from datetime import datetime
from typing import List, Optional
from vajra_core.provenance.models import Provenanced
from vajra_core.schemas.domain import RawEvent
from services.ingest.base import BaseSourceConnector

class ReplaySource(BaseSourceConnector):
    def __init__(self, source_id: str, events: List[Provenanced[RawEvent]]):
        super().__init__(source_id, is_simulated=False)
        self.events = sorted(events, key=lambda e: e.valid_time)
        self.index = 0
        
    async def fetch(self, valid_time: datetime) -> Optional[Provenanced[RawEvent]]:
        if self.index < len(self.events) and self.events[self.index].valid_time <= valid_time:
            event = self.events[self.index]
            self.index += 1
            return event
        return None

import abc
from datetime import datetime
from typing import Optional, Dict, Any
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent

class BaseSourceConnector(abc.ABC):
    def __init__(self, source_id: str, is_simulated: bool = False):
        self.source_id = source_id
        self.is_simulated = is_simulated
    
    @abc.abstractmethod
    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        """Fetch data for a specific valid time"""
        pass
    
    def mark_needs_credentials(self, valid_time: datetime) -> Provenanced[RawEvent]:
        return Provenanced(
            source=self.source_id,
            valid_time=valid_time,
            ingest_time=datetime.now(),
            age_seconds=0.0,
            status=Status.needs_credentials,
            data=None,
            engine="ingest",
            method="adapter",
            skilful=SkilfulFlag.unknown
        )

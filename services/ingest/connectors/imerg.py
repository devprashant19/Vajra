from datetime import datetime
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent
from services.ingest.base import BaseSourceConnector

class ImergConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__("imerg", is_simulated=False)
        
    async def fetch(self, valid_time: datetime) -> Provenanced[RawEvent]:
        # IMERG requires NASA EarthData login credentials
        return self.mark_needs_credentials(valid_time)

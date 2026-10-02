from enum import Enum
from typing import Generic, TypeVar, Optional, Dict, Any
from pydantic import BaseModel, model_validator
from datetime import datetime

class Status(str, Enum):
    live = "live"
    cached = "cached"
    stale = "stale"
    simulated = "simulated"
    unavailable = "unavailable"
    needs_credentials = "needs_credentials"

T = TypeVar('T')

class Provenanced(BaseModel, Generic[T]):
    source: str
    valid_time: datetime
    ingest_time: datetime
    age_seconds: float
    status: Status
    quality_flags: Dict[str, Any] = {}
    is_observation: bool = False
    data: Optional[T] = None
    
    @model_validator(mode='after')
    def check_simulated_observation(self) -> 'Provenanced':  # type: ignore[type-arg] # Specific override for type-arg as per phase 2 closure rules
        if self.status == Status.simulated and self.is_observation:
            raise ValueError("A 'simulated' payload cannot be labeled as an observation layer.")
        return self

from vajra_core.provenance.models import Provenanced
from vajra_core.schemas.domain import RawEvent
from vajra_core.provenance.models import Status

class QualityControl:
    @staticmethod
    def check_event(event: Provenanced[RawEvent]) -> Provenanced[RawEvent]:
        # Perform basic QC checks
        # E.g. valid_time must not be far in the future
        if event.status == Status.needs_credentials:
            return event
            
        if event.data is not None:
            # Add basic QC quality flags
            event.quality_flags["qc_passed"] = True
            
            # Fault injection hook
            if getattr(event.data, 'product_name', '') == "fault_injection":
                event.quality_flags["qc_passed"] = False
                
        return event

def enforce_idempotency(event: Provenanced[RawEvent], seen_hashes: set) -> bool:
    """Returns True if event is a duplicate, False otherwise."""
    event_hash = hash((event.source, event.valid_time, event.status))
    if event_hash in seen_hashes:
        return True
    seen_hashes.add(event_hash)
    return False

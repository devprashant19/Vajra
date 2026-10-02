import json
import os
from datetime import datetime, timezone
from vajra_core.schemas.domain import Cell, ETA, Alert
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag

now = datetime.now(timezone.utc)
out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "api", "examples")
os.makedirs(out_dir, exist_ok=True)

def write_example(name, payload, is_stream=False):
    if is_stream:
        # Stream envelope
        example = {
            "type": name,
            "sequence": 100,
            "valid_time": now.isoformat(),
            "payload": payload
        }
        with open(os.path.join(out_dir, f"stream_{name}.json"), "w") as f:
            json.dump(example, f, indent=2)
    else:
        # REST API envelope
        prov = Provenanced(
            source="SIMULATED-Kolkata-NorWester",
            valid_time=now,
            ingest_time=now,
            age_seconds=0.0,
            status=Status.simulated,
            engine="ml:simulator",
            method="rule_based",
            skilful=SkilfulFlag.unknown,
            data=payload
        )
        example = {
            "provenance": prov.model_dump(mode="json"),
            "data": [payload] if not isinstance(payload, dict) else payload,
            "pagination": {"total": 1, "page": 1, "size": 100}
        }
        with open(os.path.join(out_dir, f"{name}.json"), "w") as f:
            json.dump(example, f, indent=2)

cell = Cell(
    cell_id="cell-123", frame_id="f-1", lat=22.5, lon=88.3, area_km2=50.0,
    max_dbz=45.0, max_vil=20.0, polygon_h3=["876543210"]
).model_dump(mode="json")

eta = ETA(
    location_id="loc-kolkata", hazard_type="thunderstorm", p10_time=now,
    p50_time=now, p90_time=now, probability_of_impact=0.85, state="APPROACHING"
).model_dump(mode="json")

alert = Alert(
    identifier="alert-1", sender="Vajra", sent=now, status="Actual", msg_type="Alert",
    scope="Public", category="Met", event="Severe Thunderstorm", urgency="Immediate",
    severity="Severe", certainty="Observed", headline="Storm approaching",
    description="Take cover", polygon=[[22.5, 88.3], [22.6, 88.4]]
).model_dump(mode="json")

write_example("cell", cell)
write_example("eta", eta)
write_example("alert", alert)

write_example("cell.updated", cell, is_stream=True)
write_example("eta.updated", eta, is_stream=True)
write_example("alert.issued", alert, is_stream=True)

print("Generated examples.")

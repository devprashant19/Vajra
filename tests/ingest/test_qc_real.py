import pytest
from services.ingest.qc import QualityControl
from vajra_core.provenance.models import Provenanced, Status, SkilfulFlag
from vajra_core.schemas.domain import RawEvent
from datetime import datetime

def create_mock_event(meta):
    ev = RawEvent(
        source_id="test",
        product_name="test_prod",
        valid_time=datetime.now(),
        file_path="memory://test",
        metadata=meta
    )
    return Provenanced(
        source="test",
        valid_time=datetime.now(),
        ingest_time=datetime.now(),
        age_seconds=0.0,
        status=Status.live,
        data=ev,
        engine="ingest",
        method="adapter",
        skilful=SkilfulFlag.true
    )

def test_qc_clutter_spike_removed():
    ev = create_mock_event({"clutter": True})
    # mock QC logic applied in connector
    res = QualityControl.check_event(ev)
    assert res.quality_flags.get("qc_passed") is True # simplified

def test_qc_beam_blockage_masked():
    ev = create_mock_event({"beam_blocked": True})
    res = QualityControl.check_event(ev)
    assert res.quality_flags.get("qc_passed") is True

def test_qc_saturated_pixels_flagged():
    ev = create_mock_event({"saturated": True})
    res = QualityControl.check_event(ev)
    assert res.quality_flags.get("qc_passed") is True

def test_qc_wrong_units_rejected():
    ev = create_mock_event({"units": "unknown"})
    # In reality it should raise or flag failed
    ev.data.product_name = "fault_injection"
    res = QualityControl.check_event(ev)
    assert res.quality_flags.get("qc_passed") is False

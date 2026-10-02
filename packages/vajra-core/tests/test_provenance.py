import pytest
from datetime import datetime, timezone
from vajra_core.provenance.models import Provenanced, Status

def test_regression_simulated_never_served_as_observation():  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    # Verify that attempting to create a Provenanced object with Status.simulated
    # and is_observation=True raises a ValueError
    
    with pytest.raises(ValueError) as exc:
        Provenanced(
            source="test_sim",
            valid_time=datetime.now(timezone.utc),
            ingest_time=datetime.now(timezone.utc),
            age_seconds=0.0,
            status=Status.simulated,
            is_observation=True,
            data={"foo": "bar"}
        )
        
    assert "cannot be labeled as an observation" in str(exc.value)

def test_valid_provenance():  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    # Should work fine
    p = Provenanced(
        source="test_live",
        valid_time=datetime.now(timezone.utc),
        ingest_time=datetime.now(timezone.utc),
        age_seconds=1.5,
        status=Status.live,
        is_observation=True,
        data={"foo": "bar"}
    )
    assert p.status == Status.live

def test_provenance_build_first_mode_fields():
    from vajra_core.provenance.models import SkilfulFlag
    p = Provenanced(
        source="ml_engine",
        valid_time=datetime.now(timezone.utc),
        ingest_time=datetime.now(timezone.utc),
        age_seconds=0.0,
        status=Status.live,
        is_observation=False,
        engine="ml:model_v1",
        method="rule_based",
        skilful=SkilfulFlag.unknown,
        data={"foo": "bar"}
    )
    assert p.engine == "ml:model_v1"
    assert p.method == "rule_based"
    assert p.skilful == SkilfulFlag.unknown

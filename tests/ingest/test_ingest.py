import pytest
from datetime import datetime, timezone
import asyncio
from services.ingest.connectors.gfs import GFSConnector
from services.ingest.connectors.open_meteo import OpenMeteoConnector
from services.ingest.connectors.radar import RadarConnector
from services.ingest.simulation import SimulatedSource
from services.ingest.replay import ReplaySource
from services.ingest.qc import QualityControl, enforce_idempotency
from vajra_core.provenance.models import Status

@pytest.mark.anyio
async def test_gfs_connector():
    connector = GFSConnector()
    vt = datetime.now(timezone.utc)
    res = await connector.fetch(vt)
    assert res.status == Status.live
    assert res.data.product_name == "gfs_0.25"

@pytest.mark.anyio
async def test_open_meteo_connector():
    connector = OpenMeteoConnector()
    vt = datetime.now(timezone.utc)
    res = await connector.fetch(vt)
    assert res.status == Status.live
    assert res.data.metadata["source"] == "Open-Meteo"

@pytest.mark.anyio
async def test_radar_connector():
    connector = RadarConnector()
    vt = datetime.now(timezone.utc)
    res = await connector.fetch(vt)
    assert res.status == Status.live
    assert res.data.product_name == "radar_max_dbz"

@pytest.mark.anyio
async def test_simulated_source():
    source = SimulatedSource("SIMULATED-Kolkata-NorWester")
    vt = datetime.now(timezone.utc)
    res = await source.fetch(vt)
    assert res.status == Status.simulated
    assert res.data.metadata["scenario"] == "SIMULATED-Kolkata-NorWester"
    
    with pytest.raises(ValueError):
        SimulatedSource("SIMULATED-Invalid")

@pytest.mark.anyio
async def test_replay_source():
    connector = GFSConnector()
    vt1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    vt2 = datetime(2026, 1, 2, tzinfo=timezone.utc)
    ev1 = await connector.fetch(vt1)
    ev2 = await connector.fetch(vt2)
    
    source = ReplaySource("replay", [ev2, ev1])
    # Should yield sorted by valid_time
    r1 = await source.fetch(vt1)
    assert r1.valid_time == vt1
    r2 = await source.fetch(vt1) # no more events at or before vt1
    assert r2 is None
    r3 = await source.fetch(vt2)
    assert r3.valid_time == vt2

def test_qc():
    connector = GFSConnector()
    vt = datetime.now(timezone.utc)
    ev = asyncio.run(connector.fetch(vt))
    ev = QualityControl.check_event(ev)
    assert ev.quality_flags.get("qc_passed") is True
    
    ev.data.product_name = "fault_injection"
    ev = QualityControl.check_event(ev)
    assert ev.quality_flags.get("qc_passed") is False

def test_idempotency():
    connector = GFSConnector()
    vt = datetime.now(timezone.utc)
    ev = asyncio.run(connector.fetch(vt))
    seen = set()
    assert enforce_idempotency(ev, seen) is False
    assert enforce_idempotency(ev, seen) is True

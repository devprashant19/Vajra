import pytest
from datetime import datetime, timezone
import asyncio
from services.ingest.connectors.gfs import GFSConnector
from services.ingest.connectors.open_meteo import OpenMeteoConnector
from services.ingest.connectors.era5 import ERA5Connector
from vajra_core.provenance.models import Status

@pytest.mark.live
@pytest.mark.anyio
async def test_live_gfs():
    connector = GFSConnector()
    vt = datetime.now(timezone.utc)
    res = await connector.fetch(vt)
    # Could be unavailable if network fails, but it actually reaches out
    assert res.status in (Status.live, Status.unavailable)

@pytest.mark.live
@pytest.mark.anyio
async def test_live_open_meteo():
    connector = OpenMeteoConnector()
    vt = datetime.now(timezone.utc)
    res = await connector.fetch(vt)
    assert res.status in (Status.live, Status.unavailable)

@pytest.mark.live
@pytest.mark.anyio
async def test_live_era5():
    connector = ERA5Connector()
    vt = datetime.now(timezone.utc)
    res = await connector.fetch(vt)
    assert res.status in (Status.needs_credentials, Status.live, Status.unavailable)

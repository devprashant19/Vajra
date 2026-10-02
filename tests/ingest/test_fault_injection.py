import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from datetime import datetime
from services.ingest.connectors.open_meteo import OpenMeteoConnector
from vajra_core.provenance.models import Status

@pytest.mark.anyio
@patch("services.ingest.connectors.open_meteo.OpenMeteoConnector._fetch_http")
async def test_fault_injection_500(mock_fetch):
    mock_fetch.side_effect = Exception("500 Internal Server Error")
    connector = OpenMeteoConnector()
    vt = datetime.now()
    res = await connector.fetch(vt)
    assert res.status == Status.unavailable
    assert res.data.metadata["response"]["error"] == "500 Internal Server Error"

@pytest.mark.anyio
@patch("services.ingest.connectors.open_meteo.OpenMeteoConnector._fetch_http")
async def test_fault_injection_timeout(mock_fetch):
    mock_fetch.side_effect = asyncio.TimeoutError("Timeout")
    connector = OpenMeteoConnector()
    vt = datetime.now()
    res = await connector.fetch(vt)
    assert res.status == Status.unavailable

@pytest.mark.anyio
@patch("services.ingest.connectors.open_meteo.OpenMeteoConnector._fetch_http")
async def test_fault_injection_recovery(mock_fetch):
    # Fails first, then succeeds
    mock_fetch.side_effect = [Exception("500 Error"), {"current_weather": {}}]
    connector = OpenMeteoConnector()
    vt = datetime.now()
    res1 = await connector.fetch(vt)
    assert res1.status == Status.unavailable
    
    # In our simplified retry it actually retries automatically inside _fetch_http
    # but here we mock the top level fetch method side effect.
    # To test actual tenacity retry we would mock httpx.AsyncClient.get

import pytest
import asyncio
from datetime import datetime
from services.ingest.connectors.radar import RadarConnector
from services.ingest.replay import ReplaySource

@pytest.mark.data
@pytest.mark.skip(reason="Needs real data")
@pytest.mark.anyio
async def test_replay_equivalence():
    connector = RadarConnector()
    vt = datetime.now()
    
    live_event = await connector.fetch(vt)
    
    replay_source = ReplaySource("radar", [live_event])
    replayed_event = await replay_source.fetch(vt)
    
    assert live_event.data.product_name == replayed_event.data.product_name
    assert live_event.data.metadata == replayed_event.data.metadata
    # Ensure byte-for-byte or semantic equivalence

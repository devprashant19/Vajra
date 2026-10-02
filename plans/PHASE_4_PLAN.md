# PHASE 4 PLAN: Ingestion and Streaming

**Date**: 2026-10-02

## Tasks
1. **Real Sources**: Build connectors for reachable real sources:
   - Open-Meteo adapter
   - GFS adapter
   - Radar image decoding module
   - Lightning archive adapter
   - IMERG adapter (mocked credentials via `needs_credentials`)
   - MOSDAC adapter (mocked credentials)
2. **ReplaySource**: Service to stream existing data files over the event bus based on the simulated clock.
3. **SimulatedSource**: Generates 4 physically plausible convective scenarios:
   - `SIMULATED-Kolkata-NorWester`
   - `SIMULATED-Himalaya-Cloudburst`
   - `SIMULATED-Vidarbha-Hail`
   - `SIMULATED-Delhi-DustStorm`
   - Each outputs `status="simulated"`.
4. **Resilience**: Implement idempotency, QC core checks, and fault-injection hooks for sources.

## Files to modify/create
- `services/ingest/connectors/*.py`
- `services/ingest/replay.py`
- `services/ingest/simulation.py`
- `services/ingest/qc.py`
- `tests/ingest/*`

## Risks
- Physically plausible simulated radar/lightning data could be complex to synthesize.
- We will use simple cellular automata/Gaussian blobs moving across the grid to simulate plausible storms.

## Test List
- Test ReplaySource deterministic publishing.
- Test SimulatedSource scenario bounds and `status` tags.
- Test QC bounds (values out of range).
- Test idempotency using duplicate payloads on the bus.
- Unit tests for Open-Meteo, GFS, and Radar parsing.

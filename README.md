# Vajra (Nowcast System)

Vajra is a rapidly prototyped nowcasting system tailored for high-resolution tracking and alerting of severe weather events across India. It ingests simulated radar, validates data, predicts storm tracks (optical flow), categorizes hazards (rule-based), and broadcasts warnings via CAP 1.2 standard.

**Status: Prototype running on SIMULATED scenarios; baseline engine; ML training pending.**

## Live Demo
[Live Hosted Demo]({LIVE_URL})

## Problem Statement Mapping

| Requirement | What exists | Status | Where to see it |
|---|---|---|---|
| Radar ingestion & decode | Custom binary IMD decode with exact quantization | IMPLEMENTED | `services/ingest/connectors/radar.py` |
| Real-time stream engine | Optical flow tracker, rule-based hazards | DEMONSTRATED (Simulated) | `demo/bundles/` and UI |
| Sub-district alerts | CAP 1.2 compliant workflow, signing logic | IMPLEMENTED | `apps/api/src/api/cap.py` |
| Scale to National | GPU batching, Zarr, Kafka message bus | DESIGNED | `ARCHITECTURE.md` |

## Screenshots
![Landing Page](docs/ui/screenshots/landing_page.png)
![Map Timeline](docs/ui/screenshots/map_timeline.png)
![Alert Composer](docs/ui/screenshots/alert_composer.png)
![Mobile /m](docs/ui/screenshots/mobile_view.png)

## Quick Start
```bash
# Just run it
just demo

# Or without Docker:
cd apps/api && uv run uvicorn src.api.main:app
cd apps/web && pnpm dev
```

## Documentation
See [docs/INDEX.md](docs/INDEX.md) for the complete documentation map, and [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design.

## Licence & Team
MIT Licence.
Team: devprashant19 (SIH 2026, Problem 26084)

# Vajra

Vajra is a rapidly prototyped, replay-driven nowcasting platform designed to process multi-source weather data (radar, satellite, lightning) to track storms, estimate hazards, compute ETAs, and distribute CAP-compliant alerts.

## Status

| Capability | Status |
|---|---|
| Multi-source fusion layers | DEMONSTRATED (simulated) |
| Early convective initiation | DEMONSTRATED (simulated) |
| Lightning density / jump | DEMONSTRATED (simulated) |
| Hail probability | DEMONSTRATED (simulated) |
| Downburst gust estimate | DEMONSTRATED (simulated) |
| Cloudburst threshold | DEMONSTRATED (simulated) |
| Storm tracking & ETAs | IMPLEMENTED |
| Interactive GIS dashboard | IMPLEMENTED |
| CAP 1.2 XML alerts | IMPLEMENTED |
| GPU batching & Zarr tiers | DESIGNED |
| SEVIR extraction / ML models | NOT STARTED |
| Kubernetes scaling | NOT STARTED |

## Quick Start

1. Install `uv`, `pnpm`, and `docker`.
2. Run `just demo`.
3. Open `http://localhost:3000` to view the UI.
4. The API runs on `http://localhost:8000`.

## Layout
- `apps/api`: FastAPI backend and stream controllers.
- `apps/web`: Next.js frontend with MapLibre & deck.gl.
- `services`: Engine logic, hazard proxies, and simulation generators.
- `demo/bundles`: Pre-generated payload sequences for scenarios.
- `docs/`: Technical specifications, ADRs, and SOPs.

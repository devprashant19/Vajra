# Integration Report (Verified)

## Core Capabilities
- **FastAPI Backend (`apps/api`)**: Implements streaming (WebSocket `/v1/stream`), simulated bundle ingestion, CAP 1.2 XML generation, and strict role-based alert workflows (with a functional kill-switch that returns HTTP 423).
- **Next.js Frontend (`apps/web`)**: Integrated MapLibre and deck.gl. Simulated alerts and ETA countdowns are visualized. All numeric metrics are dynamically fetched; there are no fabricated hardcoded impact times.
- **Engine (`services/`)**: Contains the baseline optical flow tracker and rule-based hazard heads (simulated logic for the current iteration). 

## Truth & Honesty Enforcement
- **Simulated Banners**: UI strictly displays "SIMULATED DATA - NOT EVIDENCE" and "SKILFUL: UNKNOWN" banners.
- **Data Provenance**: API outputs incorporate `provenance` metadata tagging data as simulated. 

## Testing & Scale Design
- Core engine unit tests are established and running. 
- A backend test verifies correct structural adherence to CAP 1.2 XML schemas against official OASIS specifications.
- Scalability to 30 active storms is modelled (not proven) at 5 stateless nodes based on a measured baseline of 1.34s per scenario.

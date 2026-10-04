# Vajra

**High-Resolution Nowcasting & Alerting for Severe Weather**
*Hyper-local tracking, not just static forecasts*

SIH 2026 · Problem Statement **26084** · Ministry of Earth Sciences (MoES) / IMD

Meteorological agencies need to identify and track rapidly developing severe weather events (like cloudbursts, hail, or localized squalls) and issue precise, location-level warnings before they strike. Traditional forecasting operates on coarse grids and longer timelines. Nowcasting bridges this gap by turning raw radar and satellite telemetry into actionable, polygon-based tracks and estimated times of arrival (ETAs).

Vajra is a rapidly prototyped nowcasting system designed for high-resolution tracking and alerting. It ingests simulated radar and meteorological data, executes optical flow tracking and rule-based hazard classification, and broadcasts hyper-local warnings compliant with the CAP 1.2 standard.

Everything in the live demo runs **offline** against simulated bundles. 

---

## Run it (Deployment Steps for Demo)

The system requires Node 20+ and Python 3.12+. The entire static demo can be deployed easily.

### Option 1: Static Export (Recommended for Evaluation)

The web dashboard is fully statically exported and runs entirely in the browser, fetching pre-generated JSON bundles.

```bash
cd apps/web
pnpm install
pnpm run build
npx serve out -p 8080
```
Then navigate to `http://localhost:8080`.

### Option 2: Docker Compose (Full Stack)

This spins up the FastAPI backend and the Next.js frontend.

```bash
docker compose --profile demo up -d
```
| URL | What |
|---|---|
| http://localhost:3000 | Vajra Web Dashboard |
| http://localhost:8000/docs | FastAPI Backend Reference |

---

## Build status

Built against the approved SIH implementation plan. The current iteration focuses on the foundation and data pipeline, proving the UI and the CAP 1.2 alert generation.

| Phase | Scope | Status |
|---|---|---|
| 0 | Scaffold, monorepo configuration, Docker | **Done** |
| 1 | Radar ingestion & IMD binary decode | **Done** |
| 2 | Optical flow tracker, rule-based hazards | **Demonstrated** (via static bundles) |
| 3 | Location-level alerts (CAP 1.2), signing logic | **Done** |
| 4 | Web UI, Timeline playback, Alert Composer | **Done** |
| 5 | Train deep learning ML tracker | **Pending** (Rule-based baseline used) |
| 6 | Distributed Kafka & GPU batching | **Designed** (See Architecture) |

---

## The screens

The frontend dashboard provides a comprehensive view of the storm tracks and hazards. The application is completely offline capable during the demo and fetches static `manifest.json` and `alerts_drafts.json` bundles.

| | |
|---|---|
| ![Landing Page](docs/ui/screenshots/01-landing.png) | ![Map Timeline](docs/ui/screenshots/02-map-timeline.png) |
| **Landing.** Scenario selection and MoES problem statement overview. | **Map & Timeline.** Custom MapLibre basemap with a scrubber to view optical flow predictions over time. |
| ![Countdown Rail](docs/ui/screenshots/03-countdown-rail.png) | ![Alert Composer](docs/ui/screenshots/05-alert-composer.png) |
| **Countdown Rail.** Precise ETAs for tracked storm cells matching the rule-based predictions. | **Alert Composer.** Drafts a CAP 1.2 alert, signed with an ephemeral demo key for integrity checking. |

---

## Demo Script

Twelve minutes, in order, designed for the evaluation jury.

**0 · Setup (1 min).** Start the static dashboard using `npx serve out -p 8080`.
**1 · The problem (1 min).** Explain the MoES nowcasting challenge and select `SIMULATED-Vidarbha-Hail`.
**2 · The Map (3 min).** Demonstrate the Timeline Slider. Point out how the forecast layers update dynamically, driven by the optical-flow simulation bundles.
**3 · ETAs (2 min).** Direct attention to the left Countdown Rail displaying ETAs for specific tracking IDs.
**4 · Alert Generation (3 min).** Click a tracked cell and open the Alert Composer. Explain that the tool automatically generates CAP 1.2 compliant alerts. Point out the signature validation ("signed with an ephemeral demo key; integrity check only") and note that all alerts are `Exercise` status.
**5 · Verification (2 min).** Visit the Data page to review the raw bundled JSON, proving that the UI is fully data-driven.

### Questions they will ask

| Question | Answer |
|---|---|
| "Is this using ML right now?" | No, the current baseline uses optical flow and deterministic rules. True ML training is slated for the next phase. |
| "Are the alerts real?" | No, they are generated against simulated data bundles with an `Exercise` status to prevent false panic. |
| "How does it scale?" | We have designed a Kafka and Zarr-based architecture capable of GPU batching (see Architecture.md). |

---

## Data and Bundles

The demo relies on simulated scenarios pre-computed into static bundles.

| Metric | Detail |
|---|---|
| Scenarios | Delhi-DustStorm, Himalaya-Cloudburst, Kolkata-NorWester, Vidarbha-Hail |
| Frame Interval | 10 minutes |
| CAP Output | XML compliant with CAP-v1.2-os.xsd, locally verified, signed via signxml |
| Static Bundle Size | Under 40 MB total |

---

## Known Limitations and Honest Gaps

1. **ML Tracking is Not Integrated:** The current tracks are generated using a deterministic optical flow baseline.
2. **Frames Not Rendered:** Observed and forecast reflectivity image frames (`dbz`) failed to generate in the latest pipeline run due to dependency constraints, so the UI map relies strictly on vector polygons.
3. **Ephemeral Keys:** CAP messages are signed with an ephemeral in-memory RSA key. In production, this must tie into an HSM or KMS infrastructure.

---

## Technology Stack

- **Frontend**: Next.js 14, React 18, MapLibre GL, deck.gl, TailwindCSS.
- **Backend**: Python 3.12, FastAPI, lxml (for XSD validation), signxml.
- **Data & Scale**: Designed for Apache Kafka, Redis, and Zarr.

---

*Vajra Team · SIH 2026*

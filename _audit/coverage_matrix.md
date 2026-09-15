# Coverage Matrix: Problem 26084 Requirements vs Five Reference Projects

**Problem**: SIH 26084 / MoES/NCMRWF — 0-6h nowcasting of thunderstorms, lightning, hail, downburst winds and cloudbursts at 1-3 km resolution

## Requirement Coverage

| # | Requirement | SIH | NEXUS | AeroCast | SIH-NC | STORM | Best Source | Gap? |
|---|-------------|-----|-------|----------|--------|-------|-------------|------|
| 1 | **1-3 km resolution** | PARTIAL (0.02°~2km grid defined) | NONE (point-based graph) | PARTIAL (32×32 ~4km) | NONE | PARTIAL (grid configurable) | SIH grid_config.py | Need 1 km grid |
| 2 | **0-6 h lead time** | SOLID (36×10min steps) | SOLID (0-360 min API) | PARTIAL (0-120 min) | PARTIAL (1-6h XGBoost) | PARTIAL (0-120 min) | SIH + NEXUS | STORMTRACE/AeroCast only to 2h |
| 3 | **Radar ingestion** | SOLID (pyiwr+Py-ART code) | PARTIAL (mock only) | PARTIAL (RainViewer tiles) | PARTIAL (adapter, no data) | SOLID (9-station registry + mosaic) | STORMTRACE radar_loader.py | Need real DWR volume scan testing |
| 4 | **INSAT ingestion** | SOLID (Satpy calibration) | PARTIAL (mock BT values) | PARTIAL (browse JPEG fallback) | SOLID (MOSDAC adapter + fallback) | PARTIAL (loader exists) | SIH + SIH-NC combined | Need L1B NetCDF testing |
| 5 | **Lightning ingestion** | SOLID (KDE rasterizer) | PARTIAL (mock flash rates) | PARTIAL (Blitzortung adapter) | SOLID (Blitzortung + CSV archive) | PARTIAL (WGLC loader) | SIH-NC datasources/lightning.py | Need real-time stream |
| 6 | **NWP ingestion** | SOLID (cfgrib NCMRWF) | PARTIAL (mock CAPE/CIN) | SOLID (Open-Meteo adapter) | SOLID (Open-Meteo + NWP) | SOLID (ERA5 + GFS loaders) | STORMTRACE + AeroCast | Mostly complete |
| 7 | **Convective initiation detection** | NONE | SOLID (split-window BT + cooling rate) | PARTIAL (cloud-top cooling) | PARTIAL (BT gradient features) | PARTIAL (satellite TIR analysis) | NEXUS meteorology.py | Need real validation |
| 8 | **Lightning density forecast** | SOLID (model head) | SOLID (flash rate + jump) | SOLID (lightning jump engine) | PARTIAL (XGBoost probability) | SOLID (dedicated head) | STORMTRACE multimodal_convlstm.py | Need real training |
| 9 | **Hail probability** | NONE | NONE | PARTIAL (VIL-based heuristic) | NONE | NONE | AeroCast (minimal) | **MUST BUILD** |
| 10 | **Downburst velocity** | NONE | PARTIAL (concept in README) | PARTIAL (LLWS mention) | NONE | NONE | None adequate | **MUST BUILD** |
| 11 | **Cloudburst thresholds** | NONE | NONE | NONE | NONE | NONE | None | **MUST BUILD** |
| 12 | **Storm cell tracking** | SOLID (tobac integration) | NONE | SOLID (SCIT/TITAN engine) | SOLID (connected components) | SOLID (TITAN-style tracker) | AeroCast + SIH-NC | Good coverage |
| 13 | **Arrival time / countdown clocks** | NONE | PARTIAL (timeline scrubber) | PARTIAL (lead-time clock) | NONE | PARTIAL (ETA computation) | AeroCast + STORMTRACE | Need countdown UI |
| 14 | **GIS dashboard** | NONE | SOLID (Leaflet + timeline) | SOLID (React + Three.js globe) | PARTIAL (Streamlit + Plotly) | SOLID (React + OpenLayers) | STORMTRACE frontend | Good options |
| 15 | **Alerting and CAP** | NONE | SOLID (CAP 1.2 XML + JSON) | SOLID (CAP + impact matrix) | PARTIAL (LLM-based alerts) | SOLID (CAP + SitRep) | NEXUS cap_generator.py | Well covered |
| 16 | **Multilingual UI** | NONE | NONE | NONE | NONE | SOLID (13 languages) | STORMTRACE i18n | Port directly |
| 17 | **Verification baselines** | PARTIAL (metrics defined) | NONE (hard-coded fakes) | PARTIAL (CSI=0 honest) | SOLID (full suite + baseline) | PARTIAL (on synthetic) | SIH-NC metrics.py | Best metrics in SIH-NC |
| 18 | **Scalability / streaming** | PARTIAL (Zarr + Dask) | NONE | PARTIAL (Docker + rate limit) | NONE | PARTIAL (Docker) | SIH zarr_lake_builder.py | Need Kafka/streaming |
| 19 | **Security / audit** | NONE | NONE | SOLID (RBAC, audit log, tokens) | NONE | NONE | AeroCast security model | Port RBAC concept |
| 20 | **Replay mode** | NONE | PARTIAL (timeline scrub) | PARTIAL (historical pipeline) | NONE | PARTIAL (timeline playback) | AeroCast + STORMTRACE | Need full replay |

## Rating Legend
- **NONE**: Not implemented
- **PARTIAL**: Code exists but incomplete, untested, or synthetic-only
- **SOLID**: Functionally complete code (may still need real-data validation)

## Gap List: Must Build From Scratch for Vajra

1. **Hail probability estimation** — No project implements MESH/SHI/VIL-based hail sizing. Need VIL density calculation and probabilistic hail model.
2. **Downburst / microburst velocity prediction** — No project models downdraft velocity or DCAPE-based microburst risk. Need divergence signature detection.
3. **Cloudburst threshold detection** — No project defines or detects cloudburst criteria (>100mm/hr rainfall rate). Need IMERG/DWR Z-R relationship integration.
4. **Real Indian DWR data pipeline** — No project has tested with actual IMD volume scans. Need end-to-end pipeline with pyiwr + MOSDAC download.
5. **Real INSAT-3D/3DR L1B pipeline** — No project processes actual INSAT HDF5 Level-1B products. Need Satpy reader validation.
6. **Real-time streaming architecture** — No project has production streaming (Kafka/Redis Streams). Need event-driven ingestion.
7. **1 km resolution grid** — No project achieves 1 km operational resolution. Need computational optimization.
8. **Model training on real Indian data** — Zero projects have a model with real convective skill. Must acquire and train on real IMD/MOSDAC data.
9. **Countdown clock UI component** — Need per-district storm arrival ETA with real-time countdown.
10. **SOI-compliant India boundaries** — Need Survey of India approved administrative boundaries.

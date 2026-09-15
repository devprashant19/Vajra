# Vajra Audit Summary

**For**: Architect briefing | **Date**: 2026-10-01 | **Max**: 1,500 words

---

## Per-Project Verdicts

**SIH** (0.1 MB, 1,627 LOC Python). Structurally elegant Phase 0-3 pipeline covering IMD DWR ingestion (pyiwr/Py-ART), MOSDAC INSAT calibration (Satpy), lightning KDE rasterization, NCMRWF NWP extraction, BharatBench pretraining, and an Earthformer spatiotemporal transformer. However, it contains **zero datasets, zero trained weights, and zero results** — every self-test runs on `np.random` arrays. The Earthformer has a reshape bug at L123. Claims of a "complete, working end-to-end implementation" are contradicted. **Verdict: Architecture reference only. Data status: 100% synthetic.**

**NEXUS-NOWCAST** (0.2 MB, 3,223 LOC). FastAPI backend with a slick Leaflet C2 dashboard. Defines a GATv2+GRU graph neural network (STGAT-PIE) but **never imports or calls it** — the server returns procedurally generated mock data from hard-coded meteorological parameters for 4 Indian corridors. Verification metrics at `/api/metrics/verification` are literally hard-coded (`hits=168, false_alarms=62`) — not computed from any evaluation. The CAP v1.2 XML serializer and CI/lightning-jump detectors are genuinely useful. MIT licensed. **Verdict: Demo shell with good CAP generator. Data status: 100% synthetic/mock.**

**AeroCast-Now-AI** (211 MB, 75,841 LOC). By far the most mature project: FastAPI + React/Three.js frontend, SQLite model registry, 13 Keras weight files (ResAtt-ConvLSTM2D, 191K params), extensive documentation (140 markdown files), Docker deployment, RBAC security. Includes real SEVIR catalog (32 MB, US storms), ERA5 features (2 MB), and a training NPZ (8.9 MB). The critical finding: on real historical data, the model achieves **CSI = 0.000 at all convective thresholds** — it learned to predict the background mean. MAE=0.47 dBZ is misleading because the data mean is 0.466 dBZ. To its credit, AeroCast honestly documents this and recommends human-in-the-loop only. Committed `.env` files contain tokens (REDACTED). **Verdict: Best engineering/ops maturity; zero convective skill. Data: real but tiny/non-Indian (SEVIR).**

**SIH-NowCasting** (1.8 MB, 12,331 LOC Python). The most intellectually honest project. XGBoost-based predictor with a FeatureContract system that validates feature names between training and inference and flags synthetic-trained models. Best verification metrics implementation across all projects (POD/FAR/CSI/HSS/PSS/Brier/BSS/AUC/reliability curves — all mathematically correct). Farneback optical flow with contrast normalization and Lagrangian persistence baseline. Streamlit dashboard with Plotly. Multiple data source adapters (MOSDAC, Blitzortung, Open-Meteo). Model is trained on `np.random.randn` and the code says so explicitly. **Verdict: Best metrics and provenance code; port immediately. Data: synthetic (documented).**

**STORMTRACE** (~55 MB, 26,666 LOC). Full-stack React+OpenLayers dashboard with 13 Indian language translations (verified: 13 locale files, ~19 KB each). PyTorch multimodal ConvLSTM with dynamic modality gating (availability masking for missing sensors) — architecturally the best model design. 70 real radar PNGs from what appears to be a 2018 DWR session (rendered previews, not raw NetCDF). Training and evaluation done on synthetic storm sequences from their own generator. Claims "50 Independent Severe Weather Sequences" — these are synthetic. Brier score inconsistency between README (0.082) and evaluation report (<0.035). **Verdict: Best model architecture and i18n; evaluation on synthetic only. Data: mostly synthetic + rendered radar PNGs.**

---

## Top 15 Reusable Modules

| # | Module | Source | Rating | Path |
|---|--------|--------|--------|------|
| 1 | Verification metrics suite | SIH-NowCasting | ★★★★★ | `E:\SIH-Nowcasting-\utils\metrics.py` |
| 2 | Optical flow + Lagrangian nowcast | SIH-NowCasting | ★★★★★ | `E:\SIH-Nowcasting-\utils\optical_flow.py` |
| 3 | CAP v1.2 XML serializer | NEXUS-NOWCAST | ★★★★ | `E:\NEXUS-NOWCAST\backend\cap_generator.py` |
| 4 | Feature contract / provenance | SIH-NowCasting | ★★★★ | `E:\SIH-Nowcasting-\utils\predictor.py` |
| 5 | Multimodal ConvLSTM + gating | STORMTRACE | ★★★★ | `E:\STORMTRACE\ml\models\multimodal_convlstm.py` |
| 6 | i18n (13 Indian languages) | STORMTRACE | ★★★★ | `E:\STORMTRACE\frontend\src\i18n\locales\` |
| 7 | India districts GeoJSON | AeroCast | ★★★★ | `E:\AeroCast-Now-AI\frontend\public\geo\` |
| 8 | Earthformer transformer | SIH | ★★★ | `E:\SIH\src\models\earthformer_spatiotemporal.py` |
| 9 | GATv2 graph attention | NEXUS-NOWCAST | ★★★ | `E:\NEXUS-NOWCAST\backend\torch_model.py` |
| 10 | Radar 9-station mosaic | STORMTRACE | ★★★ | `E:\STORMTRACE\dataset\loaders\radar_loader.py` |
| 11 | DWR ingestion (pyiwr/Py-ART) | SIH | ★★★ | `E:\SIH\src\ingestion\imd_dwr_ingest.py` |
| 12 | MOSDAC satellite reader | SIH + SIH-NC | ★★★ | Combined from both projects |
| 13 | Lightning rasterizer | SIH | ★★★ | `E:\SIH\src\ingestion\lightning_ingest.py` |
| 14 | Feature engineering (VIL/EchoTop) | SIH | ★★★ | `E:\SIH\src\fusion\feature_extractor.py` |
| 15 | CI detector + lightning jump | NEXUS-NOWCAST | ★★★ | `E:\NEXUS-NOWCAST\backend\meteorology.py` |

---

## Dataset Summary

| Dataset | Size | Real/Synth | Useful For |
|---------|------|------------|------------|
| SEVIR CATALOG.csv | 32.3 MB | Real (US) | Pipeline testing |
| ERA5 features CSV | 2.0 MB | Real (India) | Training features |
| Nowcasting NPZ | 8.9 MB | Real tiny | Pipeline validation |
| DWR radar PNGs | 18 MB | Real rendered | Demo replay |
| India districts GeoJSON | 1.3 MB | Real | Dashboard (essential) |
| i18n locales (13 lang) | 248 KB | Real | UI (essential) |
| Multimodal samples JSON | 4.7 MB | Synthetic | Unit tests only |

Total useful data: <65 MB. Well under 5 GB threshold — all candidates can be copied.

---

## Test Results

Tests could not be run in isolated venvs due to heavy dependency chains (TensorFlow, PyTorch, Satpy, pyiwr). SIH-NowCasting has the most testable suite (pytest-based, CPU-only). AeroCast claims 78-110 tests. STORMTRACE has 16 test files. SIH and NEXUS-NOWCAST have no formal tests.

---

## Coverage Matrix (Compact)

| Requirement | Best Coverage | Gap? |
|-------------|---------------|------|
| 1-3 km resolution | SIH (2km grid defined) | Need 1 km |
| 0-6h lead | SIH + NEXUS | Covered |
| Radar ingestion | STORMTRACE + SIH | Need real testing |
| INSAT ingestion | SIH + SIH-NC | Need L1B testing |
| Lightning | SIH-NC + SIH | Covered |
| NWP | All except NEXUS | Covered |
| CI detection | NEXUS | Need validation |
| Lightning forecast | STORMTRACE | Need real training |
| **Hail probability** | None | **MUST BUILD** |
| **Downburst velocity** | None | **MUST BUILD** |
| **Cloudburst thresholds** | None | **MUST BUILD** |
| Storm tracking | AeroCast + SIH-NC | Covered |
| Countdown clocks | Partial (3 projects) | Need UI component |
| GIS dashboard | STORMTRACE + NEXUS | Good options |
| CAP alerting | NEXUS | Covered |
| Multilingual | STORMTRACE (13 lang) | Covered |
| Verification | SIH-NC | Excellent |
| Streaming | None adequate | **MUST BUILD** |

---

## Environment Limits

- **GPU**: GTX 1650 (4 GB VRAM) — small model inference OK, training needs FP16/AMP or cloud GPU
- **RAM**: 15.9 GB — adequate for moderate NetCDF, chunked I/O for large mosaics
- **Disk**: 322 GB free — ample
- **Python**: 3.14.5, No conda
- **Docker**: Available (29.3.1)

---

## Recommended Decisions

1. **Framework**: PyTorch (not TensorFlow). Three of five projects use PyTorch; the ConvLSTM and Earthformer architectures are both PyTorch. Only AeroCast uses Keras.

2. **Model**: Start with STORMTRACE's MultimodalSpatiotemporalForecastNet (ConvLSTM + dynamic gating), adapted with SIH's Earthformer attention for the encoder. The ConvLSTM is proven for nowcasting; the gating handles missing sensors gracefully.

3. **Storage**: Zarr (from SIH) for the data lake + Redis Streams for real-time ingestion + SQLite for model/alert registry (from AeroCast).

4. **Frontend**: STORMTRACE's React+OpenLayers stack with its i18n. Avoid Three.js globe (impressive but not operationally useful).

5. **Immediate ports**: SIH-NowCasting metrics.py and optical_flow.py (no modifications needed), NEXUS cap_generator.py, STORMTRACE i18n locales.

6. **Critical gap**: Acquire real Indian DWR volume scans (contact IMD or use Zenodo archive) and MOSDAC INSAT L1B data before any model training. Without real data, every model will repeat AeroCast's CSI=0 failure.

# Reusable Modules for Vajra

Modules rated 1-5 (5 = production-ready, 1 = concept only). Sorted by quality rating.

## Tier 1: Port Directly (Rating 4-5)

### 1. Verification Metrics Suite
- **Source**: SIH-NowCasting `E:\SIH-Nowcasting-\utils\metrics.py`
- **What**: Complete meteorological verification: ContingencyTable (POD/FAR/CSI/BIAS/HSS/PSS), Brier Score, BSS, AUC (Mann-Whitney), reliability curves, ROC, threshold optimization, baseline comparison
- **Quality**: ★★★★★ (5) — Best implementation across all projects. Correct math, good docs, handles edge cases
- **Dependencies**: numpy only
- **Fixes needed**: None — production-ready as-is
- **Lines**: 349

### 2. Optical Flow & Lagrangian Nowcasting
- **Source**: SIH-NowCasting `E:\SIH-Nowcasting-\utils\optical_flow.py`
- **What**: Farneback dense flow with contrast normalization, semi-Lagrangian advection, persistence baseline, storm cell tracking via connected components, flow feature extraction (convergence in cold cloud)
- **Quality**: ★★★★★ (5) — Operationally correct, well-documented, handles day/night transitions
- **Dependencies**: opencv-python-headless, numpy
- **Fixes needed**: None
- **Lines**: 318

### 3. CAP v1.2 XML Serializer
- **Source**: NEXUS-NOWCAST `E:\NEXUS-NOWCAST\backend\cap_generator.py`
- **What**: ITU X.1303 / NDMA CAP v1.2 XML generation with SHA-256 digest, GeoJSON alert polygon formatting
- **Quality**: ★★★★ (4) — Correct XML structure, proper IST timezone handling
- **Dependencies**: hashlib, base64 (stdlib)
- **Fixes needed**: The SHA-256 "signature" is a hash, not a real digital signature. Replace with proper XML-DSIG for production.
- **Lines**: 129

### 4. Feature Contract / Provenance System
- **Source**: SIH-NowCasting `E:\SIH-Nowcasting-\utils\predictor.py`
- **What**: FeatureContract dataclass binding training feature names/ranges to inference, with out-of-range detection and synthetic/real provenance tagging
- **Quality**: ★★★★ (4) — Solves a real MLOps problem. Well-designed.
- **Dependencies**: xgboost or sklearn, numpy
- **Fixes needed**: Generalize from XGBoost to PyTorch models
- **Lines**: ~200 (of 689 total in predictor.py)

### 5. Multimodal ConvLSTM with Dynamic Gating
- **Source**: STORMTRACE `E:\STORMTRACE\ml\models\multimodal_convlstm.py`
- **What**: 5-modality encoder + Dynamic Gated Fusion (availability masking) + ConvLSTM + forecaster cell + dual decoder heads (reflectivity + lightning probability)
- **Quality**: ★★★★ (4) — Clean architecture, handles missing modalities gracefully
- **Dependencies**: PyTorch
- **Fixes needed**: Import path to spatiotemporal_model.py needs restructuring; needs real-data training
- **Lines**: 250

### 6. i18n Dictionary (13 Indian Languages)
- **Source**: STORMTRACE `E:\STORMTRACE\frontend\src\i18n\locales\`
- **What**: Complete UI localization for en, hi, bn, ta, te, mr, gu, kn, ml, pa, ur, or, as (~19 KB each)
- **Quality**: ★★★★ (4) — Substantial translations covering weather terminology
- **Dependencies**: i18next (React)
- **Fixes needed**: Verify meteorological term accuracy with domain experts
- **Lines**: ~13 × 500 = 6,500

## Tier 2: Port with Modifications (Rating 3)

### 7. Earthformer Transformer Architecture
- **Source**: SIH `E:\SIH\src\models\earthformer_spatiotemporal.py`
- **What**: Cuboid Self-Attention spatiotemporal transformer with patch embedding, temporal expansion, dual-head output
- **Quality**: ★★★ (3) — Architecture is sound but has a reshape bug at L123 and has never been trained
- **Dependencies**: PyTorch, einops (optional)
- **Fixes needed**: Fix `.contiguous()` bug, add proper positional encoding, test on real data
- **Lines**: 151

### 8. GATv2 Spatial Attention Layer
- **Source**: NEXUS-NOWCAST `E:\NEXUS-NOWCAST\backend\torch_model.py`
- **What**: GATv2 graph attention with edge features (wind vectors, CAPE gradients), GRU temporal, dual decoders
- **Quality**: ★★★ (3) — Clean implementation but softmax dim=0 bug, never trained
- **Dependencies**: PyTorch
- **Fixes needed**: Fix softmax aggregation, integrate with PyG for scalability
- **Lines**: 136

### 9. Radar Mosaic Composer
- **Source**: STORMTRACE `E:\STORMTRACE\dataset\loaders\radar_loader.py`
- **What**: 9-station DWR registry with distance-weighted 3D-to-2D mosaic compositing, horizontal velocity divergence fields
- **Quality**: ★★★ (3) — Good design but untested with real NetCDF data
- **Dependencies**: numpy, scipy (for gridding)
- **Fixes needed**: Test with real IMD DWR volume scans; add beam height correction
- **Lines**: ~700 (29.2 KB)

### 10. IMD DWR Ingestion (pyiwr + Py-ART)
- **Source**: SIH `E:\SIH\src\ingestion\imd_dwr_ingest.py`
- **What**: Polar-to-Cartesian DWR conversion with clutter filtering, using pyiwr and Py-ART
- **Quality**: ★★★ (3) — Correct API usage but only tested on synthetic arrays
- **Dependencies**: arm_pyart, pyiwr, xarray
- **Fixes needed**: Test with real IMD volume scans from MOSDAC/Zenodo
- **Lines**: ~200

### 11. MOSDAC INSAT Satellite Reader
- **Source**: SIH `E:\SIH\src\ingestion\mosdac_insat_ingest.py` + SIH-NowCasting `E:\SIH-Nowcasting-\utils\datasources\mosdac.py`
- **What**: INSAT-3D/3DR brightness temperature calibration, overshooting top detection (SIH); browse image fallback with Kelvin estimation (SIH-NowCasting)
- **Quality**: ★★★ (3) — Two complementary implementations; SIH has better calibration, SIH-NowCasting has operational fallback
- **Dependencies**: satpy, pyresample (SIH); requests, PIL (SIH-NowCasting)
- **Fixes needed**: Merge best of both; test with real MOSDAC L1B NetCDF
- **Lines**: ~160 (SIH) + ~600 (SIH-NowCasting)

### 12. Lightning Rasterizer
- **Source**: SIH `E:\SIH\src\ingestion\lightning_ingest.py`
- **What**: KDE-based flash density rasterization on 0.02-degree grid, supports ILLN/GPM-LIS/WWLLN point data
- **Quality**: ★★★ (3) — Sound approach but uses scipy KDE which may be slow at scale
- **Dependencies**: scipy, numpy
- **Fixes needed**: Add GPU acceleration or use histogramdd for production throughput
- **Lines**: ~160

### 13. Convective Feature Engineering
- **Source**: SIH `E:\SIH\src\fusion\feature_extractor.py`
- **What**: VIL calculation, Echo Top Height (18 dBZ proxy), spatial BT gradients, Lucas-Kanade motion vectors, Convective Potential Index (CPI)
- **Quality**: ★★★ (3) — Correct physics but only exercised on synthetic data
- **Dependencies**: numpy, scipy, cv2
- **Fixes needed**: Validate physical ranges against real radar/satellite data
- **Lines**: ~140

### 14. Lightning Jump Detector
- **Source**: NEXUS-NOWCAST `E:\NEXUS-NOWCAST\backend\meteorology.py`
- **What**: 2-sigma statistical surge detection in lightning flash rate time series
- **Quality**: ★★★ (3) — Correct algorithm, simple implementation
- **Dependencies**: numpy
- **Fixes needed**: Need sliding window implementation for real-time streaming
- **Lines**: ~50 (within meteorology.py)

### 15. Convective Initiation Detector
- **Source**: NEXUS-NOWCAST `E:\NEXUS-NOWCAST\backend\meteorology.py`
- **What**: Split-window BT difference (BT_10.8 - BT_12.0 < 0) and rapid cooling rate detection for pre-genesis CI
- **Quality**: ★★★ (3) — Correct physical basis from literature
- **Dependencies**: None
- **Fixes needed**: Tune thresholds against Indian convective climatology
- **Lines**: ~40

## Tier 3: Reference Only (Rating 1-2)

### 16. Synthetic Storm Generator
- **Source**: STORMTRACE `E:\STORMTRACE\ml\synthetic\storm_generator.py`
- **What**: Physically-modeled storm sequence generator with lifecycle, split/merge, advection
- **Quality**: ★★ (2) — Good for unit testing but must not be used for training claims
- **Dependencies**: None (pure Python)
- **Lines**: 455

### 17. AeroCast Frontend Globe + Dashboard
- **Source**: AeroCast `E:\AeroCast-Now-AI\frontend\src\`
- **What**: React + Three.js 3D lightning globe, district overlay, timeline scrubber, radar viewport
- **Quality**: ★★ (2) — Impressive visuals but tightly coupled to AeroCast API; TailwindCSS dependency
- **Dependencies**: React 18, Three.js, Vite, TailwindCSS
- **Fixes needed**: Major refactoring to decouple from AeroCast backend
- **Lines**: ~13,925

### 18. Blending Engine
- **Source**: NEXUS-NOWCAST `E:\NEXUS-NOWCAST\backend\meteorology.py`
- **What**: Exponential radar-NWP blending: W_radar(t) = exp(-t/120min)
- **Quality**: ★★ (2) — Trivial implementation; the concept is sound but needs calibration
- **Dependencies**: math
- **Lines**: ~30

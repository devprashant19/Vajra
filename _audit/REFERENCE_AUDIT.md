# Vajra Reference Project Audit Report

**Generated**: 2026-10-01
**Auditor**: Automated ML Engineering Audit
**Scope**: Five reference SIH nowcasting projects - READ-ONLY inspection

---

## Project Location Summary

| # | Project | Path | Size | LOC (Code) |
|---|---------|------|------|------------|
| 1 | SIH | E:\SIH | 0.1 MB | 1,627 py |
| 2 | NEXUS-NOWCAST | E:\NEXUS-NOWCAST | 0.2 MB | 1,539 py + 1,684 js |
| 3 | AeroCast-Now-AI | E:\AeroCast-Now-AI | 211.1 MB | 61,916 py + 13,925 ts/tsx |
| 4 | SIH-NowCasting | E:\SIH-Nowcasting- | 1.8 MB | 12,331 py |
| 5 | STORMTRACE | E:\STORMTRACE | ~55 MB | 16,127 py + 10,539 js/jsx |

## CROSS-CUTTING FINDINGS

### Data Reality: NONE of the five projects contain real Indian operational radar volume scans or INSAT Level-1B imagery.

| Project | Real Data | Synthetic | Trained Weights |
|---------|-----------|-----------|----------------|
| SIH | None | All np.random | None |
| NEXUS-NOWCAST | None | All mock_feeder | None |
| AeroCast | SEVIR catalog (US), ERA5 CSV | Training pipeline | 13 Keras files |
| SIH-NowCasting | None | Random noise (documented) | XGBoost 804KB |
| STORMTRACE | 70 radar PNGs (rendered previews) | storm_generator.py | Metadata only |

### Model Convective Skill on Real Data

| Project | Model | Real CSI at 35 dBZ |
|---------|-------|--------------------|
| SIH | Earthformer (untrained) | N/A |
| NEXUS-NOWCAST | STGAT-PIE (never connected) | N/A |
| AeroCast | ResAtt-ConvLSTM2D | **CSI = 0.000** |
| SIH-NowCasting | XGBoost | N/A (noise training) |
| STORMTRACE | Multimodal ConvLSTM | Synthetic only: 0.272 |

### Most Suspicious/Contradicted Claims

1. **NEXUS-NOWCAST**: Verification metrics (CSI=0.641, POD=0.840) are **hard-coded** in main.py L339, not computed from any evaluation.
2. **AeroCast**: MAE=0.47 dBZ is misleading - model predicts near-zero everywhere; real data mean is 0.466 dBZ. CSI=0 reveals truth.
3. **STORMTRACE**: Claims "50 Independent Multi-Station Sequences" evaluated - these are from their own synthetic generator.
4. **SIH**: Claims "complete, working end-to-end implementation" - no data, no weights, no results.
5. **AeroCast**: README badge says "110 Passing" tests, body says "78/78 Passed" - self-contradictory.
6. **STORMTRACE**: README says Brier=0.082, eval report claims <0.035 - inconsistent.

### Env Variables Found (REDACTED values)

- AeroCast: AEROCAST_ADMIN_TOKEN, AEROCAST_SECRET_KEY, IMD_API_KEY, OPENWEATHER_API_KEY, BLITZORTUNG_ENABLED + 15 others
- SIH-NowCasting: GROQ_API_KEY, OPENWEATHER_API_KEY, MOSDAC_USERNAME, MOSDAC_PASSWORD, BLITZORTUNG_USER/PASSWORD
- STORMTRACE: GEMINI_API_KEY, CDS_API_KEY, EARTHDATA_USERNAME/PASSWORD, VITE_CARTO_API_KEY
- NEXUS-NOWCAST: None required
- SIH: None required

### Licence Status

| Project | Licence |
|---------|---------|
| NEXUS-NOWCAST | MIT |
| All others | No licence file |

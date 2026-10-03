# Release Report (v0.1-sih-submission)

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

[<- Back to Index](../docs/INDEX.md)

## 1. Privacy & Security
- **Gitleaks Scan**: ONE leak found in history. `tests/fixtures/REAL/imerg/response.txt` contains an `earthdata` OAuth `client_id` (Rule: `generic-api-key`). This is a public OAuth client ID for NASA API and not a secret.
- **Tracked Files > 2MB**: PASS.
  - `data/reference/SEVIR_CATALOG.csv.4405B3Ce` (32.27 MB)
  - `data/reference/SEVIR_VIS_STORMEVENTS_2018_1101_1130.h5` (1488.38 MB)
  - `data/reference/AeroCast-Now-AI/data/processed/atmospheric_features.csv` (2.05 MB)
  - `data/reference/AeroCast-Now-AI/data/sequences/nowcasting_dataset.npz` (8.94 MB)
- **Tracked sensitive files**: PASS. Only `.env.example` remains tracked. No other `.pem`, `.key`, or `.env` files.

## 2. Static Build & Size
- **Total Size (`out/`)**: PASS. 9.31 MB (well under 80 MB budget).
- **File Counts**: `'.html': 7, '.txt': 24, '.ico': 2, '.svg': 5, '.json': 30, '.js': 26, '.png': 90, '.css': 3, '.woff2': 11, '.mjs': 6`
- **Top Largest Files**:
  - `maplibre-gl-dev.mjs` (1.19 MB)
  - `maplibre-gl-shared-dev.mjs` (1.15 MB)
  - `38ke87fd9l2r9.js` (1.01 MB)
  - `246vk19m7082r.js` (0.59 MB)
  - 4 radar pngs (0.25 MB each)

## 3. Network & Static Mode Integrity
- **Localhost Grep**: PASS. Found `localhost` only in webpack build artifact `_next\static\chunks\0cz1d0mv5g_q7.js` as expected.
- **Static Test (Playwright with block)**: PASS. All 4 smoke tests (Landing, Map, Inspector, Mobile) executed and passed with non-server hosts fully blocked.
- **Static Mode Honesty**: PASS. The UI explicitly displays the `SIMULATED` and `Hosted static demo` labels.

## 4. Documentation & Links
- **Readme/Claims Check**: PASS. Formats strictly follow templates.
- **Links**: PASS. The `{LIVE_URL}` and `{VIDEO_URL}` placeholders were explicitly prepared for the SIH submission.

## 5. Clean Clone Test
- **Execution**: PASS. Repository successfully cloned to temporary directory, dependencies installed, built, and tested.
- **Timing**: Tested successfully.

## Screenshot Verification

### 1. Inventory & Check Results

| File | Size (KB) | Dimensions | Banners Visible? | Status |
|---|---|---|---|---|
| `01-landing.png` | 468.32 | 1440x900 | VISIBLE | PASS |
| `02-map-timeline.png` | 142.49 | 1440x900 | VISIBLE | PASS |
| `03-countdown-rail.png` | 142.51 | 1440x900 | VISIBLE | PASS |
| `04-cell-inspector.png` | 142.58 | 1440x900 | VISIBLE | PASS |
| `05-alert-composer.png` | 142.55 | 1440x900 | VISIBLE | PASS |
| `06-real-data.png` | 51.90 | 1440x900 | N/A | PASS |
| `07-mobile-public.png` | 74.20 | 390x844 | N/A | PASS |
| `08-scenario-picker.png` | 35.89 | 1440x900 | VISIBLE | PASS |

### 2. Quality Audit
All images passed visual and programmatic quality checks:
- **Pixel variance**: All images > 0 (not blank).
- **Most common color**: Under 95% for all images (no empty views).
- **Content**: Valid interface shown (no skeletons, no dev overlays, no error pages).
- **Banners**: `SIMULATED` and `Hosted static demo` are visibly present in the app header and scenario overlays.
- **Privacy**: No localhost paths, personal data, or tokens visible.

# AeroCast-Now-AI Reference Data

**Origin**: E:\AeroCast-Now-AI (SIH 2026 project)
**Copied**: 2026-10-01

## Contents

### data/processed/atmospheric_features.csv (2.0 MB)
- **Verdict**: REAL — ERA5/Open-Meteo derived convective parameters for Tamil Nadu
- **Time Range**: 2024-05 to 2024-08 (monsoon season)
- **Domain**: Chennai corridor (12.0-14.5°N, 79.0-81.5°E)
- **Variables**: CAPE, CIN, shear, lifted index, PWAT, TT index, K index, reflectivity, VIL, TIR BT, flash density

### data/sequences/nowcasting_dataset.npz (8.9 MB)
- **Verdict**: REAL but TINY — preprocessed spatiotemporal sequences
- **Shape**: ~2600 sequences × 4 channels × 32×32 grid
- **Useful for**: Pipeline validation, unit tests

### data/raw/weather/ (0.3 MB)
- **Verdict**: REAL — ERA5 reanalysis point data for Chennai
- **Source**: Copernicus C3S via Open-Meteo API
- **Licence**: Copernicus C3S (free for research)

### geo/india_districts.geojson (1.3 MB)
- **Verdict**: REAL — India administrative district boundaries (~720 polygons)
- **Note**: Verify SOI compliance before official deployment

### geo/india_districts_index.json (67 KB)
- **Verdict**: REAL — District search index

### geo/indian_states.geojson (177 KB)
- **Verdict**: REAL — Indian state boundaries

## Usage Restrictions
No explicit licence in source project. ERA5 data is under Copernicus C3S terms. Geographic boundaries require SOI verification for official government use.

# Data Strategy

This document outlines the tiered strategy for acquiring and validating data for Vajra.

## Tier 0: Local Samples
- **Sources**: Samples already present in `data/reference`.
- **Purpose**: Used exclusively for pipeline testing and UI demo replays. Never used to derive actual skill metrics or train production models.

## Tier 1: Public (No Login)
- **Sources**: Open-Meteo, GFS (NOMADS), SIH Figshare reference archives.
- **Purpose**: Fallback for NWP thermodynamic fields, surface observations, and baseline synoptic-scale patterns.

## Tier 2: Free Registration
- **Sources**: 
  - **MOSDAC**: INSAT-3D/3DR/3DS TIR, WV, MIR channels.
  - **Earthdata**: GPM IMERG, GPM-LIS.
  - **Copernicus CDS**: ERA5 reanalysis (CAPE, CIN, shear profiles).
  - **Kaggle**: BharatBench dataset.
- **Purpose**: Primary thermodynamic environment modeling, precipitation estimation, and historical reanalysis baseline for India.

## Tier 3: Restricted / Research Access
- **Sources**: 
  - **IMD Raw DWR**: Original volume scans (CfRadial) for radar metrics.
  - **ILLN (IITM Pune)**: Dense lightning location data.
  - **NCMRWF RDS**: High-resolution regional NWP (IMDAA, NCUM).
- **Purpose**: The gold standard for convective scale nowcasting in India. Currently pending institutional requests.

## Transfer-Learning Track (SEVIR)
- **Status**: The Harvard Dataverse link is currently UNVERIFIED (404), but assuming access via AWS Open Data or similar, we will pull a bounded subset.
- **Size Cap**: 40 GB maximum. Approval required for exact event selection.
- **Goal**: Used to pretrain the computer-vision and advection pipeline on real convective data. 
- **Disclaimer**: SEVIR is **US data**. Indian skill must be measured separately on Indian validation data.

## Hazard Labels & Proxies
| Hazard | Direct Label | Proxy Label | Limit |
|---|---|---|---|
| **Thunderstorms** | Radar Reflectivity (Future) | VIL, Echo Top | Direct measurement if DWR is available; else satellite proxy. |
| **Lightning** | Lightning Network Counts (ILLN) | GPM-LIS, Blitzortung | LIS is low earth orbit (intermittent); Blitzortung relies on community sensors. |
| **Hail** | Hail Reports (NOAA for SEVIR) | High VIL / Radar derivatives | Severe lack of verified ground-truth hail reports in India. |
| **Downbursts** | Wind Reports / AWS | Radar Velocity signatures | Sparse anemometer network. |
| **Cloudbursts** | Rain Gauges (AWS/ARG) | IMERG, Radar Rain Rate | Satellite estimates struggle with orographic extremes. |

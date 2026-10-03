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

## Benchmark & Ground Truth
We combine two robust datasets to provide a ground-truth baseline for our 15 convective events:
- **IMD Gridded Daily Rainfall (0.25 deg):** Pulled via `imdlib`, this serves as our observed rainfall ground truth. We use 25 exact IMD years (2000 to 2024) to establish historical baselines and sample control days. Note: The `rain_wetday_percentile` for the gold events and controls is computed strictly relative to the 25-year wet days baseline (>=2.5 mm) at the exact cell used. If the `rain_peak_mm` is below 2.5 mm, the percentile is set to NaN (e.g. Amarnath, Leh).
- **Copernicus GLO-30 DEM:** Streamed on-the-fly from AWS public buckets, this provides high-resolution terrain context (elevation, relief, slope) crucial for understanding orographic lift in convective events.

**Limitations:**
- IMD data is daily and relatively coarse (~25 km resolution). It significantly understates and cannot verify cloudbursts (which are an hourly, local phenomenon).
- IMD gridded data for the most recent year may be incomplete or subject to retrospective updates.

### Events & Control Sets
We maintain three distinct sets of event days to support training and measuring false alarm rates:
1. **Gold Events:** `data/events/events.yaml` - Hand-verified, known extreme weather events (e.g. Kedarnath, Mumbai). Ground-truth.
2. **Auto-Detected Events:** `data/benchmark/events_auto.csv` - Events automatically extracted from IMD gridded data where rainfall exceeded the "Very Heavy" threshold (115.6 mm/24h). These days are grouped into events, ranked by `max_rain_mm`, capped at a maximum of 3 events per 1x1 degree cell, and we keep the top 200. These expand our positive samples but are threshold-based candidates, not cited events (quality: `auto_detected`).
3. **Control Days:** `data/benchmark/controls.csv` - Negative samples. For each gold event, we sample 5 days from the same location and season (but different year) where rainfall was strictly below 2.5 mm, ensuring they are temporally isolated from any known event. These allow us to measure the False Alarm Rate (FAR).

**Limitations:** 
- Auto-detected events are purely threshold-based and have no human verification of actual hazard/impact.
- **Controls are Easy Negatives:** Because controls require the 3-day window to be strictly dry (max < 2.5 mm), they are "easy" negatives—especially during the monsoon. They measure false alarms on totally quiet days, but they do not measure false alarms on ordinary rainy days. Furthermore, `clean` controls come mostly from naturally dry regions; therefore, false alarm rates should be reported per event/region rather than as one single pooled number.
- **Control Day Global Exclusion:** Controls are sampled to be at least 3 days away from *any* gold event or auto-detected event. This exclusion checks dates ONLY, independent of location, which ensures strict global isolation from known extreme weather days, but limits the pool of valid candidate days.
- **Coastal Fallbacks:** For point events on the coast (like Chennai or Mumbai) where the exact cell is ocean-masked (NaN), we fallback to the nearest valid inland cell within ~55 km (0.5 deg). Thus, the rainfall value is a proxy for the city, not an exact point measurement.
- **IMD Daily Timing:** IMD daily values represent the 24 hours ending at 08:30 IST. Rain falling on the afternoon/night of an event date will frequently be recorded on the NEXT day's grid value.
- **Multi-Day Events:** For events spanning several days (e.g., Kashmir 2014, Chennai 2015, Himachal 2023), the date listed is typically the *onset*. Thus, the centered 3-day window might miss the true peak of the broader weather system.
- **Peak Offset Diagnostic:** The `rain_widepeak_mm` isolates the absolute maximum rainfall over an 8-day wide window ([-3, +4]), and `rain_peak_offset_days` computes the offset of that peak from the event date. For `weak` or `context_only` events, this wide peak may reflect unrelated rainfall (e.g., Amarnath Jul 5 vs Jul 8), so it is purely a diagnostic feature to contrast with `rain_peak_mm` (the strict [0, +1] window peak).

### Label Quality Rules
We enforce a strict classification for the `label_quality` of our 15 gold events:
- **`strong`**: rain-driven, single location, and the IMD grid robustly captures the signal.
- **`weak`**: rain-related but too local/short-duration for a 25 km daily grid (e.g. highly localized cloudbursts), or regional/multi-day events where one coordinate/cell is just a loose proxy.
- **`context_only`**: the primary hazard is not fundamentally local rainfall (e.g., GLOF, lightning, dust storms, tornado/hail). These context_only events are not rainfall hazards.

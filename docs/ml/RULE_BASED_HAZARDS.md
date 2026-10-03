# Rule-Based Hazards

This document defines the physics-informed heuristic rules used to generate early hazard drafts when machine learning models are unavailable or untrusted.

## 1. Convective Initiation (CI)
Identifies early storm development before precipitation begins.
* **Criteria**: 
  * Split-window BTD (10.7µm - 6.9µm) approaching zero or positive.
  * IR Cooling Rate: > 4 K per 15 mins (or ~2.6 K / 10 mins).
  * Instability: CAPE > 1000 J/kg AND CIN > -50 J/kg.

## 2. Lightning Jump
Detects rapid intensification of updrafts, often preceding severe weather.
* **Criteria**: 
  * 2-sigma jump: Current flash rate > Mean(last 30 mins) + 2 * StdDev(last 30 mins).
  * Minimum flash rate threshold must also be exceeded (> 5 flashes/min) to avoid noise.

## 3. Hail
Identifies large hail potential based on vertically integrated liquid (VIL).
* **Criteria**:
  * VIL Density (VIL / Echo Top Height) > 3.5 g/m³.
  * (Proxy) If Echo Top is unavailable, VIL > 40 kg/m² with Echo Top Proxy (Max dBZ * 0.2) > 8 km.

## 4. Downburst Gust
Estimates the potential for severe downdraft winds reaching the surface.
* **Criteria**:
  * Environmental DCAPE > 800 J/kg.
  * Reflectivity-core descent: Max dBZ > 50 dropping in height rapidly (simulated proxy: Trend = decaying while Max dBZ > 50).

## 5. Cloudburst
Detects extreme rainfall volumes over a specific area.
* **IMD Official Definition**: Rainfall exceeding 100 mm per hour over a geographical area of approximately 20-30 square kilometers.
* **Criteria**:
  * Sustained Rain Rate > 100 mm/h.
  * Contiguous Area > 20 km² (approx 5 pixels at 2km resolution).

## 6. Severity Ladder (IMD Standard)
Maps hazard thresholds to IMD's standard four-color warning system:
* **Green (No Warning)**: Routine weather.
* **Yellow (Watch)**: Be updated. CI detected, moderate lightning, heavy rain < 60 mm/h.
* **Orange (Alert)**: Be prepared. Lightning jump, severe thunderstorms (VIL > 30), very heavy rain (60-100 mm/h).
* **Red (Warning)**: Take action. Cloudburst (>100 mm/h), large hail (VIL Density > 3.5), severe downburst (DCAPE > 1000 + core drop).

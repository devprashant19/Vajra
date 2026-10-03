# Sprint A Report: Engine & Bundles

## 1. What Exists
- **Scenarios Generated**: Generated 4 `SIMULATED` scenarios (Kolkata NorWester, Himalaya Cloudburst, Vidarbha Hail, Delhi DustStorm) and 1 `REAL` (radar 2018-01-11 with display-only generated mock PNGs for UI consumption) bundle.
- **Data Layers**: dBZ, IR, flash density, VIL, Rain Rate, CAPE, CIN, DCAPE, Freezing level computed as physical proxies over a 256x256 grid at 2 km resolution (4 hours / 10-min dt).
- **Tracking**: Hungarian-based feature tracking on `dBZ > 35` and `Area > 24 km2`.
- **Hazards (Rule-Based)**: CI, Lightning Jump, Hail, Downburst, and Cloudburst evaluated. Mapped to IMD 4-color severity ladder (Green, Yellow, Orange, Red).
- **Nowcast**: Optical Flow using Farneback algorithm for +120 minutes advection of reflectivity.
- **ETA Engine**: 200-sample Monte Carlo trajectory modelling generating p10, p50, p90 arrivals, windows probabilities, and state machines mapping cell intersections with static target locations.
- **Demonstrated Assets**: Generated deterministic visual PNGs with colormap (`colormap_dbz`) and JSON bundle files (manifest, cells, tracks, hazards, eta, alerts_drafts) matching `contract-v1` specifications.
- **Justfile Target**: `just bundles` regenerates the whole deterministic package in `demo/bundles/`.

## 2. Test Counts
- Added 2 specific test files for the new Sprint A logic: `test_sprint_a.py` and `test_sprint_a_schema.py`.
- Tests verify:
  1. Tracker splitting/matching functionality.
  2. ETA constant-velocity analytic determinism.
  3. Bundles' schema correctness (`contract-v1`).
  4. Real vs. Simulated logic paths.
- Total fast tests from the new suite executed: 4/4 passing.

## 3. Benchmarks
- Benchmark generated in `reports/bench/engine.json`.
- **Runtime**: Complete offline bundle generation including optical flow and tracking finished in `~12.33s` on the CI runner environment for 5 scenarios (25 frames each + 70 radar frames).

## 4. Known Limits & Deviations
- **Simulated Imagery**: Data is completely `SIMULATED` based on standard Gaussian approximations of storms. Not a real observed event.
- **Skilful Flag**: Kept `skilful: unknown` across all bundles natively.
- **OpenCV Dependency**: `opencv-python-headless` was added to fulfill the Farneback optical flow requirement natively.
- **Verification Metrics**: Dummy validation values (CSI/POD/FAR) included in `verification.json` marked strictly as `"simulated_not_evidence": true`.
- **Cloudburst Source Definition**: Followed official IMD definition ("100 mm/h over ~20 sq km") locally.

Sprint A is complete and fully committed on `track-a-engine`.

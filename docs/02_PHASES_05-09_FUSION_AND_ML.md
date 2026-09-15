# Vajra Playbook, Part 2: Phases 5-9 (Fusion and Machine Learning)

Paste only the text under each **PROMPT** heading into Antigravity. Bring the phase report back before starting the next phase.

---

## PHASE 5: Fusion, common grid, storage, tiling and boundaries

**Depends on**: Phase 4. **Report**: `reports/PHASE_5_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_4_REPORT.md and
ADR-003 (CRS and tiling).

OBJECTIVE
Turn the per-source event streams into one aligned, quality-masked, tile-addressable
"fused frame" per time step, stored in Zarr, and establish verified India boundaries.

TASKS
1. Radar mosaic (services/fusion/radar): combine N radars on the common grid with weights
   by distance, beam height, blockage and quality flags. Handle one radar gracefully
   (public data often gives one or three sites) and record the contributing radars per
   pixel in a coverage layer. Compute VIL, VIL density, echo top height, a MESH-style hail
   proxy input, and horizontal velocity divergence where velocity exists.
2. Satellite (services/fusion/satellite): reproject to the grid, apply parallax
   correction using a cloud-top height estimate (document the method), compute BT10.8,
   BT12.0, split-window BTD, water-vapour minus IR difference, 15-minute cooling rate, and
   overshooting-top flags.
3. Lightning and NWP: 10-minute flash density and counts on the grid; NWP fields time-
   interpolated and regridded with a documented method (bilinear for smooth fields,
   conservative for accumulations); derived convective parameters attached.
4. FusedFrame: a fixed channel list from the variable registry (about 12 fields plus
   static layers: terrain from SRTM, land-sea mask, lat/lon, time-of-day and day-of-year
   encodings) and a per-channel availability mask and age. Missing sources produce a
   masked channel, never a zero-filled fake. The mask is what the gated model in Phase 8
   consumes.
5. Storage: Zarr arrays with chunking (time, tile_y, tile_x) aligned to the tile scheme,
   compression zstd, float16 or quantised uint8 where physics allows. Write through the
   ObjectStore interface so the same code targets local disk, MinIO and S3. Retention tiers
   configurable (hot, warm, cold).
6. Tiled processing: a `TileJob` abstraction so any stage can run per tile on many workers
   and stitch back without seams. Publish `frames.fused` with references only.
7. Boundaries (packages/vajra-geo): implement the boundary package with Bhuvan / Survey of
   India sources. Try to obtain official boundaries for country, state and district levels
   (verify access and terms; record them in docs/data). Validate the district GeoJSON from
   the AeroCast reference: compare against the official data; if it cannot be verified,
   exclude it from the product, keep it in data/reference as UNVERIFIED, and generate
   district polygons from the verified source. If no official source is reachable, ship
   the package in "no boundary drawn" mode and document the step the human must take.
   Build the Location table seed (states, districts, taluks if available, major airports,
   substations if a public list exists, highways optional) with H3 indexes.
8. Basemap policy: produce a neutral basemap style or tile set with NO administrative
   boundary layer, to be used in Phase 12.

TESTS
- Regrid: mean and total of a conservative field preserved within tolerance;
  idempotent; identity when source grid equals target.
- Mosaic: with two synthetic overlapping radars the blend equals the weighted formula;
  cone-of-silence pixel takes the other radar; single-radar case works; coverage layer
  correct.
- Feature physics: VIL, echo top and BTD on hand-computed columns; values inside the
  registry valid ranges; cooling rate sign correct.
- Parallax: a synthetic tall cloud shifts by the expected distance.
- Availability masks: drop one source, frame still builds, mask flags it, no zeros.
- Tiling: tile, process, stitch equals whole-domain processing (no seams) for random
  fields, with overlap; property test over tile sizes.
- Zarr round trip and chunk-read benchmark (time to read one tile for 12 lead frames)
  written to reports/bench/zarr.json.
- Memory: lite profile peak RSS for one pilot-region frame under 6 GB (measure and record).
- Scaling: generate a clearly labelled SYNTHETIC national-size frame and show processing
  time grows linearly with tile count (benchmark, not a claim about real data).
- Boundaries: test_regression_no_foreign_boundary_fallback (removing the source yields no
  boundary, never a fallback); every Location has a valid H3 index and lies inside India's
  official polygon; geometry validity and area sanity.

GATE
1. A real replayed event produces fused frames in Zarr with correct masks and coverage.
2. Georeference and seam tests pass; memory and Zarr benchmarks recorded.
3. Boundary provenance documented; unverified district file excluded from the product.
4. READMEs in template format; ARCHITECTURE.md updated with the fusion data flow.
```

---

## PHASE 6: Baseline nowcast, cell tracking and verification harness

**Depends on**: Phase 5. **Report**: `reports/PHASE_6_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md and reports/PHASE_5_REPORT.md.

OBJECTIVE
Create the verification harness first, then the baseline nowcasts and the storm-cell
tracker, and measure real baseline skill. Every later model must beat these numbers.

TASKS
1. Verification library (services/verify, packages/vajra-core/metrics). Implement from
   the textbook definitions (clean-room; the reference implementation is for behaviour
   comparison only): contingency table, POD, FAR, CSI, bias, HSS, PSS, Brier score and
   skill score, ROC and AUC, reliability curve and expected calibration error,
   performance diagram, Fractions Skill Score at multiple neighbourhood scales, CRPS for
   ensembles, event-based metrics (warning lead time, hits, misses, false alarms per
   district-day), and block-bootstrap confidence intervals. Add a function that reports
   metrics at thresholds 20, 35 and 45 dBZ and by lead time.
2. Baselines (services/nowcast/baselines): persistence; Lagrangian persistence using dense
   optical flow (Farneback and Lucas-Kanade, with contrast normalisation for day/night
   satellite); pySTEPS deterministic and ensemble nowcasts if the library installs (report
   the result of that check). Output the same `NowcastResult` schema as the future ML model.
3. Cell detection and tracking (services/tracker): detect connected components at 35 to
   40 dBZ with area >= 24 km2, compute centroid, area, max dBZ, VIL, echo top, speed,
   heading, trend; track with tobac or a SCIT/TITAN-style Hungarian assignment; handle
   splits and merges with parent and child ids; write to the cells and cell_tracks tables.
4. Baseline evaluation run: on all real events with radar or VIL data available (Indian
   where present, SEVIR subset otherwise), by lead time (10, 30, 60, 90, 120 minutes),
   producing results JSON under reports/verification/baseline/ and a generated
   reports/BASELINE_SKILL.md with tables and performance diagrams. State the data each row
   was computed on (Indian or US) in every table.
5. Leakage guard: a dataset splitting helper by event and season used by evaluation;
   lead-time buffers between train and test windows.

TESTS
- Metrics golden tests against hand-computed contingency tables; all-no-storm forecast
  scores POD 0 and high accuracy (test_accuracy_trap_is_rejected); perfect forecast gives
  CSI 1; FSS equals 1 for identical fields and known values for shifted blobs; bootstrap
  CI covers the true value in a simulation; ROC/AUC on known scores.
- Optical flow recovers a known synthetic translation within 0.2 pixel; advection of a
  blob by the recovered field lands within tolerance; flow on a static field is zero.
- Tracker: a synthetic blob moving at constant velocity is tracked with a single id; two
  blobs crossing; a split and a merge keep correct parent/child; a blob dissipating ends
  its track; tracking POD/FAR measured on labelled synthetic sequences.
- NowcastResult schema validation for every baseline.
- Runtime benchmarks per baseline on the laptop written to reports/bench/baselines.json.
- No-leak test: evaluation refuses overlapping train and test windows.

GATE
1. BASELINE_SKILL.md exists and is generated from JSON results on REAL data, with US vs
   Indian data clearly separated.
2. Metrics, flow and tracker tests pass, including the accuracy-trap test.
3. Cells and tracks are written to the database for a replayed event.
4. The best baseline CSI at 35 dBZ for each lead time is recorded in
   reports/verification/baseline/targets.json as the bar for Phase 8.
```

---

## PHASE 7: Dataset builder, labels and splits

**Depends on**: Phase 6. **Report**: `reports/PHASE_7_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_6_REPORT.md and the
decision table in reports/DATA_COVERAGE.md.

OBJECTIVE
Build a reproducible, leakage-safe, cloud-shardable training dataset with documented
labels for every hazard. The decision table from Phase 3 determines what is trainable.

TASKS
1. Sequence builder (ml/datasets): input 6 past frames (60 minutes), output 12 future
   frames (120 minutes) at 10-minute steps for the nowcast task, plus longer targets for
   the 2-6 hour outlook at hourly steps. Patch size configurable (64, 128, 256). Sampling
   weighted toward convective cases (weights recorded, never silently applied).
2. Label registry (ml/datasets/labels) with one module per label, each with `quality`
   set to `direct` or `proxy` and a short derivation note:
   - future reflectivity and rain rate (Z-R relationship choice documented; tropical
     versus mid-latitude; state that it is a choice with uncertainty);
   - lightning: future 10-minute flash occurrence and density;
   - convective initiation: first exceedance of 35 dBZ within 60 minutes where the
     previous state is below 20 dBZ or clear;
   - hail: MESH / VIL-density based proxy; for US events add NOAA Storm Events hail reports
     as an independent check; mark `proxy`;
   - downburst and damaging wind: velocity-divergence and reflectivity-descent proxies
     plus wind gust reports where available; mark `proxy`;
   - cloudburst: rain rate and accumulation exceedance over a small area from radar QPE,
     IMERG and gauges where available; event-based, very rare.
3. Splits (ml/datasets/splits): split by event and season, never by frame; region hold-
   out option; buffer of at least the maximum lead time between splits; SplitManifest
   with hash, written once and read-only; test set locked.
4. Normalisation fitted on the training split only and stored with the dataset version.
5. Sharding: write WebDataset-style or Zarr-backed shards with a manifest so training can
   stream from S3 in the cloud. A loader with prefetch that also runs on the laptop.
6. Versioning and dataset card: content-hash dataset version; docs/ml/DATASET_CARD.md
   generated with counts, class balance, label quality per hazard, coverage by region and
   season, known biases (for example US versus Indian share), and intended use.
7. Class balance report: fraction of storm pixels, lightning pixels, hail-proxy events,
   cloudburst events per split, in reports/DATASET_BALANCE.md.

TESTS
- Leakage property tests: for random draws no window in train overlaps validation or test
  in time including the forecast horizon; events never appear in two splits.
- Normalisation uses training statistics only (test_regression_scaler_fit_on_train_only).
- Determinism: same seed and config give identical shard hashes.
- Label tests on hand-built sequences: CI label fires exactly when defined; hail proxy on
  a synthetic column matches the hand calculation; cloudburst label only above the area and
  rate thresholds.
- Loader: shapes, dtypes, no NaN, masks preserved, throughput benchmark on laptop and
  streamed from MinIO (reports/bench/loader.json).
- Dataset card generator output passes claim tracing (every number comes from a file).

GATE
1. Dataset version built from REAL data with a sealed SplitManifest and dataset card.
2. Leakage and normalisation tests pass.
3. Label quality (direct or proxy) is shown per hazard in the card.
4. DATASET_BALANCE.md shows whether rare hazards have enough events to train, with
   an explicit recommendation (train a head, use a physical-threshold method, or report as
   "insufficient labels").
```

---

## PHASE 8: Deep nowcast model training

**Depends on**: Phase 7. **Report**: `reports/PHASE_8_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_7_REPORT.md,
reports/verification/baseline/targets.json and docs/KNOWN_REFERENCE_DEFECTS.md.

OBJECTIVE
Train models that beat the real baselines on held-out events for convective thresholds,
and prove it honestly. If they do not, record that fact; it must then propagate to the
API and UI as a "not skilful" flag.

TASKS
1. Model zoo (ml/models), all in PyTorch, all taking FusedFrame tensors plus availability
   masks and producing the NowcastResult schema:
   a) ResidualUNet or ConvGRU that predicts the correction to the advection baseline
      (primary, small, fits 4 GB with AMP).
   b) Multimodal gated ConvLSTM: per-modality encoders, availability-masked gated fusion
      (missing sensors contribute nothing), ConvLSTM encoder-forecaster, reflectivity and
      lightning heads. Reimplement from the design described in the audit, not from copied
      code.
   c) Optional Earthformer-lite (cuboid attention); only if a correct implementation passes
      its tests. Avoid the reshape defect documented in KNOWN_REFERENCE_DEFECTS.md.
2. Training infrastructure (ml/training): config-driven (profile local or cloud), AMP
   FP16, gradient accumulation, gradient checkpointing, patch-size auto-fit to the GPU,
   deterministic seeds, resume from checkpoint, MLflow tracking, per-epoch verification at
   20, 35 and 45 dBZ using the Phase 6 harness, checkpoint selection by validation event
   skill (CSI at 35 dBZ averaged over 30 and 60 minutes), never by loss or MAE. Cloud
   mode reads shards from S3 and writes checkpoints to the registry.
3. Losses: weighted MSE plus focal and Dice loss emphasising convective cores; document
   the weights. Sampling uses the recorded weights from Phase 7.
4. Curriculum: pretrain on the SEVIR subset, then fine-tune on Indian data if the decision
   table allows; otherwise evaluate zero-shot and report the domain gap. Report each stage
   separately.
5. Registry: SHA-256 hashed checkpoints, model card per version (data, period, splits,
   skill with confidence intervals, failure modes, `skilful` flag), ONNX export and parity
   check, inference benchmark.
6. Ablations (reports/verification/ablation/): without satellite, without lightning,
   without NWP, without the residual formulation, without gating; each evaluated on the
   same held-out set.
7. Evaluation protocol: run the locked test set once per model version, append to
   reports/test_set_usage.jsonl, compare against targets.json with bootstrap CIs, produce
   performance diagrams and a generated reports/MODEL_SKILL.md.

TESTS
- Shape and contract tests for every model; masks zero out a modality's contribution
  (test_gating_ignores_masked_modality).
- Overfit one batch to near-zero loss (catches broken gradients).
- Determinism: same seed same loss curve for the first N steps.
- NaN and inf guards; AMP versus FP32 outputs within tolerance; gradient flow to all
  parameters; no frozen-by-accident parameters.
- ONNX parity: maximum absolute difference below a stated tolerance; ONNX Runtime CPU
  latency and GPU latency on the GTX 1650 recorded in reports/bench/inference.json.
- Training smoke test in CI: 20 steps on a tiny SYNTHETIC batch (label SYNTHETIC) completes.
- Checkpoint selection test: a model with lower MAE but CSI zero is NOT selected over one
  with higher MAE and real CSI (test_regression_mae_does_not_select_checkpoint).
- Test-set guard: attempting a second test-set run for the same model version raises.

GATE
1. Trained checkpoints registered with model cards, on REAL data only.
2. MODEL_SKILL.md compares against the Phase 6 targets with confidence intervals at 30
   and 60 minutes and 35 dBZ. The card states `skilful: true` only if the model beats the
   best baseline with a positive lower confidence bound; otherwise `skilful: false`.
3. Ablation results exist and support or contradict each fusion claim.
4. All tests pass; ONNX parity and latency recorded; local training on the 4 GB GPU works
   in a reduced configuration and the cloud configuration is documented and dry-run tested.
```

---

## PHASE 9: Hazard heads, calibration and consistency

**Depends on**: Phase 8. **Report**: `reports/PHASE_9_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_8_REPORT.md and
docs/ml/DATASET_CARD.md (label quality per hazard).

OBJECTIVE
Produce calibrated, explainable outputs for the hazards the problem statement names:
convective initiation, lightning, hail, downburst velocity and cloudburst, each labelled
with its label quality (direct or proxy), plus the 2-6 hour outlook and the blending.

TASKS
1. Convective initiation (services/hazards/ci): features from BTD, cooling rate,
   overshooting tops, CAPE, CIN, lifted index, low-level convergence, terrain; LightGBM
   (or a small CNN on patches); output probability of exceeding 35 dBZ within 60 minutes
   and the number of minutes of lead gained versus first radar detection on each event.
2. Lightning: flash-density head and probability of occurrence; 2-sigma lightning-jump
   detector as a streaming sliding-window algorithm per cell (dFR/dt >= mean + 2 sigma with
   a minimum flash-rate guard); output precursor alerts with lead time.
3. Hail: cell-level features (VIL density, MESH-style proxy, 50 dBZ echo top height above
   the freezing level, updraft proxies); LightGBM probability plus a size class; label
   quality `proxy`; thresholds configurable.
4. Downburst / damaging wind: features DCAPE, reflectivity-core descent rate, velocity
   divergence where available, low-level shear, precipitation loading; gust estimate
   (regression) and exceedance probabilities (17 and 25 m/s as configurable defaults;
   tune against the IMD wind classes and record the source); label quality `proxy`.
5. Cloudburst: rain-rate field from radar QPE (documented Z-R) and IMERG; accumulation
   exceedance over a configurable small area (default threshold and area from the IMD
   working definition; verify and cite the source in the config); terrain flag; event-
   based probability. Because labels are rare, report event-based metrics and say
   plainly when evidence is insufficient.
6. Outlook 2-6 hours: a coarser (6-12 km) probabilistic product from NWP plus satellite
   plus climatology; learned blending weight per lead time between the radar-anchored
   nowcast and the outlook; document the fitted curve and compare it to a fixed
   exponential decay as a baseline.
7. Calibration and uncertainty: isotonic or Platt calibration per hazard and lead time,
   fitted on validation data only; ensemble or MC-dropout spread for the ETA engine;
   reliability diagrams and Brier skill score.
8. Consistency check (services/hazards/consistency): cross-examines each high-probability
   cell against CAPE, CIN, cloud-top temperature, reflectivity and diurnal timing; emits
   agree / disagree with the evidence list; a disagreement lowers a `confidence` score.
9. Generalised feature contract for PyTorch and LightGBM models: persisted ordered
   feature names and training ranges; inference binds by name; out-of-range inputs flagged;
   a model without a contract is refused at load.
10. Severity ladder config table (IMD four colours) mapping probability, intensity and
    confidence to Yellow, Orange, Red, hot-reloadable and audited.

TESTS
- Physical unit tests: DCAPE from a hand-built sounding matches the expected value; MESH
  proxy on a synthetic column; Z-R conversion at known points; freezing-level lookup.
- Lightning jump on synthetic flash-rate series: fires on a planted jump, silent on noise
  (false alarm rate measured), minimum-rate guard works.
- CI detector: on labelled real events, lead gained versus first radar detection is
  reported with a confidence interval (may be zero; report it).
- Calibration: expected calibration error decreases on held-out data; calibrator fitted
  on validation only (leakage test).
- Feature contract: permuted column order gives identical output; missing feature raises;
  out-of-range (beyond 6 sigma) flagged; model without contract refused.
- Severity ladder: boundary values map to the right colour; hot reload changes the
  mapping and writes an audit entry.
- No-overclaim: every hazard payload carries `label_quality` and `skilful`; the API
  schema refuses a hazard without them.
- Benchmarks: hazard stage latency per scan on laptop to reports/bench/hazards.json.

GATE
1. Each hazard has a model card stating label quality, data, skill with confidence
   intervals, and limits. Hazards with insufficient labels are reported as such, and the
   system uses a physical-threshold method clearly labelled `rule_based`.
2. Reliability diagrams and Brier skill scores exist for every probabilistic output.
3. Consistency checker runs on replayed events and its disagreements are logged.
4. All tests pass; READMEs in template format.
```

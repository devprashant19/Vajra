# Vajra Playbook, Part 1: Phases 1-4 (Foundation and Data)

Run the phases in order. Paste only the text under each **PROMPT** heading into Antigravity. Each phase ends with a report you bring back.

---

## PHASE 1: Toolchain, monorepo, documentation skeleton, reference import

**Depends on**: audit phase (done). **Report**: `reports/PHASE_1_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md if it exists. If it does not, first copy the provided
MASTER_RULES.md from the playbook into docs/MASTER_RULES.md, then read it fully.
Also read _audit/AUDIT_SUMMARY.md, _audit/REFERENCE_AUDIT.md, _audit/reusable_modules.md,
_audit/coverage_matrix.md and _audit/environment.md.

OBJECTIVE
Create the Vajra monorepo with a verified toolchain, documentation skeleton, quality
gates, and a clean record of which reference assets may be used and how. No product
code yet.

TASKS
1. Locate the project root (the folder containing _audit/ and data/reference/). Do not
   create a second root. Confirm the five reference projects are untouched (compare
   against _audit/dataset_manifest.json hashes where present).

2. Toolchain verification (this is the most important task; the machine runs Python
   3.14.5 on Windows 11):
   a) Install uv. Try to install the key libraries on Python 3.14 and on Python 3.12
      in throwaway environments: numpy, scipy, xarray, zarr, dask, pandas, pyarrow,
      opencv-python-headless, scikit-image, torch (CPU and CUDA build for the GTX 1650),
      lightgbm, onnxruntime, pysteps, tobac, arm_pyart, pyiwr, satpy, pyresample,
      cfgrib (needs ecCodes), h5py, netCDF4, rasterio, geopandas, shapely, h3, pyproj,
      fastapi, sqlalchemy, asyncpg, redis, confluent-kafka or aiokafka, pytest, hypothesis.
   b) Record, per library and per Python version, whether it installs and imports.
   c) Decide and document in ADR-001: the pinned Python version (default 3.12), what
      runs natively on Windows, and what must run in Docker/WSL2 (expected: Py-ART,
      pyiwr, cfgrib, Satpy). Do not guess; base it on the results.
   d) Create the pinned environment with uv (pyproject.toml workspace, lock file) and
      a Dockerfile for the geo/ML services. Verify `docker build` works.
   e) Node: pnpm workspace for apps/web and packages/vajra-types. Pin versions.
      Check the latest stable versions of Next.js, React, Tailwind, MapLibre GL JS,
      deck.gl from the package registry instead of assuming them.

3. Scaffold the repository exactly as in docs/MASTER_RULES.md section 3. Each service
   directory gets a package skeleton, a README.md in the component template (section 4.2),
   and a placeholder test that passes.

4. Developer experience: a cross-platform task runner (use `just` or a Python task
   module that works on Windows; do not require `make`). Tasks: setup, lint, format,
   typecheck, test-fast, test-all, up-lite, up-full, down, clean. Add .editorconfig,
   .gitignore (never ignore .env.example), .env.example (names only), pre-commit with
   ruff, mypy, eslint, prettier, gitleaks, and the three tools below.

5. tools/: implement
   - check_readme_format.py: validates every README.md under data/, services/,
     packages/, ml/, apps/ against the templates in MASTER_RULES section 4 (heading
     order, required bold fields, Verdict vocabulary, presence of Usage Restrictions).
   - check_no_secrets.py: fails if a secret-like string or a real .env is tracked.
   - check_claims.py: skeleton that later verifies every number in docs/ traces to a file.

6. CI: GitHub Actions workflow running lint, typecheck, fast tests (Python and Node).
   docker-compose.yml with profiles `lite` and `full` (full adds Postgres+PostGIS+Timescale,
   Redpanda, MinIO, Redis). For now, services are placeholders with health endpoints.
   Validate with `docker compose config`.

7. Reference import review:
   a) Verify data/reference/* exists, matches the audit manifest by sha256, and that every
      folder has a README.md in the data template. Fix or create READMEs to match the
      exact format used by the existing ones (Origin, Copied, Contents with Verdict,
      Usage Restrictions).
   b) Create docs/THIRD_PARTY.md: one row per reference module/dataset from
      _audit/reusable_modules.md and dataset_manifest.json with licence, decision
      (PORT if MIT / REIMPLEMENT clean-room / REFERENCE-ONLY), and date. Mark the
      district GeoJSON and the i18n locale files as licence UNKNOWN / provenance UNVERIFIED.
   c) List the bugs recorded in the audit (Earthformer reshape at L123, GATv2 softmax
      dim=0, CAP digest is not a real signature, hard-coded NEXUS metrics) in
      docs/KNOWN_REFERENCE_DEFECTS.md so they are not reintroduced.

8. Documentation skeleton: README.md (project overview, honest status table listing
   every capability as NOT STARTED), ARCHITECTURE.md (Mermaid context diagram and
   service topology draft), PROGRESS.md, DECISIONS.md, docs/adr/ADR-001 (toolchain),
   ADR-002 (architecture decisions from MASTER_RULES section 2), docs/data/, docs/ops/,
   docs/ml/, docs/api/, docs/presentation/.

TESTS (all must pass offline)
- test_toolchain_smoke: imports every pinned library in the pinned environment and
  prints versions to reports/bench/toolchain.json.
- test_docker_geo_image: container builds and imports Py-ART/pyiwr/Satpy/cfgrib
  (mark `slow`).
- test_readme_format: runs check_readme_format.py over the whole repo; also has negative
  tests proving a malformed README is rejected.
- test_no_secrets: a planted fake secret in a temp file is detected; repo is clean.
- test_reference_untouched: hashes of reference source trees match the audit.
- test_compose_config: `docker compose config` succeeds for both profiles.
- CI workflow file validates (use actionlint if available).

GATE
1. `just setup` then `just test-fast` passes on a clean clone.
2. ADR-001 states the Python decision with install evidence in reports/bench/toolchain.json.
3. All READMEs pass the format checker; THIRD_PARTY.md covers every reference item.
4. pre-commit passes; gitleaks reports nothing.
5. PROGRESS.md and reports/PHASE_1_REPORT.md written using the template.
```

---

## PHASE 2: Contracts and platform kernel

**Depends on**: Phase 1. **Report**: `reports/PHASE_2_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md and reports/PHASE_1_REPORT.md.

OBJECTIVE
Build packages/vajra-core and packages/vajra-types: the shared contracts every later
service depends on, plus the database schema. Nothing else should be able to bypass
these contracts.

TASKS
1. Grid and geometry (packages/vajra-core/grid):
   - GridSpec for the national grid (68-98E, 6-38N, 0.02 degree, about 2 km) and a
     regional grid (0.01 degree, about 1 km). Decide the CRS (EPSG:4326 or an
     equal-area projection) in ADR-003 with the reasoning about cell area distortion.
   - Tile scheme: fixed 256x256 tiles with configurable overlap, global tile ids,
     functions latlon<->(row,col)<->tile id, neighbour lookup. This scheme is what lets
     inference and processing run across many workers.
   - H3 helpers (resolution 7 and 8) for location indexing.
2. Variable registry: name, unit, valid physical range, source group, dtype, fill
   value, for every field used later (reflectivity dBZ, VIL, echo top, BT 10.8 and 12.0,
   BTD, cooling rate, flash density, CAPE, CIN, shear, PWAT, freezing level, DCAPE,
   rain rate, etc.). Unit conversion helpers.
3. Time: UTC internally, IST for display. A `Clock` interface with RealClock and
   ReplayClock (set, advance, speed). No service may call datetime.now() directly.
4. Provenance: enum Status {live, cached, stale, simulated, unavailable,
   needs_credentials}; envelope `Provenanced[T]` with source, valid_time, ingest_time,
   age_seconds, status, quality_flags. Serialization must refuse a `simulated` payload
   labelled as an observation layer.
5. Schemas (Pydantic v2): RawEvent envelope, FusedFrameRef, Cell, CellTrack,
   CellForecast, HazardField, Location (admin unit, asset, H3 index, priority),
   ETA (p10/p50/p90, probability of impact, state), Alert (CAP-ready), AuditEntry,
   Threshold, ModelCard, VerificationResult, SourceHealth. Export JSON Schema and OpenAPI
   components, then generate TypeScript types into packages/vajra-types with a script;
   CI fails if generated files are out of date.
6. Abstractions with implementations:
   - ObjectStore: LocalFS, S3-compatible (MinIO/S3).
   - EventBus: InMemory, Redis Streams, Kafka API (Redpanda). Topics: raw.radar,
     raw.sat, raw.lightning, raw.nwp, raw.gauge, frames.fused, nowcast.ready,
     cells.updated, eta.updated, alerts.draft, alerts.issued. Consumer groups,
     partition keys, dead-letter topic, idempotency key (source, product, valid_time).
   - Cache: InMemory, Redis.
7. Database (packages/vajra-core/db): Alembic migrations for PostgreSQL + PostGIS +
   TimescaleDB: sources, scans, cells, cell_tracks, cell_forecasts, hazard_polygons,
   locations, eta, alerts, alert_audit (hash-chained), thresholds, users_roles,
   verification_results, model_registry. Spatial and time indexes. Hypertables for time
   series. A SQLite backend is allowed only for unit tests, behind the same repository
   interface.
8. Config: pydantic-settings; profiles lite/full/national from MASTER_RULES section 2;
   region registry as data files (pilot domains, radar lists) not code.
9. Error taxonomy and structured logging (JSON logs with correlation id).

TESTS
- Property tests (hypothesis): latlon<->grid index round-trips within half a cell;
  tile ids unique and cover the domain without gaps; overlap tiles stitch back to the
  original array; H3 round trip; unit conversions are invertible; timezone conversion.
- Schema round-trip (model -> JSON -> model) and JSON Schema validation for every schema.
- Provenance: test_regression_simulated_never_served_as_observation.
- Contract tests: one suite parameterised over every ObjectStore, EventBus and Cache
  implementation (idempotent publish, ordering within partition, consumer groups,
  dead-letter after N failures, replay from offset). Redis/Kafka/MinIO variants run in
  Docker and are marked integration.
- Migrations: upgrade, downgrade, upgrade again on an empty database; constraint tests;
  a spatial query uses the GiST index (check with EXPLAIN).
- Generated TypeScript types compile with tsc and match the schemas (drift test).
- Clock: replay clock drives a scheduler deterministically.

GATE
1. All tests pass; coverage on vajra-core at least 85%; mypy strict passes on vajra-core.
2. The same contract suite passes on InMemory and on at least one real bus/store in Docker.
3. `just up-full` starts Postgres/PostGIS/Timescale, Redpanda, MinIO, Redis and migrations apply.
4. ADR-003 (CRS and tiling) written. READMEs in template format for each package.
```

---

## PHASE 3: Real data acquisition and data lake

**Depends on**: Phase 2. **Report**: `reports/PHASE_3_REPORT.md`

The audit's most important finding is that none of the five projects holds real Indian radar volumes or INSAT Level-1B data. This phase decides what real data you can actually train and evaluate on. Expect to do some manual registrations yourself (see "Your part" below).

### Your part (do these while Antigravity works; it cannot do them for you)
1. MOSDAC account (free, may take 1-2 days): INSAT-3DR/3DS L1B and products.
2. NASA Earthdata login: IMERG precipitation and GPM-LIS lightning.
3. Copernicus CDS account and API key: ERA5.
4. Kaggle account and API token: the BharatBench dataset named in the SIH reference (verify that it exists).
5. If your college or mentors can help: a request to IMD for raw DWR volume scans, and to IITM for lightning data. Note the outcome, even if it is a no.
6. Put credentials only in your local `.env` (never in chat).

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_2_REPORT.md,
_audit/external_sources.md and _audit/dataset_manifest.json.

OBJECTIVE
Establish exactly which REAL data is obtainable for training, validation and demo, build
the tooling to acquire it reproducibly, and produce an honest data-coverage decision. Do
not substitute synthetic data for anything.

TASKS
1. Source verification. For every source in _audit/external_sources.md, check live whether
   the URL or identifier resolves (for example the figshare/Zenodo DOI the SIH README
   cites, Open-Meteo, GFS on NOMADS, MOSDAC portal, Earthdata, CDS, Kaggle BharatBench,
   SEVIR on its public bucket, Blitzortung terms). Produce docs/data/SOURCE_STATUS.md with:
   reachable or not, credentials needed, licence and terms text summary (quote nothing
   long), file formats, approximate sizes, time coverage. Anything you cannot verify is
   marked UNVERIFIED. Read terms of use and record any restriction (for example
   non-commercial or no redistribution).

2. Tiered strategy, recorded in docs/data/DATA_STRATEGY.md:
   - Tier 0: samples already in data/reference (pipeline testing, demo replay only).
   - Tier 1: public without login (verify which).
   - Tier 2: free with registration (MOSDAC, Earthdata, CDS, Kaggle).
   - Tier 3: restricted or research access (IMD raw DWR, ILLN, NCMRWF RDS).
   - Transfer-learning track: a bounded subset of the real US SEVIR dataset (radar VIL,
     IR channels, GLM lightning), selected from the catalog by season and storm type,
     size configurable (default cap 40 GB; ask before exceeding), used to pretrain and to
     validate the pipeline on real convective data. State plainly that SEVIR is US data and
     that Indian skill must be measured separately.
   - Label sources per hazard, with their limits (radar-derived future reflectivity;
     lightning network counts; hail proxies plus NOAA Storm Events hail reports for SEVIR
     events; wind reports for downburst proxies; IMERG and rain-gauge thresholds for
     cloudburst). Mark which labels are direct and which are proxies.

3. Acquisition tooling (services/ingest/archive): resumable, rate-limited, checksum-
   verified downloaders, one per source, credentials only from environment, `--dry-run`,
   size estimate before download, manifest.json written beside each download, and a
   README.md auto-generated in the data template (Origin, Downloaded, Contents with
   Verdict, Usage Restrictions). Missing credentials produce status `needs_credentials`
   and a clear message, never a crash or fake data.

4. Acquisition runbook docs/data/ACQUISITION_RUNBOOK.md: step by step instructions for
   the human for each registration and download, the exact environment variable names,
   expected file sizes and time, and how to verify the result.

5. Case-event library data/events/events.yaml: 15-30 Indian severe convective events
   (pre-monsoon thunderstorm and squall-line days, Kolkata nor'westers, cloudbursts in
   the Himalayan states, hail events, lightning-fatality days) plus SEVIR events for the
   transfer track. Include ONLY events for which you can cite a public source
   (IMD bulletin, NDMA report, reputable news) and record the citation URL, date, location
   and hazard type. Mark uncertain entries UNVERIFIED. Never invent an event.

6. Data lake layout: data/raw/<source>/<yyyy>/<mm>/<dd>/..., data/lake/ (Zarr),
   data/catalog/catalog.parquet (DuckDB-queryable) with one row per asset: source,
   product, valid time range, bbox, sha256, size, status, licence, verdict
   (REAL/REAL (rendered)/REAL but TINY/SYNTHETIC). Catalog builder scans the lake and
   validates rows.

7. Coverage profiling (ml/data_profile): for every event and modality compute what
   exists: radar scans per hour, satellite frames, lightning counts, NWP fields, gauges.
   Output reports/DATA_COVERAGE.md and coverage heatmaps (time x modality x region), all
   generated from the catalog.

8. Decision table at the end of DATA_COVERAGE.md, one row per modality and hazard:
   "Can we train on real Indian data: YES / PARTIAL / NO", volume available, label quality,
   and the fallback (for example SEVIR pretraining, ERA5-based heads, satellite-only
   outlook). This table drives Phases 7-9.

TESTS (offline unless marked live)
- Downloaders with mocked HTTP: resume after interruption, checksum mismatch is
  detected and quarantined, rate limit respected, 401/403 -> needs_credentials,
  partial file never published.
- Catalog: schema validation, duplicate detection by sha256, rejects rows without
  verdict, reproducible build.
- README generator output passes tools/check_readme_format.py.
- Events file: schema test; every event has a citation URL or an UNVERIFIED flag; dates
  and coordinates in valid ranges.
- Live tests (marked live, optional): head requests to each public URL; one tiny real
  download per Tier 1 source with checksum.
- Profiling: known toy catalog gives the expected coverage numbers.

GATE
1. SOURCE_STATUS.md covers every source with a verified or UNVERIFIED label.
2. At least one REAL multi-modal dataset (radar or VIL, satellite/IR, lightning) is
   downloaded and catalogued, even if it is the SEVIR subset; Indian real data counts are
   reported honestly.
3. DATA_COVERAGE.md and the decision table exist and are generated from the catalog.
4. All tests pass offline; data READMEs pass the format checker.
5. "Needs from the human" lists every pending registration or request.
```

---

## PHASE 4: Ingestion connectors, quality control and streaming

**Depends on**: Phase 3. **Report**: `reports/PHASE_4_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_3_REPORT.md and
reports/DATA_COVERAGE.md. You may read the reference implementations listed in
docs/THIRD_PARTY.md to understand behaviour, but write new code (clean-room) unless
THIRD_PARTY.md says PORT.

OBJECTIVE
Build the real-time ingestion layer: one connector per source, strict quality control,
publication to the event bus, and a replay connector that feeds archived real data
through the same code path as live data.

TASKS
1. Connector framework (services/ingest): base class with poll -> fetch -> validate ->
   publish; idempotency key (source, product, valid_time); exponential backoff with
   jitter; circuit breaker; dead-letter topic; quarantine folder for malformed files;
   Prometheus metrics (lag, success, failures, bytes); provenance status on every event;
   raw files stored untouched in the ObjectStore.
2. Connectors, each with QC:
   - Radar (IMD DWR): volume scans via pyiwr/Py-ART where real volumes exist; legend-
     driven decoding of public composite images as a clearly labelled low-precision
     fallback (status carries `quality=rendered`). QC: clutter and anomalous-propagation
     filtering, beam-blockage mask, range-dependent sensitivity, velocity dealiasing,
     attenuation flag. Output: per-radar polar or Cartesian sweeps with QC flags.
   - Satellite (INSAT-3D/3DR/3DS): L1B HDF5 to brightness temperature (Satpy) when
     available; browse-image fallback labelled `uncalibrated`. Navigation and georeference
     validation using the graticule burned into products (tolerance 0.1 degree), plus a
     regression test for each bug the audit lists (vertical flip, title-bar contamination).
   - Lightning: adapters for archive CSV, Blitzortung (respect its terms), GPM-LIS,
     and ILLN (credential-gated, status `needs_credentials` when absent). Deduplication,
     detection-efficiency map, rasterisation with numpy histogram binning (not KDE) to
     10-minute flash density.
   - NWP: Open-Meteo, GFS, ERA5, and NCMRWF IMDAA/NCUM adapters; derive CAPE, CIN,
     lifted index, 0-6 km shear, PWAT, freezing level, DCAPE, storm-relative helicity with
     unit checks.
   - Rain: IMERG and (if access exists) IMD AWS/ARG gauges.
3. ReplaySource: reads archived assets from the lake/raw store in valid-time order and
   emits them on the bus under a ReplayClock at adjustable speed. It must use the same
   publish path as the live connectors. This is the basis of the demo "Time Machine".
4. Health: each connector reports freshness and status to a `source_health` table and to
   `/health/sources` (API comes later; expose a function now).
5. Streaming topology: partition key = radar id or region tile; consumer group per service;
   document the topology in ARCHITECTURE.md and docs/ops/INGEST_RUNBOOK.md.

TESTS
- Unit QC tests with known truth (using synthetic fixtures in tests/fixtures/SYNTHETIC/):
  injected clutter spikes are removed; ring/beam-blockage regions masked; aliased
  velocity corrected; saturated pixels flagged.
- Real-sample integration tests using data/reference and the Phase 3 downloads: each
  connector ingests at least one real file end to end.
- Georeference test: graticule within 0.1 degree for satellite products;
  test_regression_satellite_vertical_flip and test_regression_title_bar_contamination.
- Idempotency: re-ingesting the same file produces no duplicate events.
- Fault injection: upstream 500s, timeouts, truncated files, wrong checksums, malformed
  headers: connectors recover, quarantine bad files, never crash the loop, status becomes
  `stale`/`unavailable` as appropriate.
- Kill test: stop a connector mid-download, restart, resume without duplicates.
- Replay equivalence: a replayed file yields byte-identical events to live ingestion of
  the same file.
- Throughput benchmark: events per second and MB per second per connector written to
  reports/bench/ingest.json with machine info.
- Provenance: no connector can emit `simulated` data on an observation topic.

GATE
1. Each connector either ingests real data end to end or reports `needs_credentials`
   with documented steps; nothing is faked.
2. Replay source drives the bus under ReplayClock; equivalence test passes.
3. All tests pass; benchmark file exists; READMEs in template format.
4. `just up-lite` ingests a replayed real event and shows events on the bus.
```

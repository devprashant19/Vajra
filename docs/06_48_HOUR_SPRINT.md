# Vajra 48-Hour Sprint

**Purpose**: The deadline is two days away, so the 17-phase schedule is replaced by four parallel sprints. They produce a working, polished, honest demo: a replay-driven platform where every number is labelled by its origin. Save this file as `docs/06_48_HOUR_SPRINT.md`. It overrides `docs/05_BUILD_FIRST_MODE.md` and the phase prompts wherever they conflict. The honesty rules in `docs/ENGINEERING_STANDARDS.md` and section 2 of `docs/05_BUILD_FIRST_MODE.md` stay in force.

---

## 1. What we are building in 48 hours

**Replay-bundle architecture.** An engine runs offline on four SIMULATED scenarios (and one real display-only replay) and writes "bundles": colourised field images per frame, cells, tracks, hazards, ETAs and alert drafts, all in the `contract-v1` JSON shapes. A small FastAPI service serves the bundles through the `/v1` endpoints and a WebSocket replay stream driven by a ReplayClock. The web app talks only to that API (or to static copies of the bundles for a hosted backup). This gives every screen live-feeling data while the full streaming pipeline stays a documented design.

**Why this is honest.** Each bundle carries `status: simulated`, `engine`, `method` and `skilful: unknown`, and the UI shows a SIMULATED watermark plus an engine banner. Real data appears in a separate "Real data" section and is labelled as real. The architecture documents separate IMPLEMENTED, DEMONSTRATED (simulated), DESIGNED and NOT STARTED.

**Problem-statement coverage.** Every requirement gets a visible, labelled output: multi-source fusion layers (radar, satellite, lightning, NWP fields), early convective initiation flag, lightning density and jump alert, hail probability, downburst gust estimate, cloudburst threshold exceedance, storm tracking, countdown clocks with uncertainty, an interactive GIS dashboard, CAP alerts, and a scalability design.

## 2. Frozen scope

**Build:** engine bundles (Sprint A), UI (Sprint B), API + alerts (Sprint C), real-data panel + docs + demo (Sprint D).

**Do not build or do:** full fusion at national scale, SEVIR extraction, model training, MOSDAC integration, Keycloak, Storybook, visual regression, Lighthouse CI, soak or chaos tests, Kubernetes runs, translation review. Describe them as DESIGNED or NOT STARTED where they appear.

**Contract rule:** `contract-v1` is frozen. Do not change schemas. If something is missing, add an optional field and note it in an ADR.

## 3. Sprint A: engine and bundles (conversation 1, branch track-a-engine)

### PROMPT

```
Read docs/ENGINEERING_STANDARDS.md, docs/05_BUILD_FIRST_MODE.md and docs/06_48_HOUR_SPRINT.md. This is Sprint A.
The deadline is in two days; work fast, commit after each step, do not push, do not create tags.

STEP 0 (30 minutes at most): CLEANUP AND MERGES
a) Delete the placeholder payloads for ERA5 and GPM-LIS in tests/fixtures/REAL; they are not real.
   Unit tests that used them switch to named SYNTHETIC fixtures.
b) data/events/events.yaml: remove the blanket http_status 200 and retrieval dates that were applied by
   script. Run tools/probe_sources.py over the citation URLs and write true results; failures or
   unprobed entries become UNVERIFIED.
c) The SEVIR option tables (12 files / 4.1 GB, 6 files / 2.0 GB) conflict with the measured 5.7 GB size
   of a single VIL file. Mark them ESTIMATE-UNVERIFIED in the reports and DATA_COVERAGE.md. Do not work
   on SEVIR further.
d) Never print .env contents again (no cat/type of .env).
e) Merge integrate/pr-1-benchmark and track-a-engine into main with merge commits. Resolve conflicts:
   regenerate uv.lock; keep the Python 3.12 pin; keep the events.yaml schema. Run fast tests,
   pre-commit and gitleaks. Then merge main into track-b-ui and track-c-platform. Report the result in
   five lines.

STEP 1: SCENARIO GENERATOR (extend SimulatedSource)
Gridded fields every 10 minutes for 4 hours over a small pilot domain (about 256x256 cells at 2 km),
for the four SIMULATED-* scenarios: reflectivity (dBZ), IR brightness temperature, 10-min flash density,
VIL, rain rate, and scalar instability fields (CAPE, CIN, DCAPE proxy, freezing level). Storms must
initiate, move, grow, decay, and occasionally split or merge; the generator also writes its own ground-
truth cell tracks. Seeded and deterministic. Real Indian city and airport coordinates near each
scenario's region are used for locations (30-50 per scenario: district headquarters, airports, a few
substations); mark them as example assets.

STEP 2: TRACKER
Connected components at >= 35 dBZ with area >= 24 km2, centroid, area, max dBZ, VIL, echo top, speed,
heading, trend; Hungarian matching between steps with split and merge handling.

STEP 3: BASELINE ENGINES
Persistence and Lagrangian optical-flow advection (Farneback, contrast-normalised) out to +120 min in
10-minute steps. Output NowcastResult with engine="optical_flow", skilful="unknown". Do not use any
random-valued fill.

STEP 4: RULE-BASED HAZARD HEADS (method="rule_based", label_quality="proxy", thresholds in config)
Convective initiation (split-window BTD, cooling rate, instability), lightning (flash density plus the
2-sigma jump detector on a sliding window), hail (VIL density and echo-top proxy), downburst gust
estimate (DCAPE proxy plus reflectivity-core descent), cloudburst (rain rate and area accumulation
thresholds; verify the IMD working definition from an official source and cite it in the config),
severity ladder (IMD four colours). Document every formula in docs/ml/RULE_BASED_HAZARDS.md.

STEP 5: ETA ENGINE
Monte Carlo trajectories (N=200, vectorised numpy, seeded) from each tracked cell, footprint growth or
decay, bounding-box prefilter per location, outputs p10/p50/p90 arrival, probability of impact within
15/30/60/120 minutes, impact duration, dominant hazard, and the state machine WATCH / APPROACHING /
IMPACT / CLEARING / CLEARED / STALE with hysteresis. Absolute timestamps.

STEP 6: BUNDLE WRITER
For each scenario write demo/bundles/<scenario_id>/ with manifest.json (scenario, SIMULATED, engine,
domain bounds, frame times, legends), frames/<layer>/<time>.png (colourised, with known geographic
bounds, observed and forecast leads), cells.json, tracks.json, hazards.json, eta.json, alerts_drafts.json,
all in contract-v1 shapes with provenance (status simulated, engine, method, skilful unknown). Add a
fifth bundle REAL-radar-2018-01-11 from the 70 real PNGs: type real_display_only, quality rendered,
georeferenced false, frames as images, plus the decoded-dBZ histogram; no forecasts for it.
`just bundles` regenerates everything deterministically in under 10 minutes.

STEP 7: SIMULATED VERIFICATION (demo content only)
Compute CSI/POD/FAR at 35 dBZ by lead time for optical flow versus persistence against the generator's
ground truth, and write demo/bundles/<scenario>/verification.json with the flag
"simulated_not_evidence": true. Never cite these numbers as performance.

STEP 8: TESTS (keep it lean)
Tracker on synthetic moving blobs (including split and merge); ETA analytic case (constant-velocity
cell gives the exact arrival; zero uncertainty collapses the window); bundle schema validation against
contract-v1 for every file; determinism (same seed, identical hashes); no use of random-valued fill in
the radar decoder path; a benchmark file reports/bench/engine.json with machine info. Run fast tests.

DELIVERABLE: write reports/SPRINT_A_REPORT.md (what exists, test counts, benchmark, known limits) and
stop. If time runs short, finish steps in order and report what is done; steps 1-3, 5 and 6 are the
critical path.
```

## 4. Sprint B: UI (conversation 2, branch track-b-ui)

### PROMPT

```
Read docs/ENGINEERING_STANDARDS.md, docs/05_BUILD_FIRST_MODE.md, docs/06_48_HOUR_SPRINT.md, and the Phase 12-14
sections of docs/03_PHASES_10-14_ETA_BACKEND_UI.md (design language and screens). This is Sprint B. The
deadline is in two days. Work only in the track-b-ui worktree; commit after each priority; do not push;
no tags. The connection is slow: install dependencies once and reuse the pnpm store. Verify the latest
stable package versions from the registry.

DATA SOURCE: the contract-v1 API. Until Sprint A and C land, use MSW mock handlers generated from
docs/api/examples/, all labelled SIMULATED. Later, the same code reads the real API or static copies of
demo/bundles/ (build a data layer with one adapter interface and two implementations: api and static).
The app must be able to export statically (`next build` with static export) with bundles in /public, so a
hosted backup demo works without a server.

PRIORITIES (commit and test after each; a partial result must still be demoable)
P1 SHELL AND MAP: dark-first design system (tokens, typography with a UI sans and a monospaced
   tabular-numeral face, translucent panels, IMD four-colour severity with icons, colour-blind safe,
   light theme too). Top bar with source-health lights and provenance badges, IST and UTC clock,
   language selector, theme toggle, replay switch. MapLibre with a neutral basemap with NO
   administrative boundary layer (hide the boundary layers in the style; test it). Image-source layers for
   radar, satellite, lightning, hazard fields with opacity and legends; deck.gl for cells, tracks,
   uncertainty cones, locations. Timeline dock (-2 h to +4 h) with play, pause, speed, scrub, step,
   forecast hatching, keyboard control, URL-encoded view state. Command palette (Ctrl+K) to jump to a
   place or scenario. SIMULATED watermark, engine banner and skilful-unknown banner always visible on
   forecast layers.
P2 COUNTDOWN AND INSPECTOR: ranked countdown rail with circular rings, p10-p90 range bars, state
   colours, local ticking from absolute timestamps (correct after pause/seek/reconnect, never negative),
   pin/filter/search, click flies to the location. Cell inspector side sheet: gauges (dBZ, VIL, echo
   top, flash rate), hazard bars with method and label-quality badges, "why this warning"
   (inputs behind the rule, agreements and disagreements), affected locations with ETAs, "Draft alert".
P3 ALERT COMPOSER: draft list, polygon on the map, severity chooser, message preview, approval workflow
   with role switch, CAP XML view, history with audit trail; approval is blocked with an explanation
   while skilful is not "true" unless an admin records a reason.
P4 SCENARIO AND DATA PAGES: scenario picker (the four SIMULATED scenarios plus the REAL display-only
   radar replay with its own "REAL (rendered), not georeferenced" label), data-health page, verification
   page that shows the simulated verification with a clear "SIMULATED, not evidence" banner, model
   cards page showing engine, method, skilful and label quality.
P5 PUBLIC MOBILE PAGE /m: location pick, one big plain-language countdown with the window, hazard icon
   and safety actions, forecast-reliability notice, offline cache of the last state, installable PWA,
   language switch: 13 locale files from your own keys; English and Hindi written carefully, the rest
   machine-drafted and flagged in metadata; RTL for Urdu.
P6 LANDING PAGE /: striking hero (animated storm cells and lightning; a lazy-loaded WebGL or canvas
   visual is fine, never loaded in the ops app), what Vajra does in 10 seconds, four data sources,
   honest status, link to the app. Static export friendly.

SKIP: Storybook, visual regression, Lighthouse CI, full accessibility audit. KEEP: lint and typecheck,
about 10 Vitest tests (countdown logic, time controller, URL state, provenance banner rules), 3
Playwright smoke tests (load, play the timeline, open an inspector), axe on two pages, performance
sanity (60 fps pan with default layers on the laptop; record a number in reports/bench/ui.json).

DELIVERABLE: reports/SPRINT_B_REPORT.md with what is done per priority, screenshots in
docs/ui/screenshots/, test counts, and the build output size. Stop after P6 or when told.
```

## 5. Sprint C: API and alerts (conversation 3, branch track-c-platform)

### PROMPT

```
Read docs/ENGINEERING_STANDARDS.md, docs/05_BUILD_FIRST_MODE.md, docs/06_48_HOUR_SPRINT.md, docs/api/openapi.json
(tag contract-v1) and the Phase 11 and 15 sections of the playbook. This is Sprint C. The deadline is in
two days. Work in the track-c-platform worktree; commit after each step; do not push; no tags.

1. API: FastAPI implementing every /v1 path of contract-v1 by serving demo/bundles/ (until Sprint A
   delivers them, use docs/api/examples/). Every response carries the provenance envelope. Pagination,
   ETag, error model, request ids. Endpoints: status, health/sources, cells, cells/{id}, eta,
   locations/{id}/eta, hazards and image-layer URLs, alerts (list, create, approve, cancel), verification,
   models, replay events and control, thresholds/admin. Serve the layer images with immutable URLs.
2. STREAM: WebSocket and SSE /v1/stream under a ReplayClock: message types cell.updated, eta.updated,
   alert.issued, source.status, replay.state; sequence numbers, resume from the last sequence, heartbeat,
   bounded per-client queues. Replay control: start, pause, seek, speed, per session.
3. AUTH: simple JWT with roles admin, forecaster, viewer, public, and the RBAC matrix from the contract.
   Demo users created locally by a script (no committed secrets). Keycloak is out of scope.
4. ALERTS: CAP 1.2 generator written from the OASIS specification, validated against the official XSD,
   signed with a real XML-DSig signature (use a maintained library; dev key generated locally and
   ignored by git). Rule-based draft creation from the ETA/hazard bundles, lifecycle messages (Alert,
   Update, Cancel) with references, 20-minute deduplication under the ReplayClock, approval workflow
   (draft, pending, approved, dispatched, rejected, cancelled) with role checks, hash-chained audit log
   (repository interface; SQLite for the demo profile, PostgreSQL when available), kill switch that
   freezes dispatch within a second. Dispatch goes to a mock webhook and the Web Push stub only, and says
   so. Alerts drafted while skilful is not "true" are flagged and need an admin reason to approve.
5. TESTS (lean): every endpoint's response validates against the OpenAPI document; CAP XSD validation for
   Alert/Update/Cancel; signature verifies and fails after tampering; audit chain tamper detection; RBAC
   matrix for alert endpoints; dedup timing under the ReplayClock; kill switch latency; WebSocket
   ordering and resume. Record numbers in reports/bench/api.json.
6. DEMO PROFILE: docker compose profile `demo` (api and web only) and `just demo` that starts the API on
   the bundles and the web build, with no credentials or internet. If Docker is slow, provide a no-Docker
   script as well.
7. DOCS: docs/api/README.md updates, docs/ops/ALERT_GOVERNANCE.md, docs/ops/HUMAN_OVERSIGHT.md,
   docs/ops/THREAT_MODEL.md (short STRIDE table), SOPs for source outage and false alarm (half a page each).

DELIVERABLE: reports/SPRINT_C_REPORT.md with PASS/FAIL per step and pasted evidence. Stop.
```

## 6. Sprint D: real-data panel, docs, demo (starts when A and B have output; run in conversation 1 or 4)

### PROMPT

```
Read docs/ENGINEERING_STANDARDS.md, docs/05_BUILD_FIRST_MODE.md, docs/06_48_HOUR_SPRINT.md and the reports of
Sprints A-C. This is Sprint D. Commit often, no push, no tags.

1. REAL DATA PANEL (data for the "Real data" page; everything labelled REAL with source and limits):
   a) the 70 real radar PNG previews as a replay with the decoder's precision note and the dBZ histogram;
   b) the real Tamil Nadu monsoon-2024 instability series from data/reference (CAPE, CIN, shear,
      PWAT) as time-series charts, with the provenance and licence notes from its README;
   c) at most two tiny real pulls (Open-Meteo or ERA5 and IMERG) for events whose citations resolved,
      each with a data-template README.
   Write them as JSON/PNG into demo/real/ and tell Sprint B's UI the schema.
2. DOCS in the project format (templates in docs/ENGINEERING_STANDARDS.md section 4): root README.md (what Vajra is,
   an honest status table with IMPLEMENTED / DEMONSTRATED (simulated) / DESIGNED / NOT STARTED per
   capability, quick start for `just demo`, layout), ARCHITECTURE.md (Mermaid diagrams: the target
   national architecture, and a separate diagram of what runs in the demo), ADRs updated, a README.md in
   each component directory passing tools/check_readme_format.py, docs/THIRD_PARTY.md finalised.
3. SCALE DESIGN (labelled DESIGNED, not tested): docs/ops/NATIONAL_DESIGN.md (partitioning by tile and
   radar, bus topics, stateless workers, GPU batching, Zarr tiers, tile CDN, client-side clocks), and a
   back-of-envelope capacity model labelled MODELLED using the measured engine benchmark constants from
   reports/bench/engine.json; keep every number traceable to a file.
4. CLAIMS CHECK: run tools/check_claims.py (make it enforce: no numbers without a source file);
   remove any unsupported figures from README, docs and the landing page text.
5. DEMO PACKAGE in docs/presentation/: DEMO_SCRIPT.md (5 minutes, first sentence states that the main
   scenarios are SIMULATED and the engine is the optical-flow baseline), a Q&A sheet with honest answers
   drawn from project files, a slide outline, and a fallback plan (static hosted build, recorded video).
6. CLEAN CLONE TEST: clone to a temp directory and follow the README to `just demo`; report time and
   friction. Report the exact limits (what is demonstrated, what is designed).

DELIVERABLE: reports/SPRINT_D_REPORT.md. Stop.
```

## 7. Hour plan (T0 = now)

| Hours | You | Conversation 1 (A) | Conversation 2 (B) | Conversation 3 (C) |
|---|---|---|---|---|
| 0-1 | Merge instructions, rotate token, send three prompts | Step 0 cleanup and merges | P1 | Steps 1-2 |
| 1-12 | Review reports, answer questions, sleep block 1 (4-5 h after hour 8) | Steps 1-6 | P1-P2 | Steps 3-5 |
| 12-24 | Check what runs; fix blockers | Steps 7-8, then Sprint D part 1 | P3-P4 | Steps 6-7, then wire to bundles |
| 24-30 | Integration: API serves A's bundles, UI reads the API | Fix engine issues | P5 | Fix API issues |
| 30-38 | Feature freeze at hour 36; Sprint D docs and demo; static hosted backup | Sprint D | P6, polish | Hardening |
| 38-46 | Deck, video, rehearsal twice, clean-clone test, submit | Support | Support | Support |
| 46-48 | Buffer only | | | |

**Cut order if behind** (first cut first): landing page globe visual, P5 languages beyond English and Hindi, simulated verification page, SSE (keep WebSocket), command palette, alert update/cancel messages, Docker (use the no-Docker script). Never cut: SIMULATED/engine/skilful labels, the map with timeline, the countdown rail, the cell inspector, the alert composer with CAP, the README with the honest status table, the demo script, the static hosted backup.

## 8. What you can claim in the demo and the pitch

Say: Vajra is a working end-to-end prototype: a replay-driven platform with tracking, a baseline nowcast, rule-based hazard estimates for lightning, hail, downburst and cloudburst, an early-initiation flag, a countdown engine with uncertainty, an alert workflow with audit and standards-compliant signed CAP messages, and a scalable architecture documented in detail. Each output shows its engine and method. The main scenarios are simulated, and real data is shown separately and labelled. ML training is the next step on the already built data pipeline.

Do not say: that the model is accurate or validated, that hail, downburst or cloudburst outputs are verified, that the scale design has been load-tested at national level, or that a simulated scenario is an observation.

## Usage Restrictions
This plan changes scope and order only. It does not relax the honesty, licence, secrecy or safety rules in `docs/ENGINEERING_STANDARDS.md`.

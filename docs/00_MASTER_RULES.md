# Vajra Master Rules

**Purpose**: Standing rules for every Antigravity phase prompt. Save this file in the project root (the SIH_2026 workspace folder that already contains `_audit/` and `data/reference/`) as `docs/ENGINEERING_STANDARDS.md`. Every phase prompt begins with "Read docs/ENGINEERING_STANDARDS.md, PROGRESS.md and DECISIONS.md first."

**Project**: Vajra, a real-time convective-scale nowcasting platform for SIH 2026 problem 26084 (MoES / NCMRWF). It predicts thunderstorms, lightning, hail, downburst winds and cloudbursts for 0-6 hours at 1-3 km, fuses Doppler radar, INSAT-3D/3DR/3DS, lightning and NWP data, and shows hazard zones with live countdown clocks on an interactive GIS dashboard.

---

## 1. Non-negotiable rules

### 1.1 Honesty
- Never fabricate a number, dataset, test result, file, URL or citation. If you did not measure it, write UNVERIFIED.
- Every quantitative claim in any document (README, report, model card, UI text) must be generated from a results file under `reports/` or `data/` and carry the file path as its source. A script `tools/check_claims.py` fails the build if a number in `docs/` has no traced source.
- Synthetic data is allowed only for unit tests and UI development, must be labelled `SYNTHETIC` in the path, the README, and the provenance status (`simulated`), and must never appear in skill tables, verification reports or the demo as observation.
- The audit showed a model with MAE 0.47 dBZ and CSI 0.000. Never optimise, select checkpoints by, or report continuous error alone. Report POD, FAR, CSI, HSS, Brier skill score, FSS and reliability, against persistence and optical-flow baselines.
- The test set is used once per model version. Log each use in `reports/test_set_usage.jsonl`. Tune only on train and validation data.

### 1.2 Safety of the workspace
- The five reference projects (SIH, NEXUS-NOWCAST, AeroCast-Now-AI, SIH-NowCasting, STORMTRACE) are READ-ONLY. Never modify, move or delete anything in them.
- Never print, copy or commit secrets. The audit found committed `.env` files in the references: do not copy them. Only `.env.example` with variable names is allowed. Pre-commit runs `gitleaks`.
- Do not create accounts, accept terms, or enter credentials on the human's behalf. When a step needs a login, stop and list it under "Needs from the human" in the report.
- Do not download more than 5 GB in one step without asking. Show the size estimate first.
- Do not run destructive commands (recursive delete outside the project, disk formatting, killing unrelated processes).

### 1.3 Licences and originality
- Reference projects other than NEXUS-NOWCAST (MIT) have no licence file, which means all rights reserved. Default rule: read them to understand the behaviour, then write NEW code from the algorithm or standard (clean-room). Do not paste their code or text.
- NEXUS-NOWCAST (MIT) code may be ported with the copyright notice kept.
- If the human records written permission from a reference team in `docs/THIRD_PARTY.md`, ported code from that team is allowed and must carry an attribution header.
- Every ported, reimplemented or reference-only item gets a row in `docs/THIRD_PARTY.md` (source path, licence, decision, date).

### 1.4 India boundaries
- Only Survey of India depictions (via ISRO Bhuvan or an official SOI source) may be drawn as India's boundary. The district GeoJSON found in the audit has unclear provenance and is treated as UNVERIFIED until Phase 5 replaces or verifies it.
- The basemap must not draw any country boundary layer. Boundaries come only from the verified Vajra boundary package. A test prevents adding any foreign fallback.

### 1.5 Working method for every phase
1. Read `docs/ENGINEERING_STANDARDS.md`, `PROGRESS.md`, `DECISIONS.md`, and the latest `reports/PHASE_*_REPORT.md`.
2. Write `plans/PHASE_<N>_PLAN.md` (tasks, files, risks, test list) and show it. Continue unless a blocking question exists.
3. Implement in small commits (conventional commit messages). Write the tests together with the code, not afterwards.
4. Run the full phase test list plus all earlier phases' fast tests (regression).
5. Write `reports/PHASE_<N>_REPORT.md` using the template in section 7, update `PROGRESS.md`, and stop.
6. If any gate item fails, fix it before writing "PASS". Never mark a gate item PASS without evidence.

---

## 2. Environment facts and decisions

**Machine (from `_audit/environment.md`)**: Windows 11, i7-10750H (6 cores), 15.9 GB RAM (about 3.4 GB was free), GTX 1650 4 GB, 322 GB free disk, Python 3.14.5, Node 22, Docker available, no conda.

- **Python**: Python 3.14 probably lacks wheels for parts of the scientific stack (Py-ART, pyiwr, Satpy, pySTEPS, torch builds, cfgrib). Phase 1 tests this. Default decision: use `uv` to install and pin Python 3.12 (fallback 3.11) for all backend and ML code, and use Docker (Linux containers) or WSL2 for the geo stack that needs ecCodes/HDF5. The frontend runs natively.
- **Profiles** (one codebase, three sizes, selected by `VAJRA_PROFILE`):
  - `lite`: laptop. One pilot region, CPU or small GPU, filesystem object store, Redis Streams bus, 1 worker each.
  - `full`: single server or small cloud node. Redpanda/Kafka, MinIO, Postgres/PostGIS/Timescale, GPU inference worker.
  - `national`: Kubernetes. All of India, partitioned by tile and radar, autoscaled workers, S3-compatible store, CDN for tiles.
- **Training**: the 4 GB GPU is for smoke tests, small models and inference. Every training script must also run on a rented or free cloud GPU with only a config change (`--profile cloud`), reading shards from object storage.

### Architecture decisions (and where they differ from the audit's suggestions)

| Area | Decision | Reason |
|---|---|---|
| Backend | Python 3.12, FastAPI, Pydantic v2, stateless services | Matches the geo/ML ecosystem |
| Bus | `EventBus` interface. Redis Streams in `lite`, Redpanda/Kafka API in `full` and `national` | Audit suggested Redis Streams only; Kafka API gives partitions and replay at national scale |
| Gridded store | Zarr on an `ObjectStore` interface (local FS, MinIO, S3) | From audit |
| Structured store | PostgreSQL + PostGIS + TimescaleDB | Audit suggested SQLite; SQLite does not scale to concurrent national workloads. SQLite only for unit tests |
| Hot state | Redis | Latest frame, pub/sub fan-out |
| ML framework | PyTorch (+ Lightning if it installs cleanly), LightGBM for cell-level heads, ONNX Runtime for serving | From audit, extended |
| Models | Residual learning on an advection baseline; multimodal ConvLSTM with availability-gated fusion (design idea from STORMTRACE, reimplemented); Earthformer-lite optional; no graph neural network | Proven, small enough for a 4 GB GPU, explainable |
| Frontend | Next.js + TypeScript + Tailwind + shadcn/ui + MapLibre GL + deck.gl | Audit suggested React + OpenLayers; MapLibre/deck.gl renders many animated raster and vector layers in WebGL and scales better |
| Three.js globe | Landing page hero only, lazy loaded | Audit: not operationally useful |
| i18n | i18next with own locale files for 13 languages | Reference translations have unclear licence; use only as terminology reference |
| Deployment | Docker Compose (`lite`, `full`), Helm/Kubernetes (`national`) | National scale |

---

## 3. Repository layout

```
<project root>/
├─ README.md                 project overview, quick start, honest status
├─ ARCHITECTURE.md           diagrams (Mermaid), data flow, decisions summary
├─ PROGRESS.md               one line per phase: status, date, report link
├─ DECISIONS.md              index of ADRs
├─ plans/                    PHASE_<N>_PLAN.md
├─ reports/                  PHASE_<N>_REPORT.md, bench/, verification/
├─ _audit/                   (existing) reference audit, read-only
├─ apps/
│  ├─ web/                   Next.js ops dashboard + public PWA
│  └─ api/                   FastAPI gateway
├─ services/                 ingest, fusion, nowcast, hazards, tracker, eta, alerts, verify
├─ packages/
│  ├─ vajra-core/            schemas, grid, units, provenance, bus/store abstractions
│  ├─ vajra-geo/             boundaries, projections, H3, tiling
│  └─ vajra-types/           TypeScript types generated from schemas
├─ ml/                       datasets, models, training, evaluation, model cards
├─ infra/                    docker-compose, helm, grafana, k6, chaos
├─ data/
│  ├─ reference/             (existing) copied reference data, each with README.md
│  ├─ raw/  catalog/  events/  lake/  derived/
├─ docs/                     adr/, data/, ops/, api/, ml/, presentation/, THIRD_PARTY.md
├─ tools/                    check_readme_format.py, check_claims.py, check_no_secrets.py
└─ tests/                    cross-service integration and end-to-end tests
```

---

## 4. Documentation standard (same format as the existing reference READMEs)

Every directory under `data/` and every `services/*`, `packages/*`, `ml/*` and `apps/*` directory gets a `README.md`. A script `tools/check_readme_format.py` validates them and runs in CI and pre-commit.

### 4.1 Data README template (exact structure)

```markdown
# <Name> Reference Data

**Origin**: <path or URL> (<short context>)
**Copied**: <YYYY-MM-DD>

## Contents

### <relative/path> (<size>)
- **Verdict**: REAL | REAL (rendered) | REAL but TINY | SYNTHETIC — <one-line evidence>
- **Time Range**: <range>
- **Domain**: <region>
- **Variables**: <list>
- **Shape**: <dims>
- **Useful for**: <training, validation, demo replay, unit tests>
- **Source**: <portal, product>
- **Licence**: <name or UNKNOWN>
- **Note**: <caveat>

## Usage Restrictions
<One paragraph: licence status, terms, what must be verified before official use.>
```

Rules: use `**Copied**` for copied data, `**Downloaded**` for downloaded data, `**Generated**` for generated data. Include only the bullet lines that apply, but always `Verdict`. Heading levels and ordering must not change. Dates use the real current date.

### 4.2 Code and service README template (same skeleton)

```markdown
# <Component> Module

**Origin**: NEW | REIMPLEMENTED from <reference path> (clean-room) | PORTED from <path> (MIT)
**Created**: <YYYY-MM-DD>

## Contents

### <relative/path> (<LOC> lines)
- **Verdict**: NEW | REIMPLEMENTED | PORTED — <one-line status, e.g. "tested on real data" or "tested on SYNTHETIC fixtures only">
- **Purpose**: <what it does>
- **Inputs / Outputs**: <types and shapes>
- **Tests**: <test file, pass count>
- **Note**: <limits>

## Usage Restrictions
<Licence, data terms, known limits, what is not validated.>
```

### 4.3 Other documents
- `ARCHITECTURE.md`: Mermaid diagrams for system context, data flow, service topology, deployment per profile, and the countdown pipeline; a table of decisions with links to ADRs.
- `docs/adr/ADR-<nnn>-<slug>.md`: context, decision, alternatives, consequences, date.
- `docs/ops/`: runbooks per failure mode. `docs/ml/`: model cards and dataset cards. `docs/api/`: generated OpenAPI plus examples.

---

## 5. Testing standard

- Python: `pytest` with markers `unit`, `integration`, `live` (needs network or credentials, off by default), `gpu`, `slow`, `bench`. Fast suite (`unit` + `integration` without live) must run offline in under 10 minutes on the laptop.
- Coverage targets: 85% for `vajra-core`, 75% for services. Type checking with `mypy` (strict for `vajra-core`). `ruff` for lint and format.
- Frontend: Vitest and React Testing Library for components, Playwright for end-to-end and visual regression, `axe` for accessibility, Lighthouse CI for performance budgets.
- Every bug found gets a regression test named `test_regression_<short_bug_name>`.
- Property-based tests (`hypothesis`) for grids, time, units, geometry and metrics.
- Performance tests write JSON to `reports/bench/` with machine info, so numbers are comparable and cited, never invented.
- Tests must be deterministic (fixed seeds). No test may depend on wall-clock "now"; use the injected `Clock`.
- Contract tests: the same suite runs against every implementation of an interface (`ObjectStore`, `EventBus`, `Cache`).

---

## 6. Design principles that apply to all phases

- **Scale by design**: stateless services, partitioning by tile and radar, idempotent handlers keyed by `(source, product, valid_time)`, backpressure, dead-letter queues, no global mutable state.
- **Replay equals live**: every service takes a `Clock` and reads from the same interfaces, so a replayed historical event uses the identical code path as live operation.
- **Provenance everywhere**: every payload carries `status` in `{live, cached, stale, simulated, unavailable, needs_credentials}`, `valid_time` and `age_seconds`. The UI renders it.
- **Graceful degradation**: a missing source reweights or falls back and says so in the API and the UI. It never silently substitutes simulated data.
- **Human in the loop**: no public alert is issued without forecaster approval.
- **Config over code**: regions, thresholds, severity ladders, languages and lead times live in versioned config tables.

---

## 7. Phase report template (`reports/PHASE_<N>_REPORT.md`)

```markdown
# PHASE <N> REPORT: <title>

**Date**: <YYYY-MM-DD>
**Commit**: <hash>

## Summary
<at most 10 lines, plain language>

## What was built
<tree of created paths with one-line purpose>

## Decisions and deviations
<links to ADRs; anything different from the prompt and why>

## Test results
| Suite | Command | Passed | Failed | Skipped | Duration |
|---|---|---|---|---|---|

## Measured numbers
<only values read from files; cite each file path>

## Gate checklist
| # | Gate item | PASS/FAIL | Evidence (path or command) |
|---|---|---|---|

## Known issues and tech debt
<honest list>

## Needs from the human
<credentials, downloads, decisions, approvals>
```

The human pastes the full report (plus logs of any FAIL) back to the architect, who writes the next phase prompt from what was actually built.

---

## 8. Resume and recovery prompts

**Resume in a new conversation**: "Read docs/ENGINEERING_STANDARDS.md, PROGRESS.md, DECISIONS.md and the latest reports/PHASE_*_REPORT.md. Summarise the state in 15 lines, list the open gate items, then wait for my next instruction."

**Fix a failed gate**: "Gate item <X> of Phase <N> failed with this output: <paste>. Diagnose the root cause, add a regression test that fails first, fix it, rerun the full Phase <N> test list and all earlier fast tests, then update reports/PHASE_<N>_REPORT.md."

**Stuck on missing data**: "Do not substitute synthetic data. Report exactly what is missing, what you tried, and the smallest real dataset that would unblock this phase."

---

## Usage Restrictions
These rules describe how the project is built. They carry no data of their own. Numbers quoted from the audit (machine specs, findings) come from `_audit/` and must be refreshed if the machine changes.

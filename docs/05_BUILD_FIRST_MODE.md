# Vajra Build-First Mode

**Purpose**: Addendum to `docs/MASTER_RULES.md` and the phase prompts. The deadline is near, so the whole system is built end to end first and the models are trained afterwards. This file re-scopes each phase, says what runs while the models are untrained, and keeps the honesty rules intact. Save it as `docs/05_BUILD_FIRST_MODE.md`. Where it conflicts with a phase prompt, this file wins; where it is silent, the phase prompt and the master rules apply.

---

## 1. The decision

1. Build Phases 4 to 17 now, working end to end on a replayed or simulated event.
2. Training is a separate track (Track T). The training code, the data builder and the evaluation code are built and smoke-tested now. The real training runs later on a cloud GPU when real data is in place.
3. Until a trained model passes its evaluation, the forecast engine is the optical-flow baseline, and the hazard outputs are rule-based and labelled so.
4. The product must work, look excellent and be honest about what drives each number. A working system with an honest label beats a trained-looking one that cannot be defended.

## 2. Honesty guardrails that stay (non-negotiable)

- **No fabricated skill.** No metric, accuracy figure or "model performance" may appear anywhere unless it was computed from a results file on real data. Baseline skill is reported only on the real data that exists, and labelled with that dataset.
- **Engine label.** Every forecast layer carries `engine` in its provenance (`persistence`, `optical_flow`, `pysteps`, `ml:<model_id>`). The UI shows it in the layer legend and the cell inspector. Every hazard output carries `method` (`rule_based` or `ml:<model_id>`) and `label_quality` (`direct`, `proxy`).
- **Skill flag.** The `skilful` flag is a three-state value: `true`, `false`, `unknown`. Untrained or unevaluated models are `unknown`, and the UI shows the same visible banner as for `false`. Alerts in the composer follow the Phase 13 and 15 rules for non-true values.
- **Simulated data.** A simulated scenario is allowed for demonstration only if all of this holds: status `simulated` in provenance, a visible SIMULATED watermark on the map, the countdown rail and the public app, the scenario name beginning with `SIMULATED-`, and the demo script saying so in the first sentence. Simulated data never enters verification tables, dataset cards, skill claims or the idea document as evidence.
- **Test set rule, claims registry and no-secrets rules** from the master rules still apply.

## 3. Phase 3 waiver (recorded, not passed)

Gate 2 of Phase 3 (a real multi-modal dataset downloaded and catalogued) stays OPEN. Record it as `WAIVED by human decision for build-first mode` in `reports/PHASE_3_REPORT.md` and in an ADR, with the unblock steps. Everything else in Phase 3 must be PASS before the phase is merged and tagged. Data work continues as Track D (below) and does not block Phases 4 to 17.

## 4. Engines while the model is untrained

- Define a `NowcastEngine` interface that returns the `NowcastResult` schema. Implementations: persistence, optical flow (Lagrangian, default), pySTEPS (if it installs), `MLEngine` (loads a registered checkpoint with a model card).
- The `MLEngine` is complete and tested with a tiny SYNTHETIC checkpoint, but is disabled in configuration until a real checkpoint has a model card and an evaluation. Switching it on is a config change plus a registry entry.
- Hazard heads are rule-based first: convective initiation from satellite and instability rules, lightning from flash density plus the 2-sigma jump detector, hail from a VIL-density and echo-top proxy rule, downburst from DCAPE and reflectivity-descent rules, cloudburst from rain-rate and area-accumulation thresholds. All carry `method: rule_based`, thresholds in config, and a model card that says what they are. The ML heads (LightGBM or CNN) are coded behind the same interface and trained later in Track T.

## 5. Data for the demo, in order of preference

1. **Real replay.** Use real data that exists: the STORMTRACE radar previews (70 rendered PNGs, qualitative only, label `quality=rendered`), ERA5 and Open-Meteo real data for the Indian events with verified citations, the real SEVIR sample when the cloud extraction arrives, and any MOSDAC file that downloads. Real replay is the headline demo whenever the data allows.
2. **SimulatedSource.** A scenario generator that emits physically plausible convective scenarios (storm initiation, motion, growth and decay, splits, merges, lightning, instability fields) through the same event bus as real data, with status `simulated`. Build four scenarios named `SIMULATED-<region>-<type>` (for example a Kolkata nor'wester, a Himalayan cloudburst, a Vidarbha hail day, a Delhi dust-storm-with-downburst). It exists so that every screen, the countdown engine, the alert workflow and the load tests can be demonstrated and tested end to end, and so the UI can be developed while real data is pending.

## 6. Scope per phase in build-first mode

| Phase | Build now (must) | Deferred to Track T or later |
|---|---|---|
| 3 (finish) | Tooling, source status, events with verified citations, catalog and coverage report from what exists, tests, READMEs; waiver recorded | Real SEVIR and Indian downloads (Track D) |
| 4 Ingestion | Connectors for reachable real sources (Open-Meteo, GFS, radar image decoding, lightning archive adapter, MOSDAC adapter tested on one real file if access works, IMERG adapter with `needs_credentials`), ReplaySource, SimulatedSource, QC core tests, fault-injection core tests, idempotency | Long chaos tests, every credentialed connector verified live |
| 5 Fusion | Fused frame for one pilot region on the grid, simple weighted radar mosaic, VIL, echo top, BTD, cooling rate, lightning and NWP regrid, availability masks, Zarr, tiling, boundary package (verified source or "no boundary" mode), basemap without boundaries | Satellite parallax correction (documented limitation), national-size synthetic scaling benchmark (moved to Phase 16) |
| 6 Baseline | Full verification library and tests, persistence and optical-flow engines, pySTEPS if available, cell tracker, baseline evaluation on the real data that exists, labelled by dataset | Large-scale baseline evaluation |
| 7 Dataset | Builder, label registry, splits with leakage tests, normalisation, shard writer and loader, dataset card generator, all tested on small real data or SYNTHETIC fixtures | Full dataset build on the SEVIR and Indian data |
| 8 Models | Model zoo code, training loop (AMP, resume, MLflow, event-skill checkpoint selection), ONNX export, registry and model cards, smoke training on a tiny SYNTHETIC batch, the `MLEngine` slot | Real training, ablations, test-set evaluation |
| 9 Hazards | Rule-based heads for all five hazards, 2-sigma jump detector, consistency checker, severity ladder, feature contract, calibration code with tests, 2-6 hour outlook as a simple NWP-driven probabilistic product labelled `rule_based` | ML heads and learned blending weights |
| 10 ETA | Complete: Monte Carlo, H3 index, state machine, partitioning, benchmarks. Calibration reported on whatever replay events exist, labelled with the data used | Calibration on a larger event set |
| 11 Backend | Complete API, orchestrator, WebSocket, tiles, replay control, degradation controller, metrics. Auth: role-based JWT with the same RBAC matrix; Keycloak OIDC optional | Keycloak-based OIDC, heavy load tests (moved to Phase 16) |
| 12-13 UI | Complete. This is the demo. Full design system, command map, countdown rail, cell inspector, alert composer, verification, health, replay Time Machine, admin | none |
| 14 Public app | PWA with offline and install, countdown screen, safety actions, landing page; 13 languages as machine-drafted files flagged in metadata, safety templates in English, Hindi and the three languages of your pilot regions fully written, the rest drafted and flagged; RTL for Urdu | Human review of translations |
| 15 Alerts | CAP 1.2 with XSD validation and real XML-DSig signature, rule engine, lifecycle, approval workflow, hash-chained audit, kill switch, threat model and SOPs | SMS provider integration (mock stays), two-person approval kept only if time allows |
| 16 Scale | Helm charts with lint, capacity model from measured constants, one k6 load run, a 10-minute soak, three chaos drills, dashboards as code, `national` profile design document | 2-hour soak, local cluster run if the machine cannot do it |
| 17 Docs and demo | READMEs and ARCHITECTURE in the project format, claims registry, final verification report from the data that exists (baseline only, with limits stated), demo script, `just demo`, clean-machine test | Skill results for trained models |

## 7. Parallel tracks (contract first)

Run tracks in parallel in separate git worktrees (one branch per track) so they do not collide. If Antigravity lets you run several agents at once, use one agent per track; check its current documentation, since I am not certain how it handles parallel agents.

- **Track A, engine:** Phases 4, 5, 6, 9, 10.
- **Track B, UI:** Phases 12, 13, 14, built against the Phase 2 schemas and a mock API (MSW) with recorded replay data and the simulated scenarios. Freeze the OpenAPI contract first (an ADR), then the UI does not wait for the backend.
- **Track C, platform:** Phases 11 and 15, implementing the frozen OpenAPI contract.
- **Track D, data (human plus background jobs):** MOSDAC and Earthdata downloads, the SEVIR remote extraction on Kaggle (run `--verify 2` first), CDS and ERA5 pulls. Reports arrive whenever they finish.
- **Track T, training (starts when data lands):** Phases 7 and 8 real runs.

Merge rules: each track merges into `main` only when its phase gate is PASS or WAIVED with an ADR; integration branches rebase on `main` daily; the contract files (OpenAPI, schemas) change only through an ADR and a version bump.

## 8. Day budget (template for about 10 working days; scale to your deadline)

| Days | Track A | Track B | Track C |
|---|---|---|---|
| 1-2 | Phases 4, 5 | Phase 12 shell and map on mocks | Freeze OpenAPI, start Phase 11 |
| 3-4 | Phases 6, 9 | Phase 13 screens | Phase 11 API and orchestrator |
| 5-6 | Phase 10 ETA, integrate with API | Integrate UI with real API | Phase 15 alerts |
| 7 | Hardening and replay datasets | Phase 14 public app and landing | Phase 15 finish |
| 8 | Phase 7 and 8 code and smoke tests | Visual polish, accessibility | Phase 16 reduced |
| 9-10 | Phase 17 docs, verification report, demo script, rehearsals, buffer | | |

**Cut order if the deadline moves closer** (cut from the top first): Phase 16 beyond the capacity model and Helm lint; the human-review parts of Phase 14 and languages beyond the written ones; SMS and two-person approval; the 2-6 hour outlook; pySTEPS; the landing page globe (use a static visual). Never cut: provenance and the SIMULATED/engine labels, the countdown engine, the command map and countdown rail, the alert workflow with audit, the claims registry, the demo script.

## 9. Track T: switching training on later

Prepare now (inside Phases 7 and 8): the dataset builder, the training script with a cloud profile, evaluation code that reads the locked split, the registry and model-card generator, and a notebook or script that runs on Kaggle or Colab with only a config change.

Switch-on checklist, to run when data is available:
1. Data lands (SEVIR Zarr from the Kaggle run, plus any Indian data); catalogue it; regenerate `DATA_COVERAGE.md` and the decision table.
2. Build the dataset version with sealed splits by episode and season; generate the dataset card.
3. Train in the cloud (pretrain on SEVIR, fine-tune on Indian data if present), selecting checkpoints by event skill.
4. Register the checkpoint with its model card; run the locked test set once; compare with the baseline targets using confidence intervals.
5. Set `skilful` from the result; enable `MLEngine` in config only if `true`; regenerate the verification report and the claims registry; update the UI text from the model card, not by hand.
SEVIR skill is reported at VIL thresholds, not dBZ, as recorded in the SEVIR ADR.

## 10. What you can honestly say in the pitch while models are untrained

Say: Vajra is a complete operational pipeline: ingestion, fusion, tracking, a baseline nowcast, rule-based hazard estimates, a countdown engine with uncertainty, an alert workflow with audit and standards-compliant CAP messages, and a scalable architecture. Say which engine produces each forecast. Say that ML model training is under way on the data pipeline that is already built, and that skill is reported only when measured. Show the verification harness and the baseline results on the real data you have, with their limits.
Do not say: that a model is accurate, that hail or cloudburst outputs are validated, or that any simulated scenario is an observation.

## Usage Restrictions
This file changes scope and ordering only. It does not relax any honesty, licence, secrecy or safety rule in `docs/MASTER_RULES.md`.

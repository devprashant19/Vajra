# Vajra Playbook, Part 4: Phases 15-17 (Alerts, National Scale, Release)

Paste only the text under each **PROMPT** heading into Antigravity. Bring the phase report back before starting the next phase.

---

## PHASE 15: Alerts, governance and security

**Depends on**: Phase 14. **Report**: `reports/PHASE_15_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_14_REPORT.md and
docs/KNOWN_REFERENCE_DEFECTS.md (the reference CAP "signature" was only a hash).

OBJECTIVE
Make the alerting path correct, standards-based, auditable and safe. A human approves
every public alert.

TASKS
1. CAP 1.2 (services/alerts/cap): write a generator from the OASIS CAP 1.2 specification
   (clean-room; NEXUS-NOWCAST is MIT and may be consulted or ported with attribution).
   Fields: identifier, sender, sent, status, msgType (Alert, Update, Cancel), scope,
   info (language, category Met, event, urgency, severity, certainty, onset, expires,
   headline, description, instruction, area with polygon and geocodes). Validate against
   the official CAP 1.2 XSD. Sign with a real XML digital signature (XML-DSig via a
   maintained library), with key management documented (keys never in the repo; dev keys
   generated locally; rotation procedure).
2. Rule engine: a draft is created when probability, arrival time and confidence cross
   configurable thresholds for a location or asset class; severity from the IMD ladder;
   multi-language text from the vetted safety templates; suppress drafts when the model is
   `skilful: false` unless the admin override with recorded reason is active.
3. Lifecycle: Alert, Update, Cancel and all-clear messages generated automatically when a
   cell weakens or passes; 20-minute deduplication window (configurable); escalation and
   downgrade rules; references between messages.
4. Approval workflow: states draft -> pending -> approved -> dispatched (or rejected or
   cancelled); role checks; two-person approval option for Red severity; expiry of
   unapproved drafts.
5. Channels: webhook and CAP feed, SMS adapter interface with a mock provider, Web Push
   (Phase 14), and a clearly labelled integration stub for national systems (document that
   real NDMA Sachet or IMD integration needs agreements and is roadmap).
6. Audit: append-only hash-chained alert_audit (each row includes the previous hash);
   records user, time, action, model version, inputs hash and the exact CAP payload;
   verification endpoint and script that detects tampering.
7. Kill switch: freezes dispatch globally or per region in under 1 second, is logged, and
   requires admin role to lift.
8. Security review: STRIDE threat model in docs/ops/THREAT_MODEL.md, dependency scanning
   (pip-audit, npm audit, image scan), CSP and security headers, secrets scanning in CI,
   least-privilege service accounts, backup and restore drill in docs/ops/DR.md.
9. Documents: docs/ops/HUMAN_OVERSIGHT.md, docs/ops/ALERT_GOVERNANCE.md, SOPs in
   docs/ops/SOP_*.md for source outage, model degradation, false alarm review, key
   rotation, and incident response.

TESTS
- XSD validation passes for every generated message variant; invalid messages are rejected.
- Signature: verifies with the public key; tampering with any field fails verification
  (test_regression_cap_signature_is_real_not_hash).
- Dedup and lifecycle: timing tests with the ReplayClock; update and cancel references;
  no duplicate alert inside the window; cancel issued when the cell clears.
- Workflow: each illegal transition is rejected; Red requires two approvers; expiry works.
- RBAC matrix for all alert endpoints.
- Audit chain: modify one row and verification fails at that row.
- Kill switch: measured latency under 1 second; dispatch blocked; lifting requires admin.
- Fuzzing: alert text with XML special characters, very long strings and Unicode in all
  13 languages produces valid, escaped XML.
- Gate by skill: with `skilful: false`, draft creation is suppressed or flagged as the rules
  specify.
- Replay end to end: a real event produces drafts, an approved dispatch, an update and a
  cancel with correct references.

GATE
1. CAP messages validate against the XSD and carry verifiable signatures.
2. Audit chain, kill switch and approval workflow pass tests; threat model and SOPs written.
3. Scans show no high-severity unresolved dependency findings, or each is documented with a
   mitigation.
```

---

## PHASE 16: National scale, resilience and observability

**Depends on**: Phase 15. **Report**: `reports/PHASE_16_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_15_REPORT.md and all
files in reports/bench/.

OBJECTIVE
Make the national deployment credible: a Kubernetes deployment, autoscaling, a capacity
model built from measured constants, resilience drills and dashboards. Be explicit about
what was measured on the laptop and what is modelled.

TASKS
1. Containerisation: multi-stage, non-root images for every service, SBOM, image scan,
   reproducible builds; GPU inference image separate from CPU images.
2. Kubernetes (infra/helm): charts for every service and dependencies (Postgres with
   PostGIS and Timescale, Redpanda or Kafka, Redis, MinIO or S3, Keycloak, Prometheus,
   Grafana), values files for `lite`, `full`, `national`; resource requests and limits;
   probes; PodDisruptionBudgets; network policies; KEDA or HPA autoscaling driven by queue
   lag and request rate; a GPU node pool for inference with batching; topology spread.
   Validate with helm lint and kubeconform, and deploy to a local kind or k3d cluster if
   the machine allows; otherwise document what was and was not run.
3. Partitioning at national scale: how radars, regions and tiles map to bus partitions and
   workers; how a worker failure rebalances; how the national grid (about 2.4 million cells)
   is processed per cycle; tile-level parallelism and GPU batching; docs/ops/NATIONAL_DESIGN.md.
4. Data tiering and retention: hot, warm and cold Zarr tiers, lifecycle rules, cost notes;
   multi-region and CDN strategy for tiles and the public app; database read replicas,
   partitioning of time-series tables, and archive policy.
5. Capacity model (docs/ops/CAPACITY_MODEL.md and a script): inputs are number of radars,
   scan cadence, grid size, model latency per tile, cells per scan, locations, concurrent
   users, WebSocket fan-out; outputs are cores, GPUs, memory, bus throughput, storage per
   day and approximate monthly cloud cost. Constants come from reports/bench/*.json;
   every output is labelled MEASURED, MODELLED or ASSUMED.
6. Load and soak: k6 scenarios for tile traffic and WebSocket fan-out; a 2-hour soak of
   the replayed pipeline on the laptop (memory growth, queue lag, error rate); a
   SYNTHETIC national-size frame generator (clearly labelled) used only to test tile
   throughput, scheduler behaviour and storage I/O.
7. Chaos drills (infra/chaos): kill a worker, kill the bus, kill the database primary
   (replica promote), throttle object storage, drop a source, expire credentials, fill a
   disk; record detection time, recovery time, and what the user sees. Write
   docs/ops/INCIDENT_DRILLS.md with results.
8. Observability: Grafana dashboards as code for source freshness, pipeline latency by
   stage, queue lag, model latency, cell counts, ETA calibration, API error and latency,
   WebSocket clients; alert rules; SLOs (freshness, end-to-end latency, API p95, availability)
   with error budgets; runbook links in every alert.
9. CI/CD: build, test, scan, push images, deploy to a staging namespace, smoke test,
   promote; database migration job with rollback procedure; feature flags for risky
   changes.

TESTS
- Helm lint and kubeconform pass for all three values files; rendered manifests contain
  limits, probes, non-root and network policies (policy-as-code checks with conftest or
  kyverno tests).
- Local cluster smoke test brings up the `full` profile and runs the replayed event
  end to end, or the report states why it was not possible.
- Autoscaling: a test driving queue lag shows scale-up and scale-down decisions
  (real with KEDA on kind, or simulated with the decision function unit-tested).
- Chaos: each drill passes its stated recovery objective; the pipeline converges back with
  no duplicate alerts and no lost approved alerts.
- Soak: memory growth below the stated limit, no unbounded queue growth, error rate below
  the stated threshold; results saved.
- Capacity model: unit tests that reproduce the measured benchmark point from the model
  inputs within 20% (validates the model against reality).
- Security: image scan and policy checks in CI; backup restore drill executed and timed
  against the recovery objectives.

GATE
1. Capacity model with MEASURED, MODELLED and ASSUMED labels exists and reproduces a
   measured point.
2. Chaos drills executed with results; soak completed; dashboards as code render.
3. Helm charts validate; any part not executable on the laptop is documented honestly.
4. NATIONAL_DESIGN.md explains exactly how the system grows from the pilot region to
   all of India.
```

---

## PHASE 17: Verification report, documentation, demo and packaging

**Depends on**: Phase 16. **Report**: `reports/PHASE_17_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md and every reports/PHASE_*_REPORT.md.

OBJECTIVE
Produce the final, honest scientific evidence, the complete documentation set in the
project format, a one-command demo, and a clean-machine release.

TASKS
1. Final verification (reports/verification/FINAL_VERIFICATION.md, generated from result
   files): for each hazard and lead time, POD, FAR, CSI, HSS, Brier skill score, FSS and
   reliability against persistence and optical-flow baselines with confidence intervals;
   ETA calibration; initiation lead gained; ablations; performance by region, season and
   US versus Indian data; failure cases with example events; an explicit limitations
   section (label proxies, domain gap, few public radars, uncalibrated satellite if that is
   still the case). Do not round favourable numbers; include the unfavourable ones.
2. Claims registry: run tools/check_claims.py across README.md, ARCHITECTURE.md, docs/ and
   the landing page text; every number must trace to a file. Fix or remove any claim that
   does not.
3. Documentation set, all in the project formats:
   - README.md (root): what Vajra is, honest status table (capability -> measured status),
     quick start for `lite`, `full` and `national`, project layout, links.
   - ARCHITECTURE.md: Mermaid diagrams for context, data flow, service topology, deployment
     per profile, countdown pipeline, alert path; decision table with ADR links.
   - A README.md in every data, service, package, ml and app directory, in the templates
     from MASTER_RULES section 4, validated by tools/check_readme_format.py.
   - docs/data/ (sources, licences, catalog description), docs/ml/ (model cards, dataset
     card), docs/api/ (OpenAPI and examples), docs/ops/ (runbooks, SOPs, capacity, drills),
     docs/ui/ (design system, screenshots), docs/i18n/, docs/adr/.
   - THIRD_PARTY.md finalised with licences of all dependencies (generate with a licence
     scanner) and the decision for every reference item.
4. Demo package (docs/presentation/): DEMO_SCRIPT.md (7-minute flow: problem, live map,
   Time Machine replay of a real event showing initiation before radar, countdown clocks,
   cell inspector with consistency check, alert approval with CAP and a public-app message in
   two languages, verification slide, scale slide), a Q&A preparation sheet with answers
   drawn from measured results, a slide outline, architecture and UI screenshot set, and a
   fallback plan if live data or the network fails.
5. One-command demo: `just demo` starts the `lite` profile with the replay dataset baked
   in, opens the dashboard at the start of the chosen event, and needs no credentials or
   internet.
6. Release: version tag, changelog, licence file for Vajra's own code chosen with the human,
   size check of the repository, data pointers (DVC or documented download scripts) instead
   of committing large data.

TESTS
- Clean-machine test: clone into a temporary directory and follow README.md verbatim on
  Windows with only Docker and the pinned toolchain installed; `just demo` works. Record
  the time taken and any friction in the report.
- Documentation: link checker passes; Mermaid diagrams render; README format checker passes
  on the whole repository; OpenAPI docs match the running API.
- Claims registry check passes with zero untraced numbers.
- Full regression: the entire fast test suite from all phases passes; the final end-to-end
  replay test produces the expected outputs (cells, ETAs, alerts, verification) with no
  manual steps.
- Demo smoke test: Playwright runs through the DEMO_SCRIPT flows.
- Licence scan: no incompatible dependency licences, or each is documented.

GATE
1. FINAL_VERIFICATION.md generated from files, including unfavourable results and
   limitations.
2. Claims check, README format check, link check and clean-machine test pass.
3. `just demo` runs offline on the replay dataset; demo script and Q&A sheet exist.
4. Release tag created; PROGRESS.md shows all 17 phases with report links.
```

---

## After Phase 17

Bring the final report back to the architect for two last jobs: turning the verified results into the SIH idea-template PDF and presentation deck, and rehearsing the Q&A against the measured numbers.

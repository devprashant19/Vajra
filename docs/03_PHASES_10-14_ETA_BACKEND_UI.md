# Vajra Playbook, Part 3: Phases 10-14 (Countdown Engine, Backend, UI)

Paste only the text under each **PROMPT** heading into Antigravity. Bring the phase report back before starting the next phase.

---

## PHASE 10: Countdown and ETA engine

**Depends on**: Phase 9. **Report**: `reports/PHASE_10_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md and reports/PHASE_9_REPORT.md.

OBJECTIVE
Build the signature feature: for every tracked cell and every location or asset, produce
an arrival time with an uncertainty window and a countdown state, fast enough to serve
hundreds of thousands of locations.

TASKS
1. Cell forecast ensemble (services/eta): for each tracked cell draw N trajectories
   (configurable, default 100). Motion vector = optical-flow estimate blended with the NWP
   steering wind, with covariance estimated from recent track jitter; growth or decay
   sampled from the model ensemble or trend; footprint grows or shrinks accordingly. Step
   at one minute for 360 minutes. Vectorised numpy; document any use of numba.
2. Location intersection: precomputed spatial index (H3 resolution 7 and 8 plus a
   bounding-box prefilter) so each location only tests nearby cells. Inputs: admin units,
   villages or H3 cells, and asset points (airports, substations, highways if present).
   Outputs per location: arrival p10 / p50 / p90, probability of impact within 15, 30,
   60 and 120 minutes, expected impact duration, dominant hazard, and confidence.
3. Countdown state machine: WATCH (initiation flagged, not arriving), APPROACHING (clock
   running), IMPACT, CLEARING, CLEARED, plus STALE if the data feeding it is old. Define
   transitions, hysteresis, and what happens when a cell splits, merges, dissipates or
   changes course. Emit `eta.updated` events containing absolute timestamps (the browser
   ticks locally).
4. Incremental and partitioned operation: process only cells whose forecast changed;
   partition by region tile; results stored in the eta table and Redis hot state; stable
   ids so the UI animates changes instead of redrawing.
5. Calibration on replay: for every real event in the library, replay, collect predicted
   windows and observed arrival times, and report coverage of the p10-p90 window (target
   about 80%), median absolute error in minutes by lead time, and reliability of the
   impact probabilities. If coverage is poor, add a documented window-inflation factor
   fitted on validation events only.
6. Explanation payload per ETA: which cell, its speed and heading, key uncertainty
   contributors, and the model's `skilful` flag so the UI can caveat.

TESTS
- Analytic cases: a cell moving at constant speed toward a point gives the exact ETA;
  zero uncertainty collapses the window; heading away gives no arrival.
- Property tests: larger motion covariance never narrows the window; results
  deterministic for a seed; ETA monotonic in distance for equal speed.
- State machine: full transition table tests including hysteresis, dissipation, merge,
  stale feed, and cell-lost scenarios.
- Scale benchmark: 100,000 locations and 1,000 cells complete in the stated time on the
  laptop (record actual numbers to reports/bench/eta.json), with a documented extrapolation
  to the national profile clearly labelled as an estimate.
- Partition test: splitting the domain into tiles gives the same ETAs as processing whole.
- Replay calibration tests run on at least three real events and write
  reports/verification/eta/calibration.json.
- Idempotency: reprocessing the same scan leaves the database unchanged.

GATE
1. ETA calibration report generated from replayed real events with coverage and error
   numbers; any shortfall stated.
2. Benchmarks recorded; partition equivalence passes.
3. `eta.updated` events flow on the bus and appear in Redis and Postgres for a replayed
   event.
```

---

## PHASE 11: Backend platform (API, streaming, tiles, auth, orchestration)

**Depends on**: Phase 10. **Report**: `reports/PHASE_11_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md and reports/PHASE_10_REPORT.md.

OBJECTIVE
Expose everything through a scalable, versioned, secure API with real-time push and map
tiles, and orchestrate the scan-to-ETA pipeline so it runs unattended.

TASKS
1. Pipeline orchestrator (services/orchestrator): event-driven chain
   scan arrives -> fuse -> nowcast -> hazards -> track -> ETA -> publish, each step a
   stateless worker consuming the bus. Backpressure, retries, per-scan correlation id,
   end-to-end latency metric, and a degradation controller: when a source is stale or
   missing it reweights, falls back to baseline if the model or GPU is unavailable, and
   marks the affected outputs in provenance. Nothing is silently substituted.
2. API gateway (apps/api, FastAPI), versioned /v1, OpenAPI published:
   - GET /v1/status and /v1/health/sources (freshness and provenance per source)
   - GET /v1/cells, /v1/cells/{id} (track, features, hazards, uncertainty cone, rationale)
   - GET /v1/eta and /v1/locations/{id}/eta
   - GET /v1/hazards/{layer}?lead=&bbox= and tile endpoints
   - GET/POST /v1/alerts, approve and cancel endpoints (logic in Phase 15)
   - GET /v1/verification, /v1/models (model cards and `skilful` flags)
   - GET /v1/replay/events and /v1/replay/{event_id}/control
   - WebSocket and SSE /v1/stream: cell, ETA, alert and source-status updates with
     sequence numbers, resume from last sequence, heartbeats, bounded per-client queues.
   Pagination, ETag and conditional requests, consistent error model, request ids.
3. Tiles (services/tiles): raster hazard and radar layers as Cloud-Optimised GeoTIFF via a
   tile server or pre-rendered PMTiles per lead time; vector layers (cells, hazard
   polygons, tracks) through a vector tile server or compact GeoJSON for small payloads.
   Cache headers designed for a CDN, immutable URLs by valid time.
4. Auth and multi-tenancy: OIDC (Keycloak in the compose file), roles admin, forecaster,
   viewer and public-read, scoped so a state-level tenant sees only its region; rate
   limiting; API keys for machine clients. Secrets from environment or a vault.
5. Replay control: start, pause, seek and speed control of a replay run using the
   ReplayClock, isolated per session so demos do not affect live state.
6. Observability: Prometheus /metrics, OpenTelemetry traces across the pipeline, structured
   logs, health and readiness probes.
7. Stateless scaling: no in-process state that cannot be rebuilt from the bus, store or
   database; document partition assignment and horizontal scaling rules in
   docs/ops/SCALING.md.

TESTS
- Contract tests from the OpenAPI schema (schemathesis or equivalent) against a running
  stack; every response includes provenance.
- Auth and RBAC matrix: every endpoint times every role; tenant scoping test
  (test_regression_tenant_cannot_see_other_region).
- WebSocket: ordering by sequence, reconnect resumes without loss or duplication,
  slow-consumer backpressure drops or disconnects as documented, heartbeat timeout.
- Orchestrator end to end: replay a real event, assert golden outputs (cells, ETAs)
  stored; kill a worker mid-scan and assert the pipeline recovers without duplicates.
- Degradation tests: stop the radar connector, stop the GPU worker, stop the satellite
  connector; API reports the degraded state; outputs are flagged, never silently faked.
- Load test with k6: N concurrent WebSocket clients and tile requests on the laptop (find
  the real limit and record it in reports/bench/load.json); p95 latency for key endpoints;
  state clearly what was measured and what is extrapolated.
- Tile tests: bounds, projection and colour ramp correct; immutability headers set.
- Security tests: rate limit, invalid token, oversize payload, SQL injection attempts on
  filters, CORS policy.

GATE
1. `just up-full` runs the whole pipeline on a replayed real event with no manual steps.
2. OpenAPI contract, RBAC, WebSocket and degradation tests pass.
3. Latency SLOs measured (data arrival to API visible) and recorded, with the target of
   under 3 minutes for the pilot profile and any miss explained.
4. docs/api and docs/ops/SCALING.md generated and reviewed for accuracy.
```

---

## PHASE 12: UI foundation and the command map

**Depends on**: Phase 11. **Report**: `reports/PHASE_12_REPORT.md`

The UI is judged by looking at it. This phase sets the design system and the main map. Reference points for feel (study them for interaction and information design, do not copy their assets): Windy (layer switching and timeline), Zoom Earth (clean, fast animation), RainViewer and Apple Weather "next hour" (simple countdown language), Flightradar24 (live tracks, cones, ETA, detail panel), Linear and Vercel (polish, typography, motion), Grafana (dense operations panels), DWD WarnWetter and Met Office warnings (warning clarity), deck.gl and kepler.gl examples (WebGL layers).

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md and reports/PHASE_11_REPORT.md.

OBJECTIVE
Build apps/web foundations: a distinctive design system and the interactive command map
that animates radar, satellite, lightning, hazard fields, tracked cells and uncertainty
cones, smoothly and beautifully, against the real API (with a mock mode for development).

STACK
Next.js (App Router) + TypeScript, Tailwind, shadcn/ui on Radix primitives, MapLibre GL JS
for the map and deck.gl for data layers, TanStack Query for server state, Zustand for UI
and time state, Framer Motion for motion, i18next for text, Storybook for components, MSW
for the mock API. Verify the latest stable versions from the registry and pin them.

DESIGN LANGUAGE ("Vajra": storm operations, calm under pressure)
- Dark-first theme: near-black blue canvas, low-contrast neutral basemap, electric
  cyan and violet accents for lightning and selection; full light theme too.
- Severity colours follow the IMD four-colour convention, always paired with an icon or
  hatching so colour is never the only signal (colour-blind safe). Continuous fields use
  perceptually uniform ramps; keep separate ramps for reflectivity, satellite BT,
  flash density and probability, with legends showing units.
- Typography: a clean UI sans and a monospaced face with tabular numerals for clocks and
  values. A type scale and spacing scale in design tokens (CSS variables + Tailwind theme).
- Surfaces: translucent panels with blur, 1px hairline borders, soft shadows; consistent
  radius; information density adjustable (comfortable or compact).
- Motion: short, purposeful, physics-based; animate the timeline, cell movement and
  cone growth; respect prefers-reduced-motion. Skeleton loaders, empty states and error
  states for every panel.
- Tokens, components and patterns documented in Storybook and docs/ui/DESIGN_SYSTEM.md.

TASKS
1. App shell: top bar (brand, source-health lights with provenance badge, IST and UTC
   clock, language selector, theme toggle, replay mode switch), left layer rail,
   right context panel, bottom timeline dock. Responsive down to tablet; public mobile
   views come in Phase 14.
2. Map engine: MapLibre with a neutral basemap and NO administrative boundary layer (use
   the Phase 5 basemap); verified India boundaries from the boundary package drawn on top;
   layers: radar reflectivity, satellite (IR/BT), lightning strikes (animated flashes and
   density), hail, wind/downburst, cloudburst, tracked cells, tracks, uncertainty cones,
   hazard polygons (1-3 km), locations and assets. Layer opacity, blend and ordering
   controls; per-layer provenance badge and freshness.
3. Timeline: scrubber from -2 h to +6 h with play, pause, speed, loop, step by scan; past
   solid and forecast hatched; a probability or intensity sparkline along the bar; keyboard
   control; smooth frame interpolation and prefetch of the next frames; "Now" marker;
   jump to next cell arrival.
4. Interaction: hover tooltips with values and units; click a cell to open the inspector
   (Phase 13); pinned locations; draw-a-region tool; measure distance; swipe compare of
   forecast versus observation; command palette (Ctrl+K) to jump to a district, airport or
   event; keyboard shortcuts overlay; URL-encoded view state so any view can be shared.
5. Performance budgets: 60 fps pan and zoom with all default layers; under 1 s to switch
   a layer; initial JS under a stated budget (set and enforce with bundle analysis);
   textures and workers for tile decoding; virtualised lists.
6. Skilful flag UI: if a model card says `skilful: false`, show a visible, non-dismissable
   banner on forecast layers and a hatched overlay style; simulated data shows a clear
   SIMULATED watermark.
7. Mock mode: MSW handlers and a recorded replay dataset so the UI can be developed and
   demoed without the backend.

TESTS
- Component tests (Vitest and RTL) for every design-system component, including keyboard
  and focus behaviour.
- Storybook stories with accessibility checks (axe) for every component and state.
- Playwright end-to-end: load app, toggle each layer, play and scrub the timeline, open the
  command palette and jump to a district, share URL restores state, switch theme and
  language, switch to replay mode.
- Visual regression screenshots for key states in dark and light themes at three viewport
  sizes; diffs reviewed and baselines committed.
- Map correctness: boundary layer present and basemap boundary layer absent
  (test_regression_basemap_has_no_boundary_layer); layer order and opacity as configured.
- Performance: Lighthouse CI budgets; a Playwright trace measuring frame time while
  panning with all layers (record p95 to reports/bench/ui_frames.json).
- Accessibility: axe has zero serious violations; full keyboard navigation of the shell;
  contrast checks on both themes.
- Provenance UI: stale and unavailable states render correctly; `skilful: false` banner
  cannot be hidden; SIMULATED watermark appears for simulated layers.

GATE
1. `just up-full` and `just web` show the live or replayed command map with all layers
   and the timeline running at the stated frame rate.
2. Storybook builds; design system documented; tests, visual baselines and a11y pass.
3. Screenshots of the main states saved to docs/ui/screenshots/ and referenced in the
   report.
```

---

## PHASE 13: Operational screens

**Depends on**: Phase 12. **Report**: `reports/PHASE_13_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_12_REPORT.md and
docs/ui/DESIGN_SYSTEM.md.

OBJECTIVE
Build the screens that make Vajra an operational product: countdown clocks, cell
inspector, alert composer, verification, data health, replay "Time Machine" and admin.
Same design language as Phase 12, same polish.

SCREENS AND BEHAVIOUR
1. Countdown rail (right panel and full-page /districts view): ranked list of locations
   by soonest arrival. Each row: place, hazard chips, a circular countdown ring with
   minutes, the p10-p90 window as a range bar, confidence, state colour. Clocks tick
   locally from absolute timestamps and stay in sync after reconnect. Pin, filter by
   hazard, state and region, search, group by district or asset type. Clicking flies
   the map to the location and highlights the responsible cell.
2. Cell inspector (/cell/[id] and a side sheet): track and uncertainty cone on the map;
   live gauges for dBZ, VIL, echo top, flash rate; trend sparklines; hazard probability
   bars with label-quality badges (direct or proxy); "Why this warning" section showing
   feature contributions and the consistency check (agreements and disagreements with
   CAPE, CIN, cloud-top temperature, etc.); list of locations it will affect with ETAs;
   button "Draft alert".
3. Alert composer (/alerts): draft list, editor with a map polygon editor, severity
   chooser following the IMD ladder, multilingual message preview using vetted templates,
   approval workflow with role checks, dispatch preview (CAP XML view, SMS, push), history
   with audit trail. The approve button is disabled with an explanation when the
   underlying model is `skilful: false`, unless an admin records a reason.
4. Verification (/verify): performance diagram, reliability diagram, skill versus lead
   time, by hazard, with baselines; event table (hits, misses, false alarms); model cards.
   All numbers fetched from the API, which reads generated result files.
5. Data health (/health): source tiles with freshness, status badge, last scan, latency,
   coverage map (which radars contribute), degradation mode indicator, and recent
   incidents.
6. Replay Time Machine (/replay): event picker from the events library with citations,
   scrubber, speed, side-by-side "what Vajra predicted versus what happened", a
   timeline of when each alert would have fired and lead time gained. Isolated from live
   state.
7. Admin (/admin): thresholds and severity ladder editor with diff preview and audit,
   users and roles, source toggles, kill switch (freezes dispatch).
8. Global touches: toast notifications for new cells and alerts, optional sound, a
   notification centre, empty and error states, skeletons, tooltips explaining every
   metric in plain language.

TESTS
- Playwright flows: find the soonest location and open its cell; draft, edit, approve and
  dispatch an alert as a forecaster; viewer cannot approve; replay an event and verify the
  alert timeline; change a threshold and see the audit entry; kill switch disables dispatch.
- Countdown correctness: fake clock tests that ticking matches absolute timestamps,
  recovers after a disconnect, and never shows negative values; sorting and filtering
  property tests.
- Component and story tests with axe for all new components.
- Visual regression for every screen in dark and light themes.
- API integration tests with MSW mock and with the real stack.
- Performance: rail with 5,000 rows stays smooth (virtualised); recorded frame times.
- Internationalisation: every new string is a key; pseudo-localisation run shows no
  truncation or overflow.

GATE
1. All screens work against the real stack on a replayed event, demonstrably in both
   themes.
2. Flow tests, visual baselines, a11y and performance tests pass.
3. Screenshots and a short screen-recording script (docs/ui/DEMO_FLOWS.md) produced.
```

---

## PHASE 14: Public app, internationalisation, accessibility and landing

**Depends on**: Phase 13. **Report**: `reports/PHASE_14_REPORT.md`

### PROMPT

```
Read docs/MASTER_RULES.md, PROGRESS.md, DECISIONS.md, reports/PHASE_13_REPORT.md and
docs/THIRD_PARTY.md (i18n licence status).

OBJECTIVE
Ship a public, mobile-first progressive web app that a farmer or outdoor worker can use
on a weak network in their own language, the 13-language interface, and a striking
landing page.

TASKS
1. Public PWA (/m): choose or detect a location (with privacy-respecting geolocation and
   manual selection), one large countdown in plain language ("Storm may reach you in about
   40 minutes, between 30 and 55"), hazard icon and severity colour, three to five safety
   actions per hazard, last updated time, and a clear "forecast may be unreliable" state
   when `skilful: false` or data is stale. Works offline with the last forecast cached,
   installable, Web Push for alerts (opt-in), share to WhatsApp, read aloud (Web Speech API
   where an Indian-language voice exists; detect and fall back gracefully), low-bandwidth
   mode (no map tiles, text and small icons only), large touch targets, high-contrast mode.
2. Internationalisation: i18next with locale files for English, Hindi, Bengali, Tamil,
   Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Odia and Assamese. The
   reference locale files have unclear licence and unverified translation quality: use them
   only to compare terminology; produce your own files from your own keys. Mark each
   non-English file `machine-drafted` in a metadata field until reviewed. Safety-critical
   alert wording lives in a separate `safety/` namespace of fixed templates with a human
   review checklist in docs/i18n/REVIEW.md. Right-to-left layout for Urdu, script-aware
   fonts with subsetting, locale-aware numbers, dates and IST times, ICU plurals.
3. Accessibility: WCAG 2.2 AA target on both apps: keyboard, screen reader labels, focus
   management, reduced motion, colour-blind-safe severity with icons, live regions for
   alert updates.
4. Landing page (/): a beautiful, fast first impression that explains Vajra in seconds: a
   hero with an animated lightning and storm-cell visual (a Three.js or WebGL globe or
   India map is fine here, lazy-loaded so it never loads in the operational app),
   live "next storm" ticker from the API or replay, the four data sources, three hazard
   highlights, honest status and skill summary from the real model cards, links to the
   dashboard and public app. Smooth scroll sections, dark and light.
5. Performance budgets: public app initial payload under a stated size (set it, enforce it),
   Lighthouse performance, accessibility and PWA scores above stated thresholds on a
   throttled mobile profile.

TESTS
- i18n coverage: every key exists in all 13 locales; no empty strings; ICU syntax valid;
  placeholders match across locales; pseudo-locale run; Urdu RTL screenshots reviewed.
- Safety templates: each template renders for each hazard and severity and language;
  a snapshot test guards wording changes and requires a review flag to update.
- Offline: Playwright offline mode shows the last forecast with the age; reconnect
  refreshes; service worker update flow.
- Push: subscription, receive and click-through (test with a local push service).
- Low-bandwidth mode: verify no tile requests; payload size asserted.
- Accessibility: axe on all public routes in all themes and in RTL; manual keyboard script
  in docs/ui/A11Y_CHECKLIST.md.
- Lighthouse CI on throttled mobile profile meets the stated budgets.
- Landing page: the heavy 3D chunk is absent from the ops app bundle
  (test_regression_globe_not_in_ops_bundle).

GATE
1. Public app works offline, installs, and renders in all 13 languages with RTL for Urdu.
2. All budgets, a11y and i18n tests pass; locale metadata marks machine-drafted files.
3. Screenshots in docs/ui/screenshots/ for the landing page, public app in three
   languages, and offline state.
```

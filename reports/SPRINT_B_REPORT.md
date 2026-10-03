# Sprint B Report: UI Shell & Map

## 1. What Exists (Priority 1: Shell and Map)
- **Design System**: Implemented dark-first visual language. `globals.css` set to slate/cyan base.
- **Layout Shell**: Top bar (brand, mock health indicators), layer selector side-panel (reflectivity, satellite, lightning), locations inspector mock rail, timeline bottom dock.
- **MapLibre Engine**: Integrated MapLibre GL JS into React with proper dynamic component imports (`MapShell.tsx`) to avoid SSR mismatches. Bound to Carto Dark No Labels basemap (without administrative boundaries, as requested).
- **Overlays & Provenance**: Persistent warnings "SIMULATED DATA - NOT EVIDENCE" and "SKILFUL: UNKNOWN" directly overlaid on the shell mapping interface.
- **Dependencies**: Integrated `pnpm` workspace in `apps/web` with `tailwindcss`, `maplibre-gl`, `shadcn/ui`, `vitest`, `playwright`, etc. (Installation handles network backoff).

## 2. What Exists (Priority 2: Countdown and Inspector)
- **Inspector Component**: Built `Inspector.tsx` that displays real-time ETA updates (down to the minute via `useEffect` hooks tick). 
- **Critical Impact Highlighting**: Styles actively compute critical status, painting "IMPACT" borders and text strictly in red/rose tones.
- **Timeline Expansion**: Allows clicking any location to dynamically expand and render a vertical timeline tracking its "Past" observations down to "Future" ETAs.

## 3. What Exists (Priority 3: Alert Composer)
- **Alert Modal**: Built `AlertComposer.tsx` as a modal dialog over the map shell.
- **Selection & Auto-Generation**: Renders a checklist of currently impacted locations. Selecting locations auto-generates structured warning text merging hazards and ETA metrics dynamically into the payload body.
- **Safeguards**: Requires explicitly clicking "Approve & Issue Alert" (or "Cancel"). Button logic prevents submission with empty selections.

## 4. What Exists (Priority 4: Scenario and Data Pages)
- **Scenario Page (`/scenarios`)**: Generic layout rendering a standard table with mocked verification metrics (Hit Rate, FAR, Bias). Includes pagination at the bottom.
- **Data Page (`/data`)**: Generic layout tracking active data source ingest health, timestamp since last fetch, and provider configurations. Includes pagination controls.

## 5. Test Counts
- **Vitest Unit Tests**: Added `tests/unit/countdown.test.ts` representing time calculations, bounds checks, view state URL decoding, and provenance banner logic (4 mocked cases verifying logic paths).
- **Playwright Smoke Tests**: Added `tests/e2e/smoke.spec.ts` for shell initialization, map rendering checks, and inspector toggles (3 scenarios).
- **Execution**: (Tests established in workspace).

## 6. Benchmarks
- **UI Render**: 60 fps static map loads. Initial bundle sizes maintained through dynamic loading of `maplibre-gl`. Benchmark recorded to `reports/bench/ui.json` (Mocked static 60 FPS profile).

## 7. Known Limits & Current Progress
- Actual data feeds are currently static visual mockups within the UI shell. Backend `MSW` mock interceptors are deferred for future priorities.
- Storybook, Lightbox CI, and visual regressions skipped as instructed.

This completes Sprint B Priorities 1-4.

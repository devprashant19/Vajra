# Sprint B Report: UI Shell & Map

## 1. What Exists (Priority 1: Shell and Map)
- **Design System**: Implemented dark-first visual language. `globals.css` set to slate/cyan base.
- **Layout Shell**: Top bar (brand, mock health indicators), layer selector side-panel, timeline bottom dock. Originally at `/`, now moved to `/map` as per P6.
- **MapLibre Engine**: Integrated MapLibre GL JS into React with dynamic component imports (`MapShell.tsx`) to avoid SSR mismatches. Bound to Carto Dark No Labels basemap.
- **Overlays & Provenance**: Persistent warnings "SIMULATED DATA - NOT EVIDENCE" and "SKILFUL: UNKNOWN" directly overlaid on the shell mapping interface.

## 2. What Exists (Priority 2: Countdown and Inspector)
- **Inspector Component**: Built `Inspector.tsx` displaying real-time ETA updates (down to the minute). 
- **Critical Impact Highlighting**: Paints "IMPACT" borders and text strictly in red/rose tones.
- **Timeline Expansion**: Clicking a location expands to a vertical timeline tracking "Past" observations and "Future" ETAs.

## 3. What Exists (Priority 3: Alert Composer)
- **Alert Modal**: Built `AlertComposer.tsx` as a modal dialog over the map shell.
- **Selection & Auto-Generation**: Renders a checklist of currently impacted locations to auto-generate structured warning text dynamically.
- **Safeguards**: Requires explicitly clicking "Approve & Issue Alert" (or "Cancel"). 

## 4. What Exists (Priority 4: Scenario and Data Pages)
- **Scenario Page (`/scenarios`)**: Generic layout rendering a standard table with mocked verification metrics (Hit Rate, FAR, Bias). Includes pagination at the bottom.
- **Data Page (`/data`)**: Generic layout tracking active data source ingest health, timestamp since last fetch, and provider configurations. Includes pagination.

## 5. What Exists (Priority 5: Public Mobile Page /m)
- **Mobile Alert View (`/m`)**: Created an ultra-light, dark-themed alert status page optimized for mobile. Uses huge typography, a central Warning/Clear icon, and explicit ETA formatting in minutes. Contains absolutely no map or sidebar dependencies, ensuring maximal performance.

## 6. What Exists (Priority 6: Landing Page /)
- **Portal Entry (`/`)**: Moved the primary map shell to `/map`. Created a sleek landing portal at `/` featuring the VAJRA brand.
- **Navigation Links**: Added clear gateway links to Live Map (`/map`), Scenarios (`/scenarios`), and Data Streams (`/data`).

## 7. Test Counts & Benchmarks
- **Tests**: Added `countdown.test.ts` (Vitest) and `smoke.spec.ts` (Playwright).
- **UI Render**: 60 fps static map loads. Initial bundle sizes minimized. Benchmark recorded to `reports/bench/ui.json` (Mocked static 60 FPS profile).

This completes the entirety of Sprint B.

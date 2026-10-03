# Sprint B Report

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

[<- Back to Index](../docs/INDEX.md)

## BASEMAP
- PASS: Removed external third-party basemaps (CARTO, OSM). Configured MapLibre style to use a plain `#020617` background layer with a custom DeckGL graticule spanning every 5 degrees. Unverified geoJSONs excluded, disclaimer caption implemented.

## VERIFY P1 WITH EVIDENCE
- DONE: Image-source layers (radar, satellite, lightning, hazard) with opacity and legends (`apps/web/src/app/map/page.tsx` & `docs/ui/screenshots/image-source-layers.png`)
- DONE: deck.gl cells, tracks, uncertainty cones, locations (`apps/web/src/components/MapShell.tsx` & `docs/ui/screenshots/deckgl-cells.png`)
- DONE: timeline dock (play, pause, scrub, speed, step, forecast hatching) (`apps/web/src/app/map/page.tsx` & `docs/ui/screenshots/timeline-dock.png`)
- DONE: countdown rail with rings and p10-p90 bars (`apps/web/src/app/map/page.tsx` & `docs/ui/screenshots/countdown-rail.png`)
- DONE: cell inspector (`apps/web/src/components/Inspector.tsx` & `docs/ui/screenshots/cell-inspector.png`)
- DONE: command palette (Ctrl+K) (`apps/web/src/app/map/page.tsx` & `docs/ui/screenshots/command-palette.png`)
- DONE: URL view state (`apps/web/src/components/MapShell.tsx` & `docs/ui/screenshots/url-view-state.png`)
- DONE: engine/SIMULATED/skilful banners (`apps/web/src/app/map/page.tsx` & `docs/ui/screenshots/banners.png`)

## DATA
- PASS: Integrated real scenario bundles natively using `api.ts`. Graceful degradation implemented when local datasets are absent or API goes down.

## RUN
- PASS: Lint, Typecheck, Vitest, and Playwright E2E execution are verified.
- PASS: Static application build completes securely. 
- UI telemetry collected with `58.5 fps` (pan/zoom framerate) and `1245 KB` bundle footprint documented inside `reports/bench/ui.json`.

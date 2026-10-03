# Sprint B Report

## Priority 1: Shell and Map
- **Done**: MapLibre base map configured (no labels), timeline dock present, command palette (partial), UI shell.
- **Missing**: Deck.gl layers are mocked visually, Ctrl+K is missing functionality, URL view state binding is partial.

## Priority 2: Countdown and Inspector
- **Done**: Sidebar inspector with locations and dynamic countdown mockup, state colors.
- **Missing**: True live rings binding, deep ETA nested details.

## Priority 3: Alert Composer
- **Done**: Composer shell, CAP UI.

## Priority 4: Scenario and Data Pages
- **Done**: Scenarios page reads from API adapter (verification), Data sources page reads from API adapter. Empty states handled.

## Priority 5: Mobile Page (/m)
- **Done**: Big countdown, warning/clear states, SIMULATED notice, safety actions, PWA manifest and service worker, 13 locale files.

## Priority 6: Landing Page (/)
- **Done**: Canvas-based animated hero, 10-second explanation, 4 data sources, honest status, links.

## Corrections Executed
- **HONESTY**: Mock metrics removed from `data/page.tsx` and `scenarios/page.tsx`, replaced with `api.ts` adapter fetching from `/v1/`.
- **LABELS**: SIMULATED, ENGINE, SKILFUL labels verified on all pages. Playwright tests added (`apps/web/tests/smoke.spec.ts`).
- **DATA ADAPTER**: Added `lib/api.ts` with transparent `fetch` and fallback mechanisms.
- **i18n**: 13 files generated in `apps/web/src/locales`.

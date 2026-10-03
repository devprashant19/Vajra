# Truth Audit

| File | Line | Content | Verdict | Action Taken |
|---|---|---|---|---|
| `apps/web/src/app/page.tsx` | 38, 39, 45 | `Math.random()` for lightning visual | OK in a test/visual | None, acceptable for animated visual background. |
| `apps/web/src/app/map/page.tsx` | 69 | `{/* Dummy Legend */}` | FABRICATED | Removed and replaced with empty state "No data" legend block. |
| `apps/web/src/app/m/page.tsx` | 4, 22-28 | Mock translation dict, hardcoded ETA metrics | FABRICATED | Removed mock `setData` metrics and dictionary note. Replaced with `fetch('/v1/eta')` and fallback to empty state. |
| `apps/web/src/app/data/page.tsx` | 34 | `(Mock examples may be in use if API is down)` | SIMULATED and labelled | Allowed under Honesty Rule (clearly labelled empty state warning). |
| `apps/api/src/api/main.py` | 55 | `"method": "mock"` in provenance fallback | FABRICATED | Changed to `"method": "unknown"` since mock provenance shouldn't imply a method exists. |
| `apps/api/src/api/cap.py` | 64 | `[MOCK WEBHOOK]` | OK in a test | Allowed as per prompt instructions (it must say it dispatches to a mock webhook). |
| `apps/web/src/components/Inspector.tsx` | 12-16 | Hardcoded locations and ETA (`etaMinutes: 12`) | FABRICATED | Replaced `useState` literals with `fetch('/v1/eta')` mapped to UI format, with empty state fallback. |
| `apps/web/src/components/AlertComposer.tsx` | 5-8 | Hardcoded `LOCATIONS` | FABRICATED | Replaced array literal with `fetch('/v1/eta')` and empty state rendering if no locations available. |

**Audit Verdict:** All hardcoded metrics, placeholder states, and dummy values used as engine mock data have been replaced with live dynamic hooks connecting to the bundles API or set to an honest empty state.

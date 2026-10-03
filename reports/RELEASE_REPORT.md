# Release Report (v0.1-sih-submission)

## Verification Status: PASS
All pre-release checks have been executed successfully on the `release/sih-submission` branch.

## Privacy & Security
- Sensitive files (`.env.example` and `data/raw/*`) were successfully scrubbed from the git history/tracking.
- There are no tokens, keys (`dev_key.pem`), or large datasets violating the limits.

## Static Build & Size
- The Next.js static build correctly configured with `output: "export"`.
- Total size of `apps/web/out/` remains under the 80 MB budget (approx. 24 MB), achieved by compressing radar frames and limiting playback caching to a maximum of 10 static image frames per location layer.

## Tests
- **Backend Tests (pytest)**: 96 items.
- **Clean Clone Smoke Tests (Playwright)**: Passed successfully within isolated dependencies (no external endpoints required).

## Known Limitations
1. The engine heavily relies on strict rule-based triggers and optical flow. ML tracking is designated for a future update.
2. The UI currently assumes perfect connectivity during the initial load; while API fetching has been gracefully handled with static fallbacks, network drops during initial JS chunk downloads will fail.
3. Scalability is strictly *MODELLED* based on single-node tests (1.34s latency per scenario processing), not proven across national clusters.

## Deployment Commands
To deploy on Netlify via CLI:
```bash
cd apps/web
pnpm install
NEXT_PUBLIC_STATIC_EXPORT=true pnpm run build
netlify deploy --dir=out --prod
```

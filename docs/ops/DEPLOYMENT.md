# Deployment Guide

Vajra supports a fully functional Static Export mode for zero-cost hosting and easy demonstrations. 
This document outlines exactly how to deploy the static demo to Vercel and Netlify.

## Requirements
- Node.js & pnpm installed locally.
- Git repository containing the Vajra code.

## 1. Local Build & Verification
To verify the build locally:
```bash
cd apps/web
pnpm install
NEXT_PUBLIC_STATIC_EXPORT=true pnpm run build
```
The compiled output will be generated in `apps/web/out/`. The total target size is capped under 80 MB. 
*(Note: Bundle frames are compressed and capped at 10 frames per layer to meet the 80 MB restriction).*

## 2. Deploying via Netlify Drop (Simplest)
1. Build the project locally as shown above.
2. Go to [Netlify Drop](https://app.netlify.com/drop).
3. Drag and drop the `apps/web/out/` folder into the browser.
4. Netlify will upload and serve the site immediately. 

## 3. Deploying via Git (Vercel & Netlify)
Both `vercel.json` and `netlify.toml` are provided in `apps/web/` with secure headers and SPA fallbacks pre-configured.

**Vercel / Netlify Dashboard:**
1. Import your GitHub repository.
2. Set the Root Directory to `apps/web`.
3. Build Command: `pnpm run build`
4. Output Directory: `out`
5. Environment Variables:
   - `NEXT_PUBLIC_STATIC_EXPORT=true`
   - `NEXT_PUBLIC_BASE_PATH` (Optional, if hosting in a sub-path).

## 4. Deploying via CLI
**Netlify CLI:**
```bash
npm install -g netlify-cli
cd apps/web
NEXT_PUBLIC_STATIC_EXPORT=true pnpm run build
netlify deploy --dir=out --prod
```

**Vercel CLI:**
```bash
npm install -g vercel
cd apps/web
NEXT_PUBLIC_STATIC_EXPORT=true pnpm run build
vercel --prod
```

## Static Mode Behaviour
- **Hosted static demo**: A warning banner is displayed across the UI.
- **Replay/Stream**: Runs client-side reading static JSONs (`/bundles/...`).
- **Alert Workflow**: (Draft, Approve, Cancel) state lives in browser memory only.
- **CAP 1.2 View**: Shows pre-generated messages (signed by the local dev key). Signing actually occurs in the API backend in full production deployments.
- **Privacy & Security**: Zero requests are made to external hosts (fonts/tiles self-hosted). CSP blocks external injections.

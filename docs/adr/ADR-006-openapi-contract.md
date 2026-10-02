# ADR-006: Freeze OpenAPI Contract for Parallel Tracks

**Date**: 2026-10-02
**Status**: Accepted

## Context
With the introduction of the Build-First Mode (ADR-005), multiple tracks must work in parallel to meet the deadline. Track A (engine), Track B (UI), and Track C (platform) require a stable API contract to avoid blocking each other. The backend API is not yet built (Track C), but the UI (Track B) needs a mock API to build against immediately.

## Decision
We freeze the OpenAPI contract based on the schemas defined in Phase 2 (`vajra-core` schemas). 
A script `tools/generate_openapi.py` compiles these schemas into an OpenAPI v3 spec (`docs/api/openapi.json`), representing the expected REST endpoints for frames, cells, tracks, ETA, hazards, and alerts.

1. All UI and Platform development must target this frozen specification.
2. The UI track (Track B) will use MSW (Mock Service Worker) driven by this OpenAPI JSON.
3. Any changes to the API contract must be proposed via a new ADR and version bump.

## Consequences
- Total parallelization between frontend and backend is achieved.
- Strict schema enforcement prevents integration bugs late in the cycle.
- Modifying core payloads becomes harder (requires a version bump) but provides necessary stability.

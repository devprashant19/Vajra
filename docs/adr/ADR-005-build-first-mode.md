# ADR-005: Build-First Mode

**Date**: 2026-10-02
**Status**: Accepted

## Context
With deadlines approaching, training deep learning models on large datasets (like SEVIR and MOSDAC) poses a schedule risk due to data acquisition and training time. However, the system architecture, UI, and business logic can be built and demonstrated independently of the trained ML weights.

## Decision
We adopt a "Build-First Mode" as described in `docs/05_BUILD_FIRST_MODE.md`. The system will be built end-to-end first (Phases 4 to 17) using baseline algorithms (persistence, optical flow) and rule-based hazard heads. Training is moved to a separate track (Track T) and will be switched on when real data is ready and the model passes evaluation.

To maintain honesty:
1. All layers and outputs must explicitly track their `engine` (e.g., `optical_flow`, `ml:<model_id>`) and `method` (e.g., `rule_based`, `ml:<model_id>`).
2. A three-state `skilful` flag (`"true"`, `"false"`, `"unknown"`) will be attached to outputs. Untrained models get `"unknown"`.
3. Simulated data for UI testing is strictly labelled with `status="simulated"` and cannot be used in skill claims.

## Consequences
- Unblocks UI and platform tracks (Tracks B and C) to work against mock data and frozen API contracts.
- Guarantees an honest, functional demo even if ML models are untrained by the deadline.
- Requires provenance tracking expansions in `vajra-core` (added `engine`, `method`, `skilful`).

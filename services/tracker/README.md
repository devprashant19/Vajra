# Tracker Service

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

Applies optical flow to sequence of radar frames to predict storm cell trajectories.

## Overview

This service is part of the Vajra backend microservices architecture.

## Interfaces

**Inputs**: Radar arrays (Topic: `radar.ingest`).
**Outputs**: `CellTrack` JSON (Topic: `tracks.live`).

## Architecture

Optical Flow computes motion vectors `(u, v)`. Extrapolation: `P(t+dt) = P(t) + V * dt`.

## Limitations and known issues

Optical flow math is REAL. In the demo, frames are SIMULATED and output is replayed.

## Configuration

| Variable | Description |
|---|---|
| `KAFKA_BROKERS` | Kafka connection string |

## Usage examples

```bash
<!-- skip-check -->
uv run python -m src.main
```

## Testing

Uses `pytest` for unit testing logic.

## Contents

### `tracker.py`
**Verdict**: NEW
Optical flow logic.

## Usage Restrictions

For demonstration use only.

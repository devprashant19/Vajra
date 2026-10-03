# ETA Service

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

Calculates Estimated Time of Arrival (ETA) for severe weather cells intersecting critical infrastructure.

## Overview

This service is part of the Vajra backend microservices architecture.

## Inputs / Outputs

**Inputs**: `CellTrack` objects (Topic: `tracks.live`).
**Outputs**: ETA JSON payloads (Topic: `eta.live`).

## Algorithm

Uses distance divided by storm velocity: `ETA = Distance / Velocity`.

## What is real versus simulated

The math is REAL. Intersections in the demo use SIMULATED tracks.

## Configuration

| Variable | Description |
|---|---|
| `KAFKA_BROKERS` | Kafka connection string |

## Commands

```bash
<!-- skip-check -->
uv run python -m src.main
```

## Testing

Uses `pytest` for unit testing logic.

## Contents

### `src/`
**Verdict**: IMPLEMENTED
ETA math and intersection logic.

## Usage Restrictions

For demonstration use only.

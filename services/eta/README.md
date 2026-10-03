# ETA Service

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

Calculates Estimated Time of Arrival (ETA) for severe weather cells intersecting critical infrastructure.

## Overview

This service is part of the Vajra backend microservices architecture.

## Interfaces

**Inputs**: `CellTrack` objects (Topic: `tracks.live`).
**Outputs**: ETA JSON payloads (Topic: `eta.live`).

## Architecture

Uses distance divided by storm velocity: `ETA = Distance / Velocity`.

## Limitations and known issues

The math is REAL. Intersections in the demo use SIMULATED tracks.

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

### `src/`
**Verdict**: NEW
ETA math and intersection logic.

## Usage Restrictions

For demonstration use only.

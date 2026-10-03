# Verify Service

**Origin**: NEW
**Created**: 2026-10-01
**Status**: DESIGNED

Evaluates predicted tracks and hazards against observed ground truth to compute skill scores.

## Overview

This service is part of the Vajra backend microservices architecture.

## Inputs / Outputs

**Inputs**: `CellTrack` predictions, actual observations.
**Outputs**: Skill metrics (CSI, POD, FAR).

## Algorithm

Contingency table metrics: `CSI = Hits / (Hits + Misses + False Alarms)`.

## What is real versus simulated

Currently DESIGNED. Metric computations are stubbed.

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
**Verdict**: NEW
Verification stubs.

## Usage Restrictions

For demonstration use only.

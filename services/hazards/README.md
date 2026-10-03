# Hazards Service

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

Evaluates tracked storm cells against meteorological thresholds to classify hazards (e.g., Hail, Heavy Rain).

## Overview

This service is part of the Vajra backend microservices architecture.

## Interfaces

**Inputs**: `CellTrack` objects with DBZ values.
**Outputs**: `Hazard` objects (Topic: `hazards.live`).

## Architecture

Rule-based: If `DBZ > 55`, class is Severe/Hail. If `DBZ > 45`, class is Heavy Rain.

## Limitations and known issues

Threshold evaluation is REAL. In the demo, the values evaluated are SIMULATED.

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
Threshold logic and classification.

## Usage Restrictions

For demonstration use only.

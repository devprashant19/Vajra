# Alerts Service

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

The Alerts Service correlates hazards with administrative boundaries to generate CAP 1.2 compliant warnings.

## Overview

This service is part of the Vajra backend microservices architecture.

## Inputs / Outputs

**Inputs**: `Hazard` objects (Topic: `hazards.live`).
**Outputs**: CAP 1.2 XML strings (Topic: `alerts.cap`).

## Algorithm

Spatial intersection of hazard polygons with sub-district GeoJSON shapes.

## What is real versus simulated

The GeoJSON intersection and CAP generation logic is REAL. The demo currently triggers it via SIMULATED hazard events.

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
CAP generation logic.

## Usage Restrictions

For demonstration use only.

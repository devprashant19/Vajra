# Alerts Service

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

The Alerts Service correlates hazards with administrative boundaries to generate CAP 1.2 compliant warnings.

## Overview

This service is part of the Vajra backend microservices architecture.

## Interfaces

**Inputs**: `Hazard` objects (Topic: `hazards.live`).
**Outputs**: CAP 1.2 XML strings (Topic: `alerts.cap`).

## Architecture

Spatial intersection of hazard polygons with sub-district GeoJSON shapes.

## Limitations and known issues

The GeoJSON intersection and CAP generation logic is REAL. The demo currently triggers it via SIMULATED hazard events.

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
CAP generation logic.

## Usage Restrictions

For demonstration use only.

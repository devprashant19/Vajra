# Fusion Service

**Origin**: NEW
**Created**: 2026-10-01
**Status**: DESIGNED

Designed to merge radar, satellite, and lightning data into a unified 3D weather grid.

## Overview

This service is part of the Vajra backend microservices architecture.

## Interfaces

**Inputs**: Radar, Satellite, Lightning streams.
**Outputs**: Multi-modal Data Cube.

## Architecture

Spatial-temporal interpolation onto a common 1km x 1km EPSG:4326 grid.

## Limitations and known issues

Currently DESIGNED. Not yet actively processing data in the demo.

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
Initial stubs for fusion.

## Usage Restrictions

For demonstration use only.

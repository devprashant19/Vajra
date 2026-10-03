# Ingest Service

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

Bridges external radar and meteorological sources into the Vajra internal data bus, handling decoding.

## Overview

This service is part of the Vajra backend microservices architecture.

## Inputs / Outputs

**Inputs**: Raw radar binary files (IMD format).
**Outputs**: Zarr arrays via Kafka bus (Topic: `radar.ingest`).

## Algorithm

Exact quantization for IMD binary grids: `Value = int(dBZ * scale + offset)`.

## What is real versus simulated

The decoder is REAL and decodes real IMD files. The streaming aspect is SIMULATED by the demo orchestrator.

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

### `connectors/`
**Verdict**: IMPLEMENTED
Radar decode logic.

## Usage Restrictions

For demonstration use only.

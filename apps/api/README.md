# API Server

**Origin**: NEW
**Created**: 2026-10-01
**Status**: DEMONSTRATED

The Vajra API is a FastAPI-based backend that handles ingestion bridging, WebSocket streaming of optical flow tracks, and CAP 1.2 alert generation.

## Overview

It provides REST endpoints and WebSocket channels. The API integrates with Kafka/Redis in production and falls back to mock bundles for the demo.

## Interfaces

| Tag | Route | Description | Auth Role |
|---|---|---|---|
| CAP | `POST /alerts/cap` | Generates a CAP 1.2 XML alert | `admin` |
| Scenarios | `GET /scenarios` | Lists available demo scenarios | `public` |
| Stream | `WS /ws` | Streams radar cell updates | `public` |

## Interfaces

WebSocket stream emits JSON packets matching the `CellTrack` and `Hazard` schemas every 2 seconds during playback.

## Overview

Alert generation enforces strict validation and is logged to a secure audit trail before signing (simulated).

## Overview

In static mode, bundles are served as static files. In API mode, the API reads them from `demo/bundles/` and serves them.

## Overview

Standardized HTTP 400/500 JSON responses following RFC 7807 (Problem Details).

## Configuration

| Variable | Description |
|---|---|
| `DATABASE_URL` | Postgres URL |
| `REDIS_URL` | Redis URL |
| `KAFKA_BROKERS` | Kafka brokers |

## Usage examples

```bash
<!-- skip-check -->
uv run uvicorn src.api.main:app
```

## Benchmarks

<!-- stats:start -->
- **Latency (p95)**: {API_LATENCY}
- **Throughput**: {API_THROUGHPUT}
<!-- stats:end -->

## Testing

Uses `pytest` for unit testing.

## Contents

### `src/api/`
**Verdict**: NEW
FastAPI routes and main application.

### `tests/`
**Verdict**: NEW
Unit tests.

## Usage Restrictions

For demonstration use only.

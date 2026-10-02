# Vajra API Documentation

## REST API
The REST API is documented in `openapi.json` and implements the core queries for cells, ETAs, alerts, and metadata.
It relies on OIDC authentication (via Keycloak) and includes provenance envelopes on every response.

## Tiles
Tiles are available at `/v1/tiles/{layer}/{z}/{x}/{y}`. 
URL scheme relies on immutable tile patterns keyed by `valid_time`. Caching headers (ETag, Cache-Control) are provided for CDN edge caching.

## WebSocket and SSE Stream
The stream endpoint at `/v1/stream` supports WebSocket and SSE.
- **Heartbeat**: Every 15 seconds.
- **Resume**: Provide `?last_sequence=<num>` when connecting.
- **Envelope Schema**: Defined in `stream.schema.json`.
- **Message Types**: `cell.updated`, `eta.updated`, `alert.issued`, `source.status`, `replay.state`.

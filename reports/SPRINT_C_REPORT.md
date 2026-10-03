# Sprint C Report

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

[<- Back to Index](../docs/INDEX.md)

## 1. SERVE BUNDLES
- PASS: `/v1/status` updated to report source. `demo/bundles/` loaded if present, example mocks fallback gracefully.

## 2. STREAM
- PASS: WebSocket `/v1/stream` endpoint added with ReplayClock controls (start/pause/seek) and heartbeats.

## 3. ALERTS
- PASS: Implemented `AlertDraft` checking skilful conditions, kill-switch under 1s blocking API, hash-chained `AUDIT_LOG` with verify endpoint, mock webhook dispatcher, XSD cap validation, 20min deduplication. 

## 4. TESTS
- PASS: Pytest coverage for openapi format, role checks, dedup, kill switch, XSD validation and audit chain verification. Benchmark stats posted to `reports/bench/api.json`.

## 5. DEMO SCRIPT
- PASS: `just demo` handles dockerized flow. Included `demo.ps1` for local No-Docker execution of `uvicorn` and `pnpm`.

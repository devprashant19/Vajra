# Phase 2 Plan: Contracts and Platform Kernel

## Objective
Build `packages/vajra-core` and `packages/vajra-types` which serve as the shared contracts and database schema for all subsequent services. No other module should bypass these core components.

## Tasks and Files
1. **Grid and Geometry (`packages/vajra-core/src/vajra_core/grid/`)**:
   - `spec.py`: GridSpec for national (2km) and regional (1km) grids.
   - `tiling.py`: Tile scheme (256x256), overlap, global IDs, coordinate translations.
   - `h3_idx.py`: H3 helpers (res 7, 8).
   - *ADR-003*: Document CRS choice (equal-area projection vs EPSG:4326).
2. **Variable Registry (`packages/vajra-core/src/vajra_core/registry/`)**:
   - `variables.py`: Registry for all variables (reflectivity, VIL, CAPE, etc.) with units, ranges, dtypes, and fill values.
3. **Time (`packages/vajra-core/src/vajra_core/time/`)**:
   - `clock.py`: `Clock` interface, `RealClock`, `ReplayClock` (UTC internally, IST display).
4. **Provenance (`packages/vajra-core/src/vajra_core/provenance/`)**:
   - `models.py`: Enum `Status` and envelope `Provenanced[T]`.
5. **Schemas & TS Generation (`packages/vajra-core/src/vajra_core/schemas/`)**:
   - `domain.py`: Pydantic models (RawEvent, FusedFrameRef, Cell, Alert, etc.).
   - `tools/generate_ts.py`: Script to generate `packages/vajra-types/` using OpenAPI/JSON schema.
6. **Abstractions (`packages/vajra-core/src/vajra_core/abstractions/`)**:
   - `store.py`: `ObjectStore` (LocalFS, S3).
   - `bus.py`: `EventBus` (InMemory, Redis Streams, Kafka/Redpanda API).
   - `cache.py`: `Cache` (InMemory, Redis).
7. **Database (`packages/vajra-core/src/vajra_core/db/`)**:
   - Alembic setup with `timescale/timescaledb-ha:pg16-latest` image.
   - Tables: sources, scans, cells, alerts, thresholds, model_registry, etc. Spatial and time indexes.
8. **Config (`packages/vajra-core/src/vajra_core/config/`)**:
   - `settings.py`: Pydantic settings with lite/full/national profiles.
9. **Error & Logging (`packages/vajra-core/src/vajra_core/logging/`)**:
   - Structured JSON logging and error taxonomy.
10. **Infra (`infra/docker-compose.yml`)**:
    - Add low-memory configurations: Postgres (small shared_buffers), Redpanda (single-core, 1GB max), Redis/MinIO default small.

## Testing Strategy
- **Property-based tests** (Hypothesis) for grids, time, provenance logic, H3 indexing.
- **Integration/Contract tests** running across InMemory vs. Redis/Kafka/Postgres implementations (Docker needed).
- **Alembic tests**: upgrade/downgrade cycles on an empty database.
- **TypeScript compilation check**: Validate that generated TS interfaces compile correctly.
- **Coverage**: Minimum 85% for `vajra-core` and strict `mypy` typing.

## Risks and Mitigation
- **Docker Dependency**: Since Windows native testing lacks a Docker daemon in my environment, integration tests for real buses (Redis, Redpanda, Postgres) may fail or get skipped locally. I will implement them properly using `pytest.skip` blocks if the daemon is unreachable, but configure GitHub Actions CI to run them strictly.
- **Memory Constrains**: Limiting Redpanda/Postgres memory is crucial to ensure `just up-full` runs efficiently on 16GB machines.

## Work Process
I will implement each logical module above step-by-step, committing via Conventional Commits after every feature is built, tested, and linted.

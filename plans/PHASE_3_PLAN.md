# Phase 3 Plan: Real data acquisition and data lake

## Tasks

1. **Source Verification & Strategy**
   - Check and verify URLs/DOIs for MOSDAC, Earthdata, Copernicus CDS, Kaggle BharatBench, SEVIR, IMD, Blitzortung, etc.
   - Produce `docs/data/SOURCE_STATUS.md` mapping each source to its verification status (live/UNVERIFIED).
   - Produce `docs/data/DATA_STRATEGY.md` classifying sources into Tier 0-3 and the SEVIR transfer-learning track.

2. **Acquisition Tooling & Runbook**
   - Develop `services/ingest/archive/downloaders.py` containing rate-limited, resumable downloaders for each data source. The downloaders will rely exclusively on credentials from `.env` and fail gracefully (returning `needs_credentials` status) if absent.
   - Implement manifest generation and automatic README generation using the data template.
   - Write `docs/data/ACQUISITION_RUNBOOK.md` for human operators to follow to set up accounts and start downloads.

3. **Event Library & Data Lake Setup**
   - Create `data/events/events.yaml` with ~15 Indian convective events (referenced with public URLs) plus the SEVIR subset.
   - Build a catalog generation script `services/ingest/catalog_builder.py` that scans the raw lake, validates contents, and writes `data/catalog/catalog.parquet`.

4. **Coverage Profiling**
   - Implement `ml/data_profile/profiler.py` to analyze the catalog output and construct cross-tabulations of data availability (time x modality x region).
   - Produce `reports/DATA_COVERAGE.md` containing the heatmaps and the final Decision Table deciding whether we can train on real Indian data.

## Risks
- Lack of credentials (.env is missing) will cause all Tier 2+ downloaders to skip, but this is handled gracefully per requirements.
- Rate limits or missing URLs from third-party APIs. We must verify them closely.

## Test List
- Offline downloaders test (mocked HTTP).
- Catalog schema and validation tests (duplicates, verdicts).
- README generator tests.
- Events schema and validation tests.
- Coverage profiling mock tests.

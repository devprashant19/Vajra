# PR #1 Integration Report

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

[<- Back to Index](../docs/INDEX.md)

**Date:** 2026-10-02
**PR:** `feat/imerg-timeseries` (from Hridanshu4004)
**Target Branch:** `integrate/pr-1-benchmark`

## 1. Review Findings
- **Files changed:** `data/benchmark/events_benchmark.csv`, `data/benchmark/controls.csv`, `data/benchmark/events_auto.csv`, `tools/download_imerg.py`, `tools/download_imd_extended.py`, `tests/test_benchmark.py`, `tests/test_imerg.py`, etc.
- **Sensitive Data & Size:** No `.env`, keys, or tokens committed. `gitleaks` verified clean.
- **Data/Raw:** No files were committed to `data/raw`.
- **Hooks & CI:** Scripts were added, but no changes altered core CI/hooks unsafely.
- **Dependencies:** Added `earthaccess`, `h5netcdf`, `imdlib`, `xarray`, `rioxarray`, `rasterio` etc. Verified they are genuine PyPI packages and compatible with the Python 3.12 pin.
- **Credentials:** `tools/download_imerg.py` safely used `os.environ.get()` and `earthaccess.login(strategy="environment")`. No hardcoded credentials.

## 2. Merge & Conflict Resolution
- **`pyproject.toml`:** Resolved conflict by accepting union of PR's dependencies while preserving Python 3.12 pin and workspace settings. Added `openapi-spec-validator` to fix test errors.
- **`uv.lock`:** Regenerated using `uv lock`.
- **`data/events/events.yaml`:** Discarded PR's manual file and used a Python script to merge `events_benchmark.csv` data (lat, lon, geometry type, labels) with the project schema, retaining `citation_url`, `retrieval_date`, and `http_status`. Re-added the SEVIR fallback.
- **Authorship:** Merged cleanly via `git merge`, preserving Hridanshu4004's original commits.

## 3. Data Terms Documentation
- Documented IMD Gridded Rainfall (0.25 deg) and Copernicus DEM terms in `docs/THIRD_PARTY.md` and `docs/data/SOURCE_STATUS.md`. Both were marked `UNVERIFIED` pending full access confirmation.
- Created `data/benchmark/README.md` following the Data Template. Formatter `check_readme_format.py` passed.

## 4. Test Pass Results
- Tests dependent on IMD files/network (e.g., `test_control_constraints`) were marked `@pytest.mark.data` and correctly skip when `data/benchmark/controls.csv` is absent.
- Cleared out duplicate placeholder tests that were breaking `pytest` collection due to import mismatches.
- **Unit count:** 108
- **Live/Data count:** 4
- **Integration count:** 0 
- **Total collected:** 112 tests

## 5. Downloader Unification
- Extracted `download_and_process_imerg()` from `tools/download_imerg.py` into `services/ingest/archive/downloaders.py` to maintain a single archive downloader registry.
- Deleted `tools/download_imerg.py` to remove duplicate. Preserved `tests/test_imerg.py`.

## 6. Strategy & Labels
- Added the `daily-grid heavy rain` labels (strong, weak, context_only) to the data strategy.
- Updated `docs/data/DATA_STRATEGY.md` with explicit limitations: daily 25km grids **cannot verify cloudbursts** (hourly/local). 
- Marked `events_auto.csv` purely as unverified "candidates," not cited events. `context_only` explicitly excludes rainfall hazard.

## Conclusion
Integration is complete.

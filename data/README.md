# Vajra Data Directory

This directory holds the data for the Vajra real-time convective-scale nowcasting platform.

## Structure

*   **`reference/`**: Holds reference datasets, catalogs, and static mapping files (e.g., `SEVIR_CATALOG.csv`, projections).
*   **`catalog/`**: Holds generated tranche/selection lists and filtered views (e.g., `sevir_tranche1_events.csv`).
*   **`sevir_extracted/`**: Holds the Zarr shards and `manifest.json` for the exact events extracted from the S3 bucket using the remote extraction pipeline.
*   **`interim/`**: Holds intermediate processing files before they are loaded into the data lake (DuckDB/PostGIS).

## Storage Rules

*   **Do not commit data files:** All directories contain `.gitignore` or exclude rules for large datasets.
*   **Ephemeral processing:** Files in `interim/` and raw downloads must be deleted after being ingested or converted to Zarr to save disk space.

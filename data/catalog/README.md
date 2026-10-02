# Vajra Data Catalogs

This directory contains filtered and processed event selections used to drive the extraction and processing pipelines.

## Files

*   **`sevir_tranche1_events.csv`**: The exact list of events selected from the SEVIR catalog that meet the project criteria (modalities present, temporal distribution, severe types). This file drives the `tools/sevir_extract_remote.py` script.

## Maintenance

These files are reproducible from the original `data/reference/SEVIR_CATALOG.csv` using the offline selection scripts. They are kept here for exact repeatability of extraction runs.

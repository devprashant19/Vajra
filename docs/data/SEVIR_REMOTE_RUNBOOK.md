# SEVIR Remote Extraction Runbook

When the local network route to `sevir.s3.amazonaws.com` is severely throttled (e.g. 0.06 MB/s), it is impossible to download the datasets directly to the workspace in a reasonable time.

To bypass this, we run a remote extraction script on a free cloud notebook with a fast AWS connection (like Google Colab or Kaggle).

## Prerequisites
1. A Google Colab or Kaggle account.
2. The `data/catalog/sevir_tranche1_events.csv` file generated locally.
3. The `tools/sevir_extract_remote.py` script.

## Steps

### 1. Setup the Cloud Environment
1. Create a new notebook in Google Colab.
2. In the first cell, install the dependencies:
   ```bash
   !pip install pandas h5py zarr fsspec s3fs requests
   ```

### 2. Upload the Catalog
1. In Colab, create the required directories:
   ```bash
   !mkdir -p data/catalog
   ```
2. Upload `sevir_tranche1_events.csv` from your local machine to `data/catalog/` in the Colab file browser.
3. Upload `sevir_extract_remote.py` to the root directory.

### 3. Run the Extraction
1. Execute the script in a notebook cell:
   ```bash
   !python sevir_extract_remote.py
   ```
2. The script will output its progress. It uses fast S3 access to ranged-read only the specific events required. It writes Zarr shards to `data/sevir_extracted/` and maintains a resumable `manifest.json`.

### 4. Download the Extracted Data
1. Once completed, zip the extracted data:
   ```bash
   !zip -r sevir_extracted.zip data/sevir_extracted
   ```
2. Download `sevir_extracted.zip` to your local machine.
3. Extract the ZIP into `data/interim/` in your local workspace.

### 5. Verification
1. Compare the local `manifest.json` against the extracted files to ensure all `eventId_modality.zarr` directories are present.
2. The checksums or integrity of the arrays can be verified by attempting to load each Zarr shard.

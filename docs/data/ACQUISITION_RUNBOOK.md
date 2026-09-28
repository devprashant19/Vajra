# Data Acquisition Runbook

This runbook instructs human operators on how to acquire credentials for the external data sources and initiate Vajra's automated acquisition pipelines.

## 1. MOSDAC Account
1. Go to https://mosdac.gov.in
2. Register for an academic/research account.
3. Wait 1-2 days for approval.
4. Add to `.env`:
   ```env
   MOSDAC_USERNAME=your_username
   MOSDAC_PASSWORD=your_password
   ```
5. Expected download time for a major event (e.g. Cyclone Amphan): ~2-4 hours (~20 GB).

## 2. NASA Earthdata Login
1. Go to https://urs.earthdata.nasa.gov
2. Register for a free account.
3. Add to `.env`:
   ```env
   EARTHDATA_USERNAME=your_username
   EARTHDATA_PASSWORD=your_password
   ```

## 3. Copernicus CDS
1. Go to https://cds.climate.copernicus.eu
2. Register for an account.
3. Retrieve your Personal Access Token from your profile.
4. Add to `.env`:
   ```env
   CDS_API_KEY=your_key
   ```

## 4. Kaggle
1. Go to https://kaggle.com
2. Log in and go to your Account settings.
3. Create a New API Token (`kaggle.json`).
4. Add to `.env`:
   ```env
   KAGGLE_USERNAME=your_username
   KAGGLE_KEY=your_token
   ```

## 5. Institutional Access (IMD / IITM)
- For IMD raw DWR scans and IITM ILLN, please file a request letter through your mentor/institution.
- Note the outcome and communicate access keys via `.env` if provided.

## Starting the Downloads
Once credentials are in `.env`, run the acquisition script:
```bash
uv run python services/ingest/archive/download_events.py
```
The script will estimate file sizes and prompt for approval for any individual artifact > 5 GB.

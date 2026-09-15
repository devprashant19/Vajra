# External Data Sources Referenced Across Projects

## Radar Data

### 1. IMD Doppler Weather Radar (DWR) Network
- **URL**: https://mausam.imd.gov.in (operational), https://dd.imd.gov.in (data)
- **Referenced by**: SIH, NEXUS-NOWCAST, AeroCast-Now-AI, SIH-NowCasting, STORMTRACE
- **Access Method**: Research request to IMD; some volume scans on Zenodo
- **Credentials**: Institutional agreement required for real-time feed
- **Format**: CfRadial / SWEEP (via pyiwr), polar volume scans
- **Zenodo Archive**: `10.6084/m9.figshare.22704910` (referenced by SIH README)
- **Used for**: Reflectivity composites, VIL, echo top, radial velocity

### 2. MOSDAC (Meteorological and Oceanographic Satellite Data Archival Centre)
- **URL**: https://mosdac.gov.in
- **Referenced by**: SIH, AeroCast-Now-AI, SIH-NowCasting, STORMTRACE
- **Access Method**: Free registration (1-2 day approval), HTTP API
- **Credentials**: MOSDAC_USERNAME / MOSDAC_PASSWORD (optional for browse imagery)
- **Format**: HDF5/NetCDF (Level-1B calibrated products), JPEG (browse imagery)
- **Used for**: INSAT-3D/3DR/3DS TIR, WV, MIR channels; brightness temperature

## Satellite Data

### 3. INSAT-3D/3DR/3DS Imager & Sounder
- **URL**: https://mosdac.gov.in (via MOSDAC portal above)
- **Referenced by**: All five projects
- **Access Method**: MOSDAC registration
- **Credentials**: MOSDAC account
- **Format**: HDF5 (L1B), NetCDF (L2), JPEG (browse)
- **Channels**: TIR1 (10.8µm), TIR2 (12.0µm), WV (6.7µm), MIR (3.9µm), VIS (0.65µm)
- **Used for**: Cloud-top temperature, convective cloud identification, split-window CI detection

## Lightning Data

### 4. ILLN (Indian Lightning Location Network) - IITM Pune
- **URL**: Not publicly accessible
- **Referenced by**: SIH, NEXUS-NOWCAST
- **Access Method**: Research collaboration with IITM Pune
- **Credentials**: Institutional agreement required
- **Format**: Point data (time, lat, lon, type, amplitude)
- **Used for**: Lightning stroke density rasterization

### 5. Blitzortung
- **URL**: https://www.blitzortung.org
- **Referenced by**: AeroCast-Now-AI, SIH-NowCasting, STORMTRACE
- **Access Method**: WebSocket/TCP feed, contributor credentials
- **Credentials**: BLITZORTUNG_USER / BLITZORTUNG_PASSWORD
- **Format**: JSON/binary stream (real-time), CSV (archive)
- **Used for**: Real-time lightning location, flash density maps

### 6. NASA GPM-LIS (Lightning Imaging Sensor)
- **URL**: https://disc.gsfc.nasa.gov (GES DISC)
- **Referenced by**: SIH
- **Access Method**: NASA Earthdata login (free registration)
- **Credentials**: EARTHDATA_USERNAME / EARTHDATA_PASSWORD
- **Format**: HDF5/NetCDF
- **Used for**: Total lightning flash rate climatology, fallback for ILLN

### 7. WWLLN (World Wide Lightning Location Network)
- **URL**: http://wwlln.net
- **Referenced by**: SIH
- **Access Method**: Research agreement with WWLLN consortium
- **Credentials**: Institutional agreement
- **Format**: CSV
- **Used for**: Global lightning location fallback

### 8. WGLC (World Global Lightning Climatology)
- **URL**: https://doi.org/10.5067/LIS/LIS-OTD/DATA303
- **Referenced by**: STORMTRACE
- **Access Method**: NASA Earthdata
- **Credentials**: Earthdata login
- **Format**: HDF5
- **Used for**: Baseline lightning climatology

## NWP / Reanalysis Data

### 9. NCMRWF IMDAA / NGFS / NCUM
- **URL**: https://rds.ncmrwf.gov.in
- **Referenced by**: SIH
- **Access Method**: NCMRWF RDS portal (research access)
- **Credentials**: Registration required
- **Format**: GRIB2 / NetCDF
- **Variables**: CAPE, CIN, PWAT, 0-6km Bulk Shear (12 km resolution)
- **Used for**: Thermodynamic environment, convective potential

### 10. ERA5 (ECMWF Reanalysis v5)
- **URL**: https://cds.climate.copernicus.eu
- **Referenced by**: AeroCast-Now-AI, STORMTRACE
- **Access Method**: CDS API (free registration)
- **Credentials**: CDS_API_KEY
- **Format**: GRIB2 / NetCDF
- **Variables**: CAPE, CIN, wind shear, temperature profiles
- **Used for**: NWP thermodynamic sounding, training data source

### 11. Open-Meteo
- **URL**: https://open-meteo.com
- **Referenced by**: AeroCast-Now-AI, SIH-NowCasting
- **Access Method**: Free REST API (no key required for basic use)
- **Credentials**: None for basic tier; API key for commercial
- **Format**: JSON
- **Used for**: Real-time CAPE, CIN, surface observations (fallback for NWP)

### 12. GFS (Global Forecast System)
- **URL**: https://nomads.ncep.noaa.gov
- **Referenced by**: NEXUS-NOWCAST, STORMTRACE
- **Access Method**: Free HTTP/OPeNDAP
- **Credentials**: None
- **Format**: GRIB2
- **Used for**: Synoptic-scale thermodynamic fields

## Precipitation Data

### 13. NASA GPM IMERG
- **URL**: https://disc.gsfc.nasa.gov
- **Referenced by**: STORMTRACE
- **Access Method**: NASA Earthdata login
- **Credentials**: EARTHDATA_USERNAME / EARTHDATA_PASSWORD
- **Format**: HDF5/NetCDF
- **Used for**: Satellite-derived precipitation estimates

### 14. RainViewer
- **URL**: https://www.rainviewer.com/api.html
- **Referenced by**: AeroCast-Now-AI
- **Access Method**: Free REST API
- **Credentials**: None for basic use
- **Format**: Tile images (PNG)
- **Used for**: Real-time radar composite tiles (global, not DWR-specific)

## Benchmark Datasets

### 15. MoES BharatBench
- **URL**: https://kaggle.com/datasets/maslab/bharatbench
- **Referenced by**: SIH
- **Access Method**: Kaggle download (free)
- **Credentials**: Kaggle account
- **Format**: NetCDF
- **Used for**: ERA5-derived India-gridded benchmark for pretraining

### 16. SEVIR (Storm Event Imagery)
- **URL**: https://doi.org/10.7910/DVN/DBMQHO (Harvard Dataverse)
- **Referenced by**: AeroCast-Now-AI
- **Access Method**: Direct download
- **Credentials**: None
- **Format**: HDF5 + CSV catalog
- **Used for**: US storm event imagery catalog (NOTE: not Indian data)
- **Licence**: CC BY-NC-SA 4.0

## Geographic Data

### 17. India District Boundaries
- **Source**: Natural Earth / Census of India (exact provenance unclear)
- **Referenced by**: AeroCast-Now-AI, STORMTRACE
- **Access Method**: GeoJSON files bundled in repos
- **Format**: GeoJSON
- **Note**: Should verify Survey of India (SOI) compliance for official use

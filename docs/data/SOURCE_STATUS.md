# Data Source Status Verification

| Source | Identifier / URL | Status | Credentials | Licence / Terms | Format | Est. Size | Time Coverage |
|---|---|---|---|---|---|---|---|
| **SIH Reference (Figshare)** | https://doi.org/10.6084/m9.figshare.22704910 | **LIVE** | None | CC BY 4.0 (assumed for figshare unless noted) | Archive | ~Varies | Historical |
| **Open-Meteo** | https://open-meteo.com | **LIVE** | None (Basic) | Non-commercial free | JSON | Tiny | Real-time / Forecast |
| **GFS (NOMADS)** | https://nomads.ncep.noaa.gov | **LIVE** | None | Public Domain | GRIB2 | Large per run | Real-time |
| **MOSDAC** | https://mosdac.gov.in | **LIVE** | `MOSDAC_USERNAME` | Research/Academic use | HDF5, JPEG | Large | Real-time & Archive |
| **Earthdata (NASA)** | https://disc.gsfc.nasa.gov | **LIVE** | `EARTHDATA_USERNAME` | Public Domain / Open | HDF5, NetCDF | Large | Historical |
| **Copernicus CDS (ERA5)** | https://cds.climate.copernicus.eu | **LIVE** | `CDS_API_KEY` | Copernicus Open (Free for research) | GRIB2 / NetCDF | Medium | Reanalysis |
| **Kaggle BharatBench** | https://kaggle.com/datasets/maslab/bharatbench | **LIVE** | Kaggle Token | Open/Varies | NetCDF | Medium | Pre-computed dataset |
| **SEVIR (Harvard Dataverse)** | https://doi.org/10.7910/DVN/DBMQHO | **UNVERIFIED (404)** | None | CC BY-NC-SA 4.0 | HDF5 + CSV | >40 GB total | 2017-2019 (US only) |
| **Blitzortung** | https://www.blitzortung.org | **LIVE** | `BLITZORTUNG_USER` | Restrictions on redistribution | JSON / CSV | Small | Real-time & Archive |
| **IMD DWR Network** | https://dd.imd.gov.in / Research | **UNVERIFIED** | Institutional | Research / Restricted | CfRadial | Huge | Real-time (if access granted) |
| **ILLN (IITM Pune)** | Institutional Request | **UNVERIFIED** | Institutional | Research / Restricted | Point data | Small | Real-time |

Note: `needs_credentials` status is reported for MOSDAC, Earthdata, Copernicus CDS, Kaggle, Blitzortung, IMD DWR, and ILLN as `.env` credentials are not currently present.

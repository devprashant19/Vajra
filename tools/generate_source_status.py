import json
import os

def generate():
    os.makedirs("docs/data", exist_ok=True)
    with open("reports/bench/source_probe.json", "r") as f:
        results = json.load(f)

    # Manual notes for terms of use, format, size, time coverage
    notes = {
        "figshare_sih": {
            "credentials": "No",
            "licence": "CC BY 4.0",
            "terms_url": "https://figshare.com/articles/dataset/NEXUS_Data/22704910",
            "formats": "NetCDF/HDF5",
            "size": "Unknown",
            "coverage": "Unknown"
        },
        "open_meteo": {
            "credentials": "No",
            "licence": "CC BY 4.0 (Non-commercial API)",
            "terms_url": "https://open-meteo.com/en/terms",
            "formats": "JSON, Parquet",
            "size": "Variable",
            "coverage": "Historical & Forecast"
        },
        "nomads_gfs": {
            "credentials": "No",
            "licence": "Public Domain (US Govt)",
            "terms_url": "https://nomads.ncep.noaa.gov/txt_descriptions/Data_Access_Policy.txt",
            "formats": "GRIB2",
            "size": "Terabytes",
            "coverage": "Recent forecast cycles"
        },
        "mosdac": {
            "credentials": "Yes",
            "licence": "ISRO Data Policy",
            "terms_url": "https://mosdac.gov.in/data-policy",
            "formats": "HDF5",
            "size": "Terabytes",
            "coverage": "Historical & Real-time INSAT"
        },
        "earthdata": {
            "credentials": "Yes",
            "licence": "Public Domain / NASA Earthdata Policy",
            "terms_url": "https://earthdata.nasa.gov/earth-observation-data/data-use-policy",
            "formats": "HDF5, NetCDF",
            "size": "Petabytes",
            "coverage": "Historical & Near Real-time"
        },
        "cds": {
            "credentials": "Yes",
            "licence": "Copernicus License",
            "terms_url": "https://cds.climate.copernicus.eu/api-how-to",
            "formats": "GRIB, NetCDF",
            "size": "Petabytes",
            "coverage": "Historical ERA5"
        },
        "kaggle_bharatbench": {
            "credentials": "Yes",
            "licence": "Unknown",
            "terms_url": "https://www.kaggle.com/datasets/maslab/bharatbench",
            "formats": "Unknown",
            "size": "Unknown",
            "coverage": "Unknown"
        },
        "sevir_dataverse": {
            "credentials": "No",
            "licence": "MIT License",
            "terms_url": "https://doi.org/10.7910/DVN/DBMQHO",
            "formats": "HDF5",
            "size": "Terabytes",
            "coverage": "2018-2019 US"
        },
        "sevir_aws": {
            "credentials": "No",
            "licence": "MIT License",
            "terms_url": "https://registry.opendata.aws/sevir/",
            "formats": "HDF5",
            "size": "1TB+",
            "coverage": "2018-2019 US"
        },
        "blitzortung": {
            "credentials": "No",
            "licence": "Non-commercial only",
            "terms_url": "https://www.blitzortung.org/en/contact.php",
            "formats": "Custom",
            "size": "Variable",
            "coverage": "Real-time"
        }
    }

    lines = [
        "# Source Status",
        "",
        "| Source | Reachable | Credentials | Licence / Terms | Format | Est. Size | Coverage |",
        "|---|---|---|---|---|---|---|"
    ]

    for name, res in results.items():
        status = res.get("status")
        reachable = "✅" if status in (200, 201, 202, 301, 302, 303, 307, 308) else f"❌ ({status})"
        note = notes.get(name, {})
        cred = note.get("credentials", "UNVERIFIED")
        lic = note.get("licence", "UNVERIFIED")
        url = note.get("terms_url", "")
        if url:
            lic = f"[{lic}]({url})"
        fmt = note.get("formats", "UNVERIFIED")
        size = note.get("size", "UNVERIFIED")
        cov = note.get("coverage", "UNVERIFIED")
        
        lines.append(f"| {name} | {reachable} | {cred} | {lic} | {fmt} | {size} | {cov} |")

    with open("docs/data/SOURCE_STATUS.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    generate()

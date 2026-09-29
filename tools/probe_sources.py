import urllib.request
import urllib.error
import ssl
import json
import os
from datetime import datetime

URLS = {
    "figshare_sih": "https://doi.org/10.6084/m9.figshare.22704910",
    "open_meteo": "https://open-meteo.com",
    "nomads_gfs": "https://nomads.ncep.noaa.gov",
    "mosdac": "https://mosdac.gov.in",
    "earthdata": "https://disc.gsfc.nasa.gov",
    "cds": "https://cds.climate.copernicus.eu",
    "kaggle_bharatbench": "https://www.kaggle.com/datasets/maslab/bharatbench",
    "sevir_dataverse": "https://doi.org/10.7910/DVN/DBMQHO",
    "sevir_aws": "https://sevir.mit.edu/",
    "blitzortung": "https://www.blitzortung.org"
}

def probe():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    results = {}
    
    for name, url in URLS.items():
        entry = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": None,
            "final_url": None,
            "error": None,
            "headers": {}
        }
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req, context=ctx, timeout=10)
            entry["status"] = res.getcode()
            entry["final_url"] = res.geturl()
            # Capture interesting headers
            for k in ["Content-Type", "Server", "Location"]:
                if k in res.headers:
                    entry["headers"][k] = res.headers[k]
        except urllib.error.HTTPError as e:
            entry["status"] = e.code
            entry["error"] = str(e.reason)
        except Exception as e:
            entry["error"] = str(e)
            
        results[name] = entry
        print(f"Probed {name}: {entry.get('status')} {entry.get('error') or ''}")

    os.makedirs("reports/bench", exist_ok=True)
    with open("reports/bench/source_probe.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    probe()

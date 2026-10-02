import os
import json
import hashlib
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any, List

class DownloaderConfig:
    def __init__(self, name: str, env_vars: List[str], base_url: str, licence_text: str):
        self.name = name
        self.env_vars = env_vars
        self.base_url = base_url
        self.licence_text = licence_text

class Downloader:
    def __init__(self, config: DownloaderConfig, data_dir: str = "data/raw"):
        self.config = config
        self.data_dir = data_dir
        self.output_dir = os.path.join(data_dir, config.name)
        
    def _check_credentials(self) -> bool:
        for var in self.config.env_vars:
            if not os.environ.get(var):
                return False
        return True

    def _estimate_size(self, url: str) -> Optional[int]:
        try:
            req = urllib.request.Request(url, method="HEAD")
            res = urllib.request.urlopen(req, timeout=10)
            length = res.headers.get("Content-Length")
            return int(length) if length else None
        except Exception:
            return None
            
    def _generate_readme(self, files_info: List[Dict[str, Any]]):
        os.makedirs(self.output_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        contents_md = ""
        for f in files_info:
            size_mb = f['size'] / (1024 * 1024) if f['size'] else 0
            contents_md += f"### {f['filename']} ({size_mb:.2f} MB)\n"
            contents_md += f"- **Verdict**: REAL — Downloaded from {self.config.name}\n"
            contents_md += f"- **Time Range**: Varies\n"
            contents_md += f"- **Domain**: India / Global\n"
            contents_md += f"- **Variables**: Varies\n"
            contents_md += f"- **Shape**: Varies\n"
            contents_md += f"- **Useful for**: training, validation\n"
            contents_md += f"- **Source**: {self.config.name}\n"
            contents_md += f"- **Licence**: {self.config.licence_text}\n"
            contents_md += f"- **Note**: Auto-generated during download\n\n"
            
        readme_content = f"""# {self.config.name} Reference Data

**Origin**: {self.config.base_url} (Official archive)
**Downloaded**: {date_str}

## Contents

{contents_md}
## Usage Restrictions
{self.config.licence_text}
"""
        with open(os.path.join(self.output_dir, "README.md"), "w") as f:
            f.write(readme_content)

    def download(self, relative_path: str, url: str, expected_sha256: str = "", dry_run: bool = False) -> str:
        if not self._check_credentials():
            print(f"[{self.config.name}] needs_credentials: Missing {self.config.env_vars}")
            return "needs_credentials"
            
        est_size = self._estimate_size(url)
        size_str = f"{est_size / (1024*1024*1024):.2f} GB" if est_size else "Unknown"
        print(f"[{self.config.name}] Estimated size: {size_str} for {relative_path}")
        
        if est_size and est_size > 5 * 1024 * 1024 * 1024 and not dry_run:
            print(f"[{self.config.name}] Download exceeds 5 GB. Asking human.")
            return "needs_approval"
            
        if dry_run:
            print(f"[{self.config.name}] Dry run complete for {relative_path}.")
            return "success_dry_run"
            
        target_path = os.path.join(self.output_dir, relative_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Resumable download logic
        headers = {}
        if os.path.exists(target_path):
            existing_size = os.path.getsize(target_path)
            if est_size and existing_size == est_size:
                print(f"[{self.config.name}] File already downloaded.")
                return "success_cached"
            headers["Range"] = f"bytes={existing_size}-"
            mode = "ab"
        else:
            existing_size = 0
            mode = "wb"
            
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as res, open(target_path, mode) as f:
                while True:
                    chunk = res.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    
            if expected_sha256:
                h = hashlib.sha256()
                with open(target_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        h.update(chunk)
                if h.hexdigest() != expected_sha256:
                    print(f"[{self.config.name}] Checksum mismatch! Quarantining file.")
                    os.rename(target_path, target_path + ".quarantine")
                    return "checksum_mismatch"
                    
            manifest_path = target_path + ".manifest.json"
            manifest_data = {
                "source": self.config.name,
                "url": url,
                "downloaded_at": datetime.now().isoformat(),
                "size_bytes": os.path.getsize(target_path)
            }
            with open(manifest_path, "w") as mf:
                json.dump(manifest_data, mf)
                
            self._generate_readme([{"filename": relative_path, "size": manifest_data["size_bytes"]}])
            time.sleep(1) # Rate limiting
            return "success"
            
        except urllib.error.HTTPError as e:
            if e.code in [401, 403]:
                print(f"[{self.config.name}] needs_credentials: HTTP {e.code}")
                return "needs_credentials"
            return "error"
        except Exception as e:
            print(f"[{self.config.name}] Error: {e}")
            return "error"

# Pre-configured instances
MOSDAC = DownloaderConfig("mosdac", ["MOSDAC_USERNAME", "MOSDAC_PASSWORD"], "https://mosdac.gov.in", "Research and academic use only.")
EARTHDATA = DownloaderConfig("earthdata", ["EARTHDATA_USERNAME", "EARTHDATA_PASSWORD"], "https://disc.gsfc.nasa.gov", "Public Domain.")
CDS = DownloaderConfig("cds", ["CDS_API_KEY"], "https://cds.climate.copernicus.eu", "Copernicus Open (Free for research).")
KAGGLE = DownloaderConfig("kaggle", ["KAGGLE_USERNAME", "KAGGLE_KEY"], "https://kaggle.com", "Varies.")
IMD = DownloaderConfig("imd", [], "https://imdpune.gov.in", "Restricted research use. (imdlib)")
COPERNICUS_DEM = DownloaderConfig("copernicus_dem", [], "s3://copernicus-dem-30m/", "Public Domain (AWS)")

class IMDRainfallDownloader(Downloader):
    def __init__(self, data_dir: str = "data/raw"):
        super().__init__(IMD, data_dir)
        
    def download(self, year: int, dry_run: bool = False) -> str:
        if dry_run: return "success_dry_run"
        try:
            import imdlib as imd
            import time
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"[{self.config.name}] Downloading IMD rainfall data for {year}...")
            
            # imdlib downloads internally, add retries with backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    imd.get_data("rain", year, year, fn_format="yearwise", file_dir=self.output_dir)
                    break
                except Exception as e:
                    print(f"[{self.config.name}] Attempt {attempt + 1} failed for {year}: {e}")
                    if attempt < max_retries - 1:
                        backoff_time = (2 ** attempt) * 10  # 10s, 20s
                        print(f"[{self.config.name}] Waiting {backoff_time} seconds before retry...")
                        time.sleep(backoff_time)
                    else:
                        raise e
            
            # Write a manifest
            file_path = os.path.join(self.output_dir, f"rain_{year}.grd")
            manifest_path = file_path + ".manifest.json"
            manifest_data = {
                "source": self.config.name,
                "url": f"https://imdpune.gov.in/rain_{year}",
                "downloaded_at": datetime.now().isoformat(),
                "size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            with open(manifest_path, "w") as mf:
                json.dump(manifest_data, mf)
                
            return "success"
        except Exception as e:
            print(f"[{self.config.name}] Error: {e}")
            return "error"

def compute_dem_stats(elev: np.ndarray) -> dict:
    import numpy as np
    elev = elev.astype(float)
    elev[elev < -1000] = np.nan
    if np.isnan(elev).all():
        return {"elev_mean_m": np.nan, "elev_max_m": np.nan, "relief_m": np.nan, "slope_mean_deg": np.nan}
    
    elev_mean = np.nanmean(elev)
    elev_max = np.nanmax(elev)
    relief = elev_max - np.nanmin(elev)
    
    dy, dx = np.gradient(elev, 30, 30)
    slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
    slope_mean = np.nanmean(slope)
    
    return {
        "elev_mean_m": float(elev_mean),
        "elev_max_m": float(elev_max),
        "relief_m": float(relief),
        "slope_mean_deg": float(slope_mean)
    }

def get_copernicus_dem_features(bbox: List[float]) -> Dict[str, float]:
    """
    Computes DEM stats (elev_mean_m, elev_max_m, relief_m, slope_mean_deg) for a given bbox [min_lon, min_lat, max_lon, max_lat].
    """
    try:
        import rasterio
        from rasterio.session import AWSSession
        import boto3
        import numpy as np
    except ImportError:
        return {"elev_mean_m": float('nan'), "elev_max_m": float('nan'), "relief_m": float('nan'), "slope_mean_deg": float('nan')}
        
    min_lon, min_lat, max_lon, max_lat = bbox
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    
    lat_int = int(np.floor(center_lat))
    lon_int = int(np.floor(center_lon))
    
    ns = f"N{lat_int:02d}" if lat_int >= 0 else f"S{-lat_int:02d}"
    ew = f"E{lon_int:03d}" if lon_int >= 0 else f"W{-lon_int:03d}"
    
    s3_url = f"s3://copernicus-dem-30m/Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM/Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM.tif"
    
    session = boto3.Session()
    aws_session = AWSSession(session, requester_pays=False)
    
    try:
        with rasterio.Env(aws_session, AWS_NO_SIGN_REQUEST='YES'):
            with rasterio.open(s3_url) as src:
                window = rasterio.windows.from_bounds(min_lon, min_lat, max_lon, max_lat, transform=src.transform)
                elev = src.read(1, window=window)
                return compute_dem_stats(elev)
    except Exception as e:
        print(f"[COPERNICUS_DEM] Failed to read from {s3_url}: {e}")
        return {"elev_mean_m": np.nan, "elev_max_m": np.nan, "relief_m": np.nan, "slope_mean_deg": np.nan}

if __name__ == "__main__":
    d = Downloader(MOSDAC)
    d.download("test.nc", "https://mosdac.gov.in/test.nc", dry_run=True)

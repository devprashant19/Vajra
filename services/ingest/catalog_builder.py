import os
import glob
import json
import pandas as pd
from datetime import datetime

class CatalogBuilder:
    def __init__(self, raw_dir: str = "data/raw", catalog_path: str = "data/catalog/catalog.parquet"):
        self.raw_dir = raw_dir
        self.catalog_path = catalog_path
        
    def build(self):
        records = []
        # Find all manifests
        manifests = glob.glob(os.path.join(self.raw_dir, "**/*.manifest.json"), recursive=True)
        
        for mf_path in manifests:
            with open(mf_path, "r") as f:
                data = json.load(f)
                
            # Parse directory structure to infer details (e.g. data/raw/mosdac/2024/05/10/file.nc.manifest.json)
            parts = mf_path.replace("\\", "/").split("/")
            if len(parts) >= 3:
                source = parts[2]
            else:
                source = data.get("source", "unknown")
                
            verdict = data.get("verdict", "REAL")
            
            licence = data.get("licence", "UNKNOWN")
            if source == "imd": licence = "Restricted research use. (imdlib)"
            elif source == "copernicus_dem": licence = "Public Domain (AWS)"
            
            records.append({
                "source": source,
                "product": data.get("product", "unknown"),
                "valid_time_start": data.get("valid_time_start", datetime.now().isoformat()),
                "valid_time_end": data.get("valid_time_end", datetime.now().isoformat()),
                "bbox": data.get("bbox", "[-180, -90, 180, 90]"), # EPSG:4326 bbox
                "grid_crs_extent": data.get("grid_crs_extent", "UNKNOWN"), # EPSG:7755 extent
                "sha256": data.get("sha256", ""),
                "size_bytes": data.get("size_bytes", 0),
                "status": data.get("status", "needs_credentials"),
                "licence": data.get("licence", "UNKNOWN"),
                "verdict": verdict
            })
            
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=[
                "source", "product", "valid_time_start", "valid_time_end", 
                "bbox", "grid_crs_extent", "sha256", "size_bytes", "status", "licence", "verdict"
            ])
            
        os.makedirs(os.path.dirname(self.catalog_path), exist_ok=True)
        df.to_parquet(self.catalog_path, engine="pyarrow")
        print(f"Built catalog with {len(df)} rows at {self.catalog_path}")

if __name__ == "__main__":
    builder = CatalogBuilder()
    builder.build()

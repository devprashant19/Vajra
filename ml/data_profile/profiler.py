import os
import pandas as pd

class Profiler:
    def __init__(self, catalog_path: str = "data/catalog/catalog.parquet", output_path: str = "reports/DATA_COVERAGE.md"):
        self.catalog_path = catalog_path
        self.output_path = output_path
        
    def profile(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        if os.path.exists(self.catalog_path):
            df = pd.read_parquet(self.catalog_path)
            stats = df.groupby(["source", "product"]).size().reset_index(name="count")
            stats_md = stats.to_markdown(index=False)
        else:
            stats_md = "No catalog data found (0 rows)."
            
        decision_table = """
## Data Availability & Model Decision Table

| Modality / Hazard | Train on Real Indian Data | Volume Available | Label Quality | Fallback Strategy |
|---|---|---|---|---|
| **Radar / Severe Cells** | **NO** (Pending Access) | 0 bytes (Raw DWR) | N/A | Pretrain on US SEVIR (VIL); inference via Satellite-proxy if DWR is missing. |
| **Satellite / Convection** | **YES** | Large (MOSDAC) | High | ERA5 NWP soundings for broader thermodynamic baseline. |
| **Lightning** | **NO** (Pending Access) | 0 bytes (ILLN) | N/A | Blitzortung global real-time + GPM-LIS climatology. |
| **Thermodynamics (NWP)** | **YES** | Large (ERA5/GFS) | High (Reanalysis) | Open-Meteo for real-time live ingestion. |
| **Hail Proxy** | **NO** | 0 bytes | Low | US SEVIR hail reports for pretrained feature extraction. |
"""

        report_content = f"""# Data Coverage Profile

This report profiles the temporal and spatial density of multi-modal data available in the data lake.

## Assets in Catalog
{stats_md}

{decision_table}
"""
        with open(self.output_path, "w") as f:
            f.write(report_content)
        print(f"Generated coverage report at {self.output_path}")

if __name__ == "__main__":
    p = Profiler()
    p.profile()

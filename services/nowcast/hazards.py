import numpy as np
from typing import Dict, Any, List

class RuleBasedHazards:
    def __init__(self, dx_km: float = 2.0):
        self.dx_km = dx_km
        self.area_px_to_km2 = dx_km ** 2

    def evaluate_cell(self, cell: Dict[str, Any], history: List[Dict[str, Any]], env: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate hazards for a single tracked cell based on rule-based heuristics.
        """
        hazards = {}
        severity = "Green"
        
        # Convective Initiation
        btd = env.get("ir", 280) - env.get("wv", 260) # proxy
        cooling_rate = 0.0
        if len(history) > 1:
            cooling_rate = history[-2].get("ir", 280) - cell.get("ir", 280)
            
        if btd > -2 and cooling_rate > 2.5 and env.get("cape", 0) > 1000 and env.get("cin", -100) > -50:
            hazards["convective_initiation"] = True
            severity = "Yellow"

        # Lightning Jump
        flash_rates = [h.get("flash_rate", 0) for h in history[-3:]] if history else []
        current_flash = cell.get("flash_rate", 0)
        if len(flash_rates) >= 3:
            mean_f = np.mean(flash_rates)
            std_f = np.std(flash_rates)
            if current_flash > 5 and current_flash > mean_f + 2 * std_f:
                hazards["lightning_jump"] = True
                severity = max_severity(severity, "Orange")

        # Hail
        vil = cell.get("max_vil", 0)
        echo_top = cell.get("echo_top_km", 8.0)
        if echo_top > 0:
            vil_density = vil / echo_top
            if vil_density > 3.5 or (vil > 40 and echo_top > 8.0):
                hazards["hail"] = True
                severity = max_severity(severity, "Red")

        # Downburst
        dcape = env.get("dcape", 0)
        if dcape > 800 and cell.get("max_dbz", 0) > 50 and cell.get("trend") == "decaying":
            hazards["downburst"] = True
            severity = max_severity(severity, "Red")

        # Cloudburst (IMD definition: > 100 mm/h over 20-30 sq km)
        rain_rate = cell.get("max_rain_rate", cell.get("max_dbz", 0) * 1.5) # Proxy if not given
        area_km2 = cell.get("area_km2", 0)
        if rain_rate >= 100.0 and area_km2 >= 20.0:
            hazards["cloudburst"] = True
            severity = max_severity(severity, "Red")
            
        if "cloudburst" not in hazards and rain_rate >= 60.0:
            severity = max_severity(severity, "Orange")

        return {
            "hazards": hazards,
            "severity": severity,
            "method": "rule_based",
            "label_quality": "proxy"
        }

def max_severity(s1: str, s2: str) -> str:
    levels = {"Green": 0, "Yellow": 1, "Orange": 2, "Red": 3}
    return s1 if levels[s1] >= levels[s2] else s2

import numpy as np
import cv2
from typing import List, Dict, Any, Optional

class BaselineEngines:
    def __init__(self, nx: int = 256, ny: int = 256):
        self.nx = nx
        self.ny = ny
        self.dt_min = 10
        self.max_lead = 120

    def persistence(self, current_frame: Dict[str, Any]) -> List[Dict[str, Any]]:
        forecasts = []
        for lead_min in range(self.dt_min, self.max_lead + self.dt_min, self.dt_min):
            forecasts.append({
                "lead_min": lead_min,
                "dbz": current_frame["dbz"].copy(),
                "vil": current_frame["vil"].copy(),
                "rain_rate": current_frame["rain_rate"].copy(),
                "flash": current_frame["flash"].copy(),
                "engine": "persistence",
                "skilful": "unknown"
            })
        return forecasts

    def _normalize_contrast(self, image: np.ndarray) -> np.ndarray:
        if image.max() == image.min():
            return np.zeros_like(image, dtype=np.uint8)
        norm = (image - image.min()) / (image.max() - image.min())
        return (norm * 255).astype(np.uint8)

    def optical_flow_farneback(self, prev_dbz: np.ndarray, curr_dbz: np.ndarray) -> List[Dict[str, Any]]:
        # Contrast normalization
        prev_norm = self._normalize_contrast(prev_dbz)
        curr_norm = self._normalize_contrast(curr_dbz)
        
        # Calculate flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_norm, curr_norm, None,
            pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        
        forecasts = []
        curr_state = {
            "dbz": curr_dbz.copy()
        }
        
        h, w = self.ny, self.nx
        y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)
        
        for lead_min in range(self.dt_min, self.max_lead + self.dt_min, self.dt_min):
            steps = lead_min // self.dt_min
            
            # Advect
            map_x = np.clip(x_coords - flow[..., 0] * steps, 0, w - 1).astype(np.float32)
            map_y = np.clip(y_coords - flow[..., 1] * steps, 0, h - 1).astype(np.float32)
            
            adv_dbz = cv2.remap(curr_dbz, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            
            forecasts.append({
                "lead_min": lead_min,
                "dbz": adv_dbz,
                "engine": "optical_flow",
                "skilful": "unknown"
            })
            
        return forecasts

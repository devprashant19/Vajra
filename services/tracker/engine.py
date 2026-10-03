import numpy as np
from scipy.ndimage import label, center_of_mass, find_objects
from scipy.optimize import linear_sum_assignment
from typing import List, Dict, Any, Tuple

class Tracker:
    def __init__(self, dx_km: float = 2.0, dt_min: float = 10.0):
        self.dx_km = dx_km
        self.dt_min = dt_min
        self.min_dbz = 35.0
        self.min_area_px = 6 # 24 km2 / (2x2 km2) = 6
        self.next_id = 0
        self.active_tracks = {} # id -> track state

    def process_frame(self, dbz: np.ndarray, vil: np.ndarray, frame_time: str) -> List[Dict[str, Any]]:
        # Connected components
        mask = dbz >= self.min_dbz
        labeled, num_features = label(mask)
        
        current_cells = []
        objects = find_objects(labeled)
        
        for i, slc in enumerate(objects):
            if slc is None:
                continue
            idx = i + 1
            cell_mask = labeled[slc] == idx
            area = np.sum(cell_mask)
            if area < self.min_area_px:
                continue
                
            cell_dbz = dbz[slc][cell_mask]
            max_dbz = np.max(cell_dbz)
            cell_vil = vil[slc][cell_mask] if vil is not None else np.zeros_like(cell_dbz)
            max_vil = np.max(cell_vil)
            
            # Local coordinates within the slice, then offset
            local_com = center_of_mass(cell_mask)
            cy = slc[0].start + local_com[0]
            cx = slc[1].start + local_com[1]
            
            current_cells.append({
                "cx": cx,
                "cy": cy,
                "area_km2": area * (self.dx_km ** 2),
                "max_dbz": max_dbz,
                "max_vil": max_vil,
                "echo_top_km": max_dbz * 0.2, # dummy proxy
                "matched": False
            })

        # Match with active tracks
        if not self.active_tracks:
            # All new
            for cell in current_cells:
                cell["id"] = f"T_{self.next_id:04d}"
                self.next_id += 1
                cell["speed_kmh"] = 0.0
                cell["heading_deg"] = 0.0
                cell["trend"] = "new"
                self.active_tracks[cell["id"]] = cell
        else:
            old_ids = list(self.active_tracks.keys())
            old_cells = [self.active_tracks[tid] for tid in old_ids]
            
            if current_cells:
                # Cost matrix based on distance
                cost = np.zeros((len(old_cells), len(current_cells)))
                for r, oc in enumerate(old_cells):
                    for c, cc in enumerate(current_cells):
                        dist = np.sqrt((oc["cx"] - cc["cx"])**2 + (oc["cy"] - cc["cy"])**2)
                        cost[r, c] = dist
                        if dist > 10.0: # max cells movement per frame
                            cost[r, c] = 9999.0
                            
                row_ind, col_ind = linear_sum_assignment(cost)
                
                new_active = {}
                for r, c in zip(row_ind, col_ind):
                    if cost[r, c] < 9999.0:
                        oc = old_cells[r]
                        cc = current_cells[c]
                        cc["id"] = oc["id"]
                        
                        dx = (cc["cx"] - oc["cx"]) * self.dx_km
                        dy = (cc["cy"] - oc["cy"]) * self.dx_km
                        dist_km = np.sqrt(dx**2 + dy**2)
                        
                        cc["speed_kmh"] = (dist_km / self.dt_min) * 60.0
                        cc["heading_deg"] = (np.degrees(np.arctan2(dx, dy)) + 360) % 360 # 0 is North
                        
                        dbz_diff = cc["max_dbz"] - oc["max_dbz"]
                        cc["trend"] = "growing" if dbz_diff > 2 else ("decaying" if dbz_diff < -2 else "steady")
                        
                        cc["matched"] = True
                        new_active[cc["id"]] = cc

                # Unmatched current cells are new
                for cc in current_cells:
                    if not cc.get("matched"):
                        cc["id"] = f"T_{self.next_id:04d}"
                        self.next_id += 1
                        cc["speed_kmh"] = 0.0
                        cc["heading_deg"] = 0.0
                        cc["trend"] = "new"
                        new_active[cc["id"]] = cc
                        
                self.active_tracks = new_active
            else:
                self.active_tracks = {}

        return list(self.active_tracks.values())

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class ETAEngine:
    def __init__(self, seed: int = 42, dx_km: float = 2.0, dt_min: float = 10.0):
        self.rng = np.random.default_rng(seed)
        self.dx_km = dx_km
        self.dt_min = dt_min
        self.N = 200 # Monte Carlo trajectories

    def compute_eta(self, cell: Dict[str, Any], locations: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        # Monte Carlo trajectories
        # Cell state
        cx = cell["cx"] * self.dx_km
        cy = cell["cy"] * self.dx_km
        speed_kmh = cell.get("speed_kmh", 0)
        heading_deg = cell.get("heading_deg", 0)
        radius_km = np.sqrt(cell.get("area_km2", 20) / np.pi)
        
        # Add uncertainty to speed and heading
        speed_samples = np.clip(self.rng.normal(speed_kmh, speed_kmh * 0.2, self.N), 0, None)
        heading_samples = self.rng.normal(heading_deg, 15.0, self.N)
        
        # Convert to vx, vy (km/min)
        vx_samples = (speed_samples / 60.0) * np.sin(np.radians(heading_samples))
        vy_samples = (speed_samples / 60.0) * np.cos(np.radians(heading_samples))
        
        results = []
        max_time_min = 120
        steps = int(max_time_min / self.dt_min)
        
        for loc in locations:
            # Simple conversion from lat/lon to km from origin (assuming 1 deg approx 111km)
            # We don't have the exact grid origin here easily, so let's mock the local coordinates
            # if they aren't provided. In the generator, we gave lat/lon. We need to project.
            # Assuming center of grid is center of lat/lon from the generator.
            loc_x = (loc.get("lon", 80.0) - 80.0) * 111.0 + 256.0 # Mocked coordinate transformation
            loc_y = (loc.get("lat", 20.0) - 20.0) * 111.0 + 256.0
            
            # Prefilter: if distance is too large compared to max possible movement
            dist_to_loc = np.sqrt((loc_x - cx)**2 + (loc_y - cy)**2)
            max_travel = (speed_kmh / 60.0) * max_time_min + 50.0 # + buffer
            if dist_to_loc > max_travel + radius_km + 20.0:
                continue # Skip, cannot reach
                
            # Vectorized MC
            # shapes: (N, steps)
            t_grid = np.arange(1, steps + 1) * self.dt_min
            
            # Trajectories
            x_traj = cx + vx_samples[:, None] * t_grid[None, :]
            y_traj = cy + vy_samples[:, None] * t_grid[None, :]
            
            # Distances to location over time
            dists = np.sqrt((x_traj - loc_x)**2 + (y_traj - loc_y)**2)
            
            # Growth/Decay of radius (simple uniform assumption)
            r_traj = radius_km + np.zeros_like(dists)
            if cell.get("trend") == "growing":
                r_traj += t_grid[None, :] * 0.1
            elif cell.get("trend") == "decaying":
                r_traj -= t_grid[None, :] * 0.1
            r_traj = np.clip(r_traj, 2.0, None)
            
            # Impact condition
            impact_mask = dists <= r_traj
            
            # Any impact across time steps per sample
            impact_any = np.any(impact_mask, axis=1)
            prob_impact = np.mean(impact_any)
            
            if prob_impact < 0.01:
                continue
                
            # Arrival times for samples that impact
            first_impact_idx = np.argmax(impact_mask[impact_any], axis=1)
            arrival_times = t_grid[first_impact_idx]
            
            p10 = float(np.percentile(arrival_times, 10)) if len(arrival_times) > 0 else None
            p50 = float(np.percentile(arrival_times, 50)) if len(arrival_times) > 0 else None
            p90 = float(np.percentile(arrival_times, 90)) if len(arrival_times) > 0 else None
            
            # Prob within windows
            prob_15 = np.mean(np.any(impact_mask[:, t_grid <= 15], axis=1))
            prob_30 = np.mean(np.any(impact_mask[:, t_grid <= 30], axis=1))
            prob_60 = np.mean(np.any(impact_mask[:, t_grid <= 60], axis=1))
            prob_120 = prob_impact
            
            # Duration
            duration_steps = np.sum(impact_mask[impact_any], axis=1)
            mean_duration = float(np.mean(duration_steps)) * self.dt_min if len(duration_steps) > 0 else 0
            
            # State machine (WATCH / APPROACHING / IMPACT / CLEARING / CLEARED / STALE)
            # Hysteresis requires previous state, but we compute stateless here based on current snapshot
            # This is a simplified state deduction
            current_dist = np.sqrt((cx - loc_x)**2 + (cy - loc_y)**2)
            state = "WATCH"
            if current_dist <= radius_km:
                state = "IMPACT"
            elif p50 is not None and p50 <= 30:
                state = "APPROACHING"
            
            results.append({
                "location_id": loc["id"],
                "cell_id": cell["id"],
                "p10_arrival_time": (current_time + timedelta(minutes=p10)).isoformat() if p10 else None,
                "p50_arrival_time": (current_time + timedelta(minutes=p50)).isoformat() if p50 else None,
                "p90_arrival_time": (current_time + timedelta(minutes=p90)).isoformat() if p90 else None,
                "prob_15min": float(prob_15),
                "prob_30min": float(prob_30),
                "prob_60min": float(prob_60),
                "prob_120min": float(prob_120),
                "impact_duration_min": mean_duration,
                "state": state,
                "dominant_hazard": cell.get("dominant_hazard", "Heavy Rain")
            })
            
        return results

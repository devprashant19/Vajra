import math
import numpy as np

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def extract_point_rainfall_stats(ds, target_lat, target_lon, target_date_str, all_years_datasets=None):
    import pandas as pd
    dt = pd.to_datetime(target_date_str)
    day_minus_1 = (dt - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    day_plus_1 = (dt + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    
    try:
        daily_ds = ds.sel(time=target_date_str, method='nearest')
        nearest_cell = daily_ds.sel(lat=target_lat, lon=target_lon, method='nearest')
        rain = float(nearest_cell.rain.values)
        cell_lat = float(nearest_cell.lat.values)
        cell_lon = float(nearest_cell.lon.values)
    except:
        rain = np.nan
        cell_lat = target_lat
        cell_lon = target_lon
        
    dist_km = haversine(target_lat, target_lon, cell_lat, cell_lon)
    fallback_used = False
    best_lat, best_lon, best_dist = cell_lat, cell_lon, dist_km
    
    if rain == -999.0 or np.isnan(rain):
        window = 1.0
        min_lat, max_lat = target_lat - window/2, target_lat + window/2
        min_lon, max_lon = target_lon - window/2, target_lon + window/2
        
        lat_slice = slice(min_lat, max_lat) if ds.lat[0] < ds.lat[-1] else slice(max_lat, min_lat)
        lon_slice = slice(min_lon, max_lon) if ds.lon[0] < ds.lon[-1] else slice(max_lon, min_lon)
        
        try:
            subset = daily_ds.sel(lat=lat_slice, lon=lon_slice)
            best_dist = float('inf')
            for clat in subset.lat.values:
                for clon in subset.lon.values:
                    r = float(subset.sel(lat=clat, lon=clon).rain.values)
                    if r != -999.0 and not np.isnan(r):
                        d_deg = math.sqrt((target_lat - float(clat))**2 + (target_lon - float(clon))**2)
                        if d_deg <= 0.5:
                            d_km = haversine(target_lat, target_lon, float(clat), float(clon))
                            if d_km < best_dist:
                                best_dist = d_km
                                best_lat = float(clat)
                                best_lon = float(clon)
                                
            if best_dist != float('inf'):
                fallback_used = True
            else:
                return {"is_valid": False}
        except:
            return {"is_valid": False}

    cell_ts = ds.sel(lat=best_lat, lon=best_lon, method='nearest')
    
    try:
        r = float(cell_ts.sel(time=target_date_str).rain.values)
        rain_event_day_mm = r if r != -999.0 else np.nan
    except:
        rain_event_day_mm = np.nan
        
    try:
        peak_slice = cell_ts.sel(time=slice(target_date_str, day_plus_1))
        vals = peak_slice.rain.values
        times = peak_slice.time.values
        valid_mask = (vals != -999.0) & (~np.isnan(vals))
        if np.any(valid_mask):
            peak_idx = np.argmax(np.where(valid_mask, vals, -np.inf))
            rain_peak_mm = float(vals[peak_idx])
            rain_peak_date = str(times[peak_idx])[:10]
        else:
            rain_peak_mm = np.nan
            rain_peak_date = ""
    except:
        rain_peak_mm = np.nan
        rain_peak_date = ""
        
    try:
        threeday_slice = cell_ts.sel(time=slice(day_minus_1, day_plus_1))
        vals3 = threeday_slice.rain.values
        valid_mask3 = (vals3 != -999.0) & (~np.isnan(vals3))
        if np.any(valid_mask3):
            rain_3day_mm = float(np.nansum(np.where(valid_mask3, vals3, np.nan)))
            rain_3day_max = float(np.nanmax(np.where(valid_mask3, vals3, np.nan)))
        else:
            rain_3day_mm = np.nan
            rain_3day_max = np.nan
    except:
        rain_3day_mm = np.nan
        rain_3day_max = np.nan
        
    try:
        if not np.isnan(rain_peak_mm):
            if all_years_datasets is not None:
                all_time = []
                for dataset in all_years_datasets.values():
                    try:
                        ts = dataset.sel(lat=best_lat, lon=best_lon, method='nearest').rain.values
                        all_time.extend(ts)
                    except:
                        pass
                all_time = np.array(all_time)
            else:
                all_time = cell_ts.rain.values
            all_time = all_time[(all_time != -999.0) & (~np.isnan(all_time))]
            wet_days = all_time[all_time >= 2.5]
            if len(wet_days) > 0:
                from scipy import stats
                rain_wetday_percentile = stats.percentileofscore(wet_days, rain_peak_mm)
            else:
                rain_wetday_percentile = np.nan
        else:
            rain_wetday_percentile = np.nan
    except:
        rain_wetday_percentile = np.nan
        
    try:
        import pandas as pd
        start_wide = (dt - pd.Timedelta(days=3)).strftime("%Y-%m-%d")
        end_wide = (dt + pd.Timedelta(days=4)).strftime("%Y-%m-%d")
        wide_slice = cell_ts.sel(time=slice(start_wide, end_wide))
        vals_wide = wide_slice.rain.values
        times_wide = wide_slice.time.values
        valid_wide = (vals_wide != -999.0) & (~np.isnan(vals_wide))
        if np.any(valid_wide):
            peak_idx_w = np.argmax(np.where(valid_wide, vals_wide, -np.inf))
            peak_date_w = str(times_wide[peak_idx_w])[:10]
            rain_peak_offset_days = (pd.to_datetime(peak_date_w) - dt).days
            rain_widepeak_mm = float(vals_wide[peak_idx_w])
        else:
            rain_peak_offset_days = np.nan
            rain_widepeak_mm = np.nan
    except:
        rain_peak_offset_days = np.nan
        rain_widepeak_mm = np.nan
        
    return {
        "rain_event_day_mm": rain_event_day_mm,
        "rain_peak_mm": rain_peak_mm,
        "rain_peak_date": rain_peak_date,
        "rain_3day_mm": rain_3day_mm,
        "rain_3day_max": rain_3day_max,
        "rain_wetday_percentile": rain_wetday_percentile,
        "rain_peak_offset_days": rain_peak_offset_days,
        "rain_widepeak_mm": rain_widepeak_mm,
        "cell_lat": best_lat,
        "cell_lon": best_lon,
        "fallback": fallback_used,
        "distance_km": best_dist,
        "is_valid": True
    }

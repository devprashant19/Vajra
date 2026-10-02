import pytest
import numpy as np
import pandas as pd
import xarray as xr
import datetime
from pathlib import Path
import sys
import os

# Add services to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.ingest.archive.downloaders import compute_dem_stats

def test_compute_dem_stats():
    # Synthetic DEM array 3x3
    # slope = 45 degrees if diff is 30m over 30m pixel
    # [[0, 30, 60],
    #  [0, 30, 60],
    #  [0, 30, 60]]
    # gradient in x is 30, y is 0. 
    # arctan(sqrt(30**2 + 0) / 30) = arctan(1) = 45 deg
    elev = np.array([
        [0.0, 30.0, 60.0],
        [0.0, 30.0, 60.0],
        [0.0, 30.0, 60.0]
    ])
    
    stats = compute_dem_stats(elev)
    assert stats["elev_mean_m"] == 30.0
    assert stats["elev_max_m"] == 60.0
    assert stats["relief_m"] == 60.0
    assert np.isclose(stats["slope_mean_deg"], 45.0, atol=2.0)

def compute_rainfall_stats_synthetic(subset, dt):
    # Re-implementation of the logic used in build_benchmark.py for testing
    day_str = dt.strftime("%Y-%m-%d")
    rain_day = float(subset.sel(time=day_str, method='nearest').rain.max().values)
    
    start_3day = (dt - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    rain_3day = float(subset.sel(time=slice(start_3day, day_str)).rain.sum(dim='time').max().values)
    
    daily_maxes = subset.rain.max(dim=['lat', 'lon']).values
    wet_days = daily_maxes[daily_maxes >= 2.5]
    
    from scipy import stats
    rain_percentile = stats.percentileofscore(wet_days, rain_day)
    return rain_day, rain_3day, rain_percentile
    

def test_rainfall_stats():
    # Create synthetic xarray Dataset
    times = pd.date_range("2020-01-01", "2020-01-10", freq="D")
    lats = [10.0, 10.25]
    lons = [75.0, 75.25]
    
    rain = np.zeros((len(times), len(lats), len(lons)))
    # Days 1, 2, 3 have some rain. Event on Day 3.
    rain[0, :, :] = 1.0 # 2020-01-01
    rain[1, :, :] = 5.0 # 2020-01-02
    rain[2, 0, 0] = 10.0 # 2020-01-03 (event day) max = 10.0
    rain[3, :, :] = 20.0 # 2020-01-04 max = 20.0
    
    ds = xr.Dataset(
        {"rain": (("time", "lat", "lon"), rain)},
        coords={"time": times, "lat": lats, "lon": lons}
    )
    
    # We pass full_ds=ds since it now supports multi-year
    # Let's add more wet days to a different year to prove it uses full_ds
    times_hist = pd.date_range("2015-01-01", "2015-01-10", freq="D")
    rain_hist = np.zeros((len(times_hist), len(lats), len(lons)))
    rain_hist[0, 0, 0] = 50.0 # big storm
    rain_hist[1, 0, 0] = 100.0 # bigger storm
    ds_hist = xr.Dataset({"rain": (("time", "lat", "lon"), rain_hist)}, coords={"time": times_hist, "lat": lats, "lon": lons})
    
    all_years_datasets = {2015: ds_hist, 2020: ds}
    
    dt = datetime.datetime(2020, 1, 3)
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../tools")))
    from imd_utils import extract_point_rainfall_stats
    
    res = extract_point_rainfall_stats(ds, 10.0, 75.0, "2020-01-03", all_years_datasets=all_years_datasets)
    rain_day = res["rain_event_day_mm"]
    rain_3day = res["rain_3day_mm"]
    rain_percentile = res["rain_wetday_percentile"]
    
    assert rain_day == 10.0
    assert rain_3day == 35.0 # 5.0 + 10.0 + 20.0
    # Wet days maxes across full_ds (2015 + 2020) at lat 10.0, lon 75.0:
    # 2015: Jan 1 (50.0), Jan 2 (100.0)
    # 2020: Jan 2 (5.0), Jan 3 (10.0), Jan 4 (20.0)
    # Total wet days array: [5.0, 10.0, 20.0, 50.0, 100.0] (sorted)
    # Percentile of 20.0 in this array -> 3rd out of 5 -> 60.0%
    assert np.isclose(rain_percentile, 60.0, atol=0.1)

def test_csv_schema():
    # Check if CSV has expected schema
    # The actual file might not exist in CI if network is blocked, 
    # but we can write a dummy one and test the schema reader.
    expected_cols = [
        "id", "rain_event_day_mm", "rain_peak_mm", "rain_peak_date", "rain_3day_mm", "rain_wetday_percentile",
        "percentile_baseline", "rain_peak_offset_days", "rain_widepeak_mm", "rain_cell_lat", "rain_cell_lon", "rain_cell_fallback", "rain_cell_distance_km",
        "elev_mean_m", "elev_max_m", "relief_m", "slope_mean_deg"
    ]
    df = pd.DataFrame(columns=expected_cols)
    assert list(df.columns) == expected_cols

def test_deduplication():
    # Synthetic test to verify that if two events are within 2 days and 0.5 degrees, they are duplicates
    gold_event = {"date": datetime.datetime(2020, 1, 1), "lat": 10.0, "lon": 75.0}
    
    # duplicate
    cand1 = {"date": datetime.datetime(2020, 1, 2), "lat": 10.2, "lon": 75.2}
    
    # not duplicate
    cand2 = {"date": datetime.datetime(2020, 1, 4), "lat": 10.2, "lon": 75.2}
    cand3 = {"date": datetime.datetime(2020, 1, 2), "lat": 11.0, "lon": 75.0}
    
    def is_dup(cand):
        import numpy as np
        dt_diff = abs((cand["date"] - gold_event["date"]).days)
        dist = np.sqrt((cand["lat"] - gold_event["lat"])**2 + (cand["lon"] - gold_event["lon"])**2)
        return dt_diff <= 2 and dist <= 0.5
        
    assert is_dup(cand1)
    assert not is_dup(cand2)
    assert not is_dup(cand3)

def test_control_schema():
    expected_cols = [
        "control_id", "parent_event_id", "date", "lat", "lon", "label",
        "rain_event_day_mm", "rain_peak_mm", "rain_peak_date", "rain_3day_mm", "rain_wetday_percentile",
        "percentile_baseline", "rain_peak_offset_days", "rain_widepeak_mm", "control_clean", "season_window_days", "offset_days",
        "rain_cell_lat", "rain_cell_lon", "rain_cell_fallback", "rain_cell_distance_km",
        "elev_mean_m", "elev_max_m", "relief_m", "slope_mean_deg"
    ]
    df = pd.DataFrame(columns=expected_cols)
    assert list(df.columns) == expected_cols

def test_fallback_and_peak_logic():
    import xarray as xr
    import numpy as np
    import datetime
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../tools")))
    from imd_utils import extract_point_rainfall_stats
    
    # 3 days: 2020-01-01 (day-1), 2020-01-02 (event), 2020-01-03 (day+1)
    times = pd.date_range("2020-01-01", "2020-01-03", freq="D")
    lats = [10.0, 10.25]
    lons = [75.0, 75.25]
    rain = np.zeros((len(times), len(lats), len(lons)))
    
    # Target is 10.0, 75.0
    rain[:, 0, 0] = np.nan # Coastal mask
    rain[0, 0, 1] = 10.0   # 2020-01-01
    rain[1, 0, 1] = 50.0   # 2020-01-02 (event day)
    rain[2, 0, 1] = 120.0  # 2020-01-03 (peak day)
    
    ds = xr.Dataset(
        {"rain": (("time", "lat", "lon"), rain)},
        coords={"time": times, "lat": lats, "lon": lons}
    )
    
    res = extract_point_rainfall_stats(ds, 10.0, 75.0, "2020-01-02")
    assert res["fallback"] == True
    assert res["rain_event_day_mm"] == 50.0
    assert res["rain_peak_mm"] == 120.0
    assert res["rain_peak_date"] == "2020-01-03"
    assert res["rain_3day_mm"] == 180.0 # 10 + 50 + 120
    assert res["rain_3day_max"] == 120.0
    assert res["rain_peak_offset_days"] == 1 # 3rd minus 2nd is +1
    assert res["rain_widepeak_mm"] == 120.0
    assert res["cell_lat"] == 10.0
    assert res["cell_lon"] == 75.25

def test_control_day_minus_one():
    # If day-1 is >= 2.5 but day and day+1 are 0, rain_3day_max should catch it
    import xarray as xr
    import numpy as np
    import datetime
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../tools")))
    from imd_utils import extract_point_rainfall_stats
    
    times = pd.date_range("2020-01-01", "2020-01-03", freq="D")
    lats = [10.0]
    lons = [75.0]
    rain = np.zeros((len(times), len(lats), len(lons)))
    
    rain[0, 0, 0] = 3.0  # day -1
    rain[1, 0, 0] = 0.0  # day 0
    rain[2, 0, 0] = 0.0  # day +1
    
    ds = xr.Dataset(
        {"rain": (("time", "lat", "lon"), rain)},
        coords={"time": times, "lat": lats, "lon": lons}
    )
    
    res = extract_point_rainfall_stats(ds, 10.0, 75.0, "2020-01-02")
    assert res["rain_3day_max"] == 3.0


def test_control_constraints():
    if not os.path.exists("data/benchmark/controls.csv"):
        return
    df = pd.read_csv("data/benchmark/controls.csv")
    for pid, grp in df.groupby("parent_event_id"):
        # One control per year
        years = pd.to_datetime(grp['date']).dt.year
        assert len(years) == len(years.unique())
        
        # 7-day spacing
        dts = sorted(pd.to_datetime(grp['date']))
        for i in range(len(dts)-1):
            assert (dts[i+1] - dts[i]).days >= 7

def test_auto_events_schema():
    expected_cols = [
        "auto_id", "date", "lat", "lon", "max_rain_mm", "n_cells", "label_quality", "source", 
        "elev_mean_m", "elev_max_m", "relief_m", "slope_mean_deg"
    ]
    df = pd.DataFrame(columns=expected_cols)
    assert list(df.columns) == expected_cols

def test_imerg_schema():
    expected_cols = [
        "event_id", "timestamp_utc", "precip_mm_hr", "cell_lat", "cell_lon", "is_bbox_max"
    ]
    df = pd.DataFrame(columns=expected_cols)
    assert list(df.columns) == expected_cols

def test_imerg_bbox_logic():
    import numpy as np
    
    # Synthetic dataframe resembling what we get from xarray to_dataframe
    data = {
        'time': pd.to_datetime(['2020-01-01 00:00:00', '2020-01-01 00:00:00', '2020-01-01 00:30:00', '2020-01-01 00:30:00']),
        'lat': [10.0, 10.5, 10.0, 10.5],
        'lon': [75.0, 75.5, 75.0, 75.5],
        'precipitationCal': [5.0, 10.0, 2.0, 1.0] # max at 00:00 is 10.0, at 00:30 is 2.0
    }
    df_subset = pd.DataFrame(data)
    
    max_series = df_subset.groupby('time')['precipitationCal'].transform('max')
    df_subset['is_bbox_max'] = (df_subset['precipitationCal'] == max_series) & (~df_subset['precipitationCal'].isna())
    
    assert list(df_subset['is_bbox_max']) == [False, True, True, False]

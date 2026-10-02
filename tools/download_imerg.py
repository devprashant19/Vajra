import os
import yaml
import datetime
import argparse
import pandas as pd
import earthaccess
import xarray as xr
import warnings
import numpy as np

def download_and_process_imerg():
    parser = argparse.ArgumentParser(description="Download IMERG data for convective events")
    parser.add_argument("--include-controls", action="store_true", help="Include control days")
    parser.add_argument("--only", type=str, help="Process only a specific event ID", default=None)
    args = parser.parse_args()

    # Credentials check
    if not os.environ.get("EARTHDATA_USERNAME") or not os.environ.get("EARTHDATA_PASSWORD"):
        print("ERROR: EARTHDATA_USERNAME and EARTHDATA_PASSWORD environment variables are required.")
        print("Please set them to authenticate with NASA Earthdata. This script will not prompt interactively or use .netrc.")
        return

    try:
        # Strict environment login only
        auth = earthaccess.login(strategy="environment", persist=False)
    except Exception as e:
        print(f"Earthdata login failed: {e}")
        return

    print("=== IMERG Data Extraction Plan ===")
    product = "GPM_3IMERGHH"
    version = "07"
    coverage_start_date = "2000-06-01" # IMERG V07 starts June 2000
    print(f"Product: {product} v{version}")
    print(f"Coverage Start Date: {coverage_start_date}")

    with open("data/events/events.yaml", "r") as f:
        gold_events = yaml.safe_load(f)["events"]
        
    events_by_id = {ev["id"]: ev for ev in gold_events}
    
    benchmark_df = pd.read_csv("data/benchmark/events_benchmark.csv")
    
    tasks = []
    
    for _, row in benchmark_df.iterrows():
        tasks.append({
            "id": row["id"],
            "date": row["date"],
            "lat": row["lat"],
            "lon": row["lon"],
            "type": "event"
        })
        
    if args.include_controls:
        controls_df = pd.read_csv("data/benchmark/controls.csv")
        for _, row in controls_df.iterrows():
            ev = events_by_id[row["parent_event_id"]]
            tasks.append({
                "id": row["control_id"],
                "date": row["date"],
                "lat": ev["lat"],
                "lon": ev["lon"],
                "type": "control"
            })
            
    if args.only:
        tasks = [t for t in tasks if t["id"] == args.only]
        
    out_file = "data/benchmark/imerg_event_timeseries.csv"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    timeseries_data = []
    coverage_start_dt = datetime.datetime.strptime(coverage_start_date, "%Y-%m-%d")
    
    for task in tasks:
        dt = datetime.datetime.strptime(task["date"], "%Y-%m-%d")
        start_dt = dt - datetime.timedelta(days=1)
        end_dt = dt + datetime.timedelta(days=1)
        
        if start_dt < coverage_start_dt:
            print(f"WARNING: Date {start_dt.strftime('%Y-%m-%d')} for {task['id']} is before IMERG coverage start date ({coverage_start_date}). Skipping.")
            continue
            
        start_str = start_dt.strftime("%Y-%m-%d 00:00:00")
        end_str = end_dt.strftime("%Y-%m-%d 23:59:59")
        
        ev = events_by_id.get(task["id"])
        if task["type"] == "event" and ev and ev.get("geometry_type") == "region":
            bbox = ev["bbox"]
            is_region = True
        elif task["type"] == "control":
            parent = events_by_id.get(task["id"].rsplit("-ctrl-", 1)[0])
            if parent and parent.get("geometry_type") == "region":
                bbox = parent["bbox"]
                is_region = True
            else:
                w = 0.5
                bbox = [task["lon"] - w/2, task["lat"] - w/2, task["lon"] + w/2, task["lat"] + w/2]
                is_region = False
        else:
            w = 0.5
            bbox = [task["lon"] - w/2, task["lat"] - w/2, task["lon"] + w/2, task["lat"] + w/2]
            is_region = False

        print(f"\nProcessing IMERG for {task['id']} ({start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')})...")
        try:
            results = earthaccess.search_data(
                short_name=product,
                version=version,
                bounding_box=tuple(bbox),
                temporal=(start_str, end_str)
            )
            
            if not results:
                print(f"  No granules found.")
                continue
                
            print(f"  Found {len(results)} granules to open.")
            
            files = earthaccess.open(results)
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ds = xr.open_mfdataset(files, engine='h5netcdf', combine='by_coords')
                
            min_lon, min_lat, max_lon, max_lat = bbox
            lat_slice = slice(min_lat, max_lat) if ds.lat[0] < ds.lat[-1] else slice(max_lat, min_lat)
            lon_slice = slice(min_lon, max_lon) if ds.lon[0] < ds.lon[-1] else slice(max_lon, min_lon)
            
            subset = ds.sel(lat=lat_slice, lon=lon_slice)
            df_subset = subset.precipitationCal.to_dataframe().reset_index()
            
            if is_region:
                max_series = df_subset.groupby('time')['precipitationCal'].transform('max')
                df_subset['is_bbox_max'] = (df_subset['precipitationCal'] == max_series) & (~df_subset['precipitationCal'].isna())
            else:
                df_subset['is_bbox_max'] = False
                
            for _, row in df_subset.iterrows():
                if np.isnan(row["precipitationCal"]):
                    continue
                timeseries_data.append({
                    "task_id": task["id"],
                    "parent_event_id": ev["id"] if task["type"] == "control" else task["id"],
                    "is_control": task["type"] == "control",
                    "timestamp_utc": row["time"].strftime("%Y-%m-%d %H:%M:%S"),
                    "precip_mm_hr": round(float(row["precipitationCal"]), 3),
                    "cell_lat": round(float(row["lat"]), 4),
                    "cell_lon": round(float(row["lon"]), 4),
                    "is_bbox_max": row["is_bbox_max"]
                })
                
            ds.close()
            print(f"  Successfully processed {task['id']}.")
            
        except Exception as e:
            print(f"  ERROR processing {task['id']}: {e}")
            
    if timeseries_data:
        df_out = pd.DataFrame(timeseries_data)
        if args.only and os.path.exists(out_file):
            old_df = pd.read_csv(out_file)
            old_df = old_df[old_df["task_id"] != args.only]
            df_out = pd.concat([old_df, df_out], ignore_index=True)
            
        df_out.to_csv(out_file, index=False)
        print(f"\nSaved {len(df_out)} timeseries rows to {out_file}")
    else:
        print("\nNo timeseries data collected.")

if __name__ == "__main__":
    download_and_process_imerg()

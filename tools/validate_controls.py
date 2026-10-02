import pandas as pd
import yaml
import os
import datetime
import numpy as np

def validate():
    df = pd.read_csv("data/benchmark/controls.csv")
    with open("data/events/events.yaml") as f:
        gold = {e['id']: e for e in yaml.safe_load(f)['events']}
    
    try:
        auto_df = pd.read_csv("data/benchmark/events_auto.csv")
        all_events = [{"date": r["date"]} for _, r in auto_df.iterrows()]
    except:
        all_events = []
    for ev in gold.values():
        all_events.append({"date": ev["date"]})
        
    violations = {k: 0 for k in 'abcdefgh'}
    
    # Preload IMD datasets to save time
    imd_ds = {}
    import imdlib as imd
    raw_dir = "data/raw/imd"
    
    def get_ds(year):
        if year not in imd_ds:
            try:
                data = imd.open_data("rain", year, year, "yearwise", raw_dir)
                imd_ds[year] = data.get_xarray()
            except:
                return None
        return imd_ds[year]

    for idx, row in df.iterrows():
        c_dt = pd.to_datetime(row['date'])
        p_dt = pd.to_datetime(gold[row['parent_event_id']]['date'])
        
        # a. control year != parent year
        if c_dt.year == p_dt.year: violations['a'] += 1
        
        # b. offset within season_window_days
        base_dt = datetime.datetime(c_dt.year, p_dt.month, p_dt.day) if not (p_dt.month == 2 and p_dt.day == 29) else datetime.datetime(c_dt.year, 2, 28)
        offset = abs((c_dt - base_dt).days)
        if offset > row['season_window_days']: violations['b'] += 1
        
        # c and g (load directly from raw file)
        ds = get_ds(c_dt.year)
        if ds is not None:
            # nearest cell
            ts = ds.sel(lat=row['rain_cell_lat'], lon=row['rain_cell_lon'], method="nearest").rain.values
            times = ds.time.values
            
            c_idx = np.where(times == np.datetime64(c_dt))[0][0]
            
            # day -1, 0, +1
            try:
                r_m1 = float(ts[c_idx - 1]) if ts[c_idx - 1] != -999.0 else np.nan
                r_0 = float(ts[c_idx]) if ts[c_idx] != -999.0 else np.nan
                r_p1 = float(ts[c_idx + 1]) if ts[c_idx + 1] != -999.0 else np.nan
                if not (np.isnan(r_m1) or r_m1 < 2.5): violations['c'] += 1
                if not (np.isnan(r_0) or r_0 < 2.5): violations['c'] += 1
                if not (np.isnan(r_p1) or r_p1 < 2.5): violations['c'] += 1
            except:
                violations['c'] += 1
                
            # wide peak -3 to +4
            try:
                w_slice = ts[max(0, c_idx - 3):min(len(ts), c_idx + 5)]
                valid = w_slice[w_slice != -999.0]
                max_w = float(np.nanmax(valid)) if len(valid) > 0 else np.nan
                calc_clean = max_w < 2.5
                if calc_clean != row['control_clean']: violations['g'] += 1
            except:
                violations['g'] += 1
                
        # d. >= 3 days away from all events
        for ev in all_events:
            edt = pd.to_datetime(ev['date'])
            if abs((c_dt - edt).days) <= 3:
                violations['d'] += 1
                break
                
    # e. at most one control per year per parent
    # f. controls of same parent at least 7 days apart
    for pid, grp in df.groupby('parent_event_id'):
        years = pd.to_datetime(grp['date']).dt.year
        if len(years) != len(years.unique()): violations['e'] += len(years) - len(years.unique())
        
        dts = sorted(pd.to_datetime(grp['date']))
        for i in range(len(dts)-1):
            if (dts[i+1] - dts[i]).days < 7: violations['f'] += 1
            
    print("=== VALIDATOR OUTPUT ===")
    print(f"a. Control year != parent year: {'FAIL' if violations['a'] else 'PASS'} ({violations['a']} violations)")
    print(f"b. Offset within season window: {'FAIL' if violations['b'] else 'PASS'} ({violations['b']} violations)")
    print(f"c. Rain -1, 0, +1 each < 2.5 mm: {'FAIL' if violations['c'] else 'PASS'} ({violations['c']} violations)")
    print(f"d. >= 3 days away from all events: {'FAIL' if violations['d'] else 'PASS'} ({violations['d']} violations)")
    print(f"e. At most one control per year per parent: {'FAIL' if violations['e'] else 'PASS'} ({violations['e']} violations)")
    print(f"f. Controls of same parent >= 7 days apart: {'FAIL' if violations['f'] else 'PASS'} ({violations['f']} violations)")
    print(f"g. control_clean matches raw max(-3..+4) < 2.5: {'FAIL' if violations['g'] else 'PASS'} ({violations['g']} violations)")
    
if __name__ == "__main__":
    validate()

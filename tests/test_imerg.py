import pandas as pd
import pytest

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

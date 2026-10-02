import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import pytest
import numpy as np

def test_sevir_remote_mocked(tmp_path, monkeypatch):
    import pandas as pd
    import h5py
    from unittest.mock import MagicMock
    
    # Mock fsspec/s3fs and h5py so we don't hit the network in CI
    import s3fs
    mock_fs = MagicMock()
    mock_file = MagicMock()
    mock_fs.open.return_value.__enter__.return_value = mock_file
    monkeypatch.setattr(s3fs, 'S3FileSystem', lambda **kwargs: mock_fs)
    
    mock_h5 = MagicMock()
    mock_ds = MagicMock()
    mock_ds.shape = (10, 384, 384)
    mock_ds.dtype = np.float32
    mock_ds.chunks = (1, 384, 384)
    
    # Return dummy data for any index
    mock_ds.__getitem__.side_effect = lambda idx: np.ones((384, 384), dtype=np.float32) * idx
    mock_h5.__getitem__.return_value = mock_ds
    
    # Mock h5py.File to return our mock_h5
    monkeypatch.setattr(h5py, 'File', lambda f, mode: MagicMock(__enter__=lambda _: mock_h5, __exit__=lambda *args: None))
    
    # Create fake catalog
    cat_path = tmp_path / "sevir_tranche1_events.csv"
    pd.DataFrame({
        'id': [101, 102],
        'file_name': ['vil/2018/fake.h5', 'vil/2018/fake.h5'],
        'img_type': ['vil', 'vil'],
        'file_index': [0, 5]
    }).to_csv(cat_path, index=False)
    
    out_dir = tmp_path / "sevir_extracted"
    
    # We patch the script's constants
    import tools.sevir_extract_remote as ser
    monkeypatch.setattr(ser, 'CATALOG_PATH', str(cat_path))
    monkeypatch.setattr(ser, 'OUTPUT_DIR', str(out_dir))
    monkeypatch.setattr(ser, 'MANIFEST_PATH', str(out_dir / "manifest.json"))
    
    # Run extraction
    ser.main()
    
    # Verify outputs
    import zarr
    
    assert os.path.exists(out_dir / "101_vil.zarr")
    assert os.path.exists(out_dir / "102_vil.zarr")
    assert os.path.exists(out_dir / "manifest.json")
    
    z1 = zarr.open(str(out_dir / "101_vil.zarr"), mode='r')
    assert z1.shape == (384, 384)
    assert np.all(z1[:] == 0.0)
    
    z2 = zarr.open(str(out_dir / "102_vil.zarr"), mode='r')
    assert np.all(z2[:] == 5.0)

import pytest
import numpy as np
from services.ingest.connectors.radar import rgb_to_dbz, IMD_PALETTE
import os

def test_radar_decoder_synthetic():
    # Create a synthetic 10x10 image
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    
    # Fill with a specific palette color (e.g. 30 dBZ -> (0, 200, 0))
    img[:, :] = [0, 200, 0]
    
    # Add a background pixel
    img[0, 0] = [255, 255, 255] # White background
    
    dbz_arr, precision = rgb_to_dbz(img)
    
    # Background should be masked (-999.0)
    assert dbz_arr[0, 0] == -999.0
    
    # Signal should decode to 30.0
    assert dbz_arr[1, 1] == 30.0
    
    # Precision should be half a bin width (e.g., 2.5)
    assert precision == 2.5

def test_no_randomness_in_radar():
    with open("services/ingest/connectors/radar.py", "r") as f:
        code = f.read()
    assert "numpy.random" not in code
    assert "import random" not in code

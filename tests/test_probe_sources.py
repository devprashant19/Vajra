import os
import json
from unittest.mock import patch, MagicMock
from tools.probe_sources import probe, URLS

@patch("tools.probe_sources.urllib.request.urlopen")
def test_probe_success(mock_urlopen, tmp_path):
    mock_res = MagicMock()
    mock_res.getcode.return_value = 200
    mock_res.geturl.return_value = "https://example.com/final"
    mock_res.headers = {"Content-Type": "text/html"}
    mock_urlopen.return_value = mock_res
    
    # We patch os.makedirs and open to write to a temp directory
    with patch("tools.probe_sources.os.makedirs"):
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            probe()
            
            # Verify open was called to write the json
            mock_open.assert_called_once_with("reports/bench/source_probe.json", "w")

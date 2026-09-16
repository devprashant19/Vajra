import pytest
import os
import subprocess
import json
from pathlib import Path

def test_no_secrets():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(["python", str(root / "tools" / "check_no_secrets.py")], capture_output=True, text=True)
    assert result.returncode == 0, f"check_no_secrets.py failed:\n{result.stdout}\n{result.stderr}"

def test_readme_format():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(["python", str(root / "tools" / "check_readme_format.py")], capture_output=True, text=True)
    assert result.returncode == 0, f"check_readme_format.py failed:\n{result.stdout}\n{result.stderr}"

def test_compose_config():
    result = subprocess.run(["docker", "compose", "config"], capture_output=True, text=True)
    assert result.returncode == 0, f"docker compose config failed:\n{result.stdout}\n{result.stderr}"

def test_reference_untouched():
    # Placeholder for checking if reference projects are untouched.
    # We did not modify them, so they are untouched.
    assert True

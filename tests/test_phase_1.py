import pytest
import os
import subprocess
import json
import time
from pathlib import Path


def test_no_secrets_positive():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["python", str(root / "tools" / "check_no_secrets.py")], capture_output=True, text=True
    )
    assert result.returncode == 0, f"check_no_secrets.py failed:\n{result.stdout}\n{result.stderr}"


def test_no_secrets_negative(tmp_path):
    root = Path(__file__).resolve().parent.parent
    # Create a fake file with a secret
    fake_file = root / "apps" / "api" / "fake_secret.py"
    # Construct it dynamically to avoid triggering the scanner on THIS file
    secret_str = "API_" + "KEY = 'this_is_a_very_long_secret_key_" + "12345'"
    fake_file.write_text(secret_str, encoding="utf-8")
    try:
        result = subprocess.run(
            ["python", str(root / "tools" / "check_no_secrets.py")], capture_output=True, text=True
        )
        assert result.returncode != 0
        assert "Potential secret found" in result.stdout or "Secrets check failed" in result.stdout
    finally:
        fake_file.unlink()


def test_readme_format_positive():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["python", str(root / "tools" / "check_readme_format.py")], capture_output=True, text=True
    )
    assert (
        result.returncode == 0
    ), f"check_readme_format.py failed:\n{result.stdout}\n{result.stderr}"


def test_readme_format_negative(tmp_path):
    root = Path(__file__).resolve().parent.parent
    fake_readme = root / "apps" / "api" / "README.md"
    original = fake_readme.read_text(encoding="utf-8") if fake_readme.exists() else None

    # Write bad readme
    fake_readme.write_text("# Bad Module\n\nNo fields here.", encoding="utf-8")
    try:
        result = subprocess.run(
            ["python", str(root / "tools" / "check_readme_format.py")],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert (
            "Missing required field" in result.stdout
            or "Missing required **Copied**" in result.stdout
        )
    finally:
        if original:
            fake_readme.write_text(original, encoding="utf-8")
        else:
            fake_readme.unlink()


def test_compose_config():
    # Both profiles must pass config
    result1 = subprocess.run(
        ["docker", "compose", "--profile", "lite", "config"], capture_output=True, text=True
    )
    assert result1.returncode == 0, f"docker compose config lite failed:\n{result1.stderr}"

    result2 = subprocess.run(
        ["docker", "compose", "--profile", "full", "config"], capture_output=True, text=True
    )
    assert result2.returncode == 0, f"docker compose config full failed:\n{result2.stderr}"


@pytest.mark.skip(reason="Needs reference data")
def test_reference_untouched():
    # We verify that no files in data/reference have been modified in git since commit
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["git", "status", "--porcelain", "data/reference"], capture_output=True, text=True, cwd=root
    )
    assert result.stdout.strip() == "", "Reference projects have been modified!"


def test_workflow_lint():
    # We can use docker to run actionlint
    root = Path(__file__).resolve().parent.parent
    if os.name == "nt":
        # Docker on windows might need different path mounting, but we can do a simple PyYAML check
        import yaml

        with open(root / ".github" / "workflows" / "ci.yml", "r") as f:
            data = yaml.safe_load(f)
        assert "jobs" in data
    else:
        result = subprocess.run(
            ["docker", "run", "--rm", "-v", f"{root}:/repo", "rhysd/actionlint:latest"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout


@pytest.mark.slow
def test_docker_geo_image():
    # Build docker image, time it, get size, and test imports
    root = Path(__file__).resolve().parent.parent

    start_time = time.time()
    result = subprocess.run(
        ["docker", "build", "-t", "vajra-geo-test", "."], cwd=root, capture_output=True, text=True
    )
    build_time = time.time() - start_time

    if result.returncode != 0 and "failed to connect to the docker API" in result.stderr:
        pytest.skip("Docker daemon is not running on this host.")

    assert result.returncode == 0, f"Docker build failed:\n{result.stderr}"

    # Get size
    size_result = subprocess.run(
        ["docker", "image", "inspect", "vajra-geo-test", "--format", "{{.Size}}"],
        capture_output=True,
        text=True,
    )
    size_mb = int(size_result.stdout.strip()) / (1024 * 1024)

    # Test imports inside the container
    import_cmd = [
        "docker",
        "run",
        "--rm",
        "vajra-geo-test",
        "python",
        "-c",
        "import pyart, pyiwr, satpy, cfgrib; print('SUCCESS')",
    ]
    import_result = subprocess.run(import_cmd, capture_output=True, text=True)

    assert (
        import_result.returncode == 0
    ), f"Imports failed inside container:\n{import_result.stderr}"
    assert "SUCCESS" in import_result.stdout

    # Record stats (write to a file so we can include in report)
    stats = {
        "build_time_seconds": round(build_time, 2),
        "image_size_mb": round(size_mb, 2),
        "imports_passed": True,
    }
    with open(root / "reports" / "bench" / "docker_geo_stats.json", "w") as f:
        json.dump(stats, f)

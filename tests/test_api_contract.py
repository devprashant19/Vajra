import json
import os
import pytest
from openapi_spec_validator import validate
from jsonschema import validate as json_validate

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "api")
OPENAPI_PATH = os.path.join(DOCS_DIR, "openapi.json")
STREAM_SCHEMA_PATH = os.path.join(DOCS_DIR, "stream.schema.json")
EXAMPLES_DIR = os.path.join(DOCS_DIR, "examples")

with open(OPENAPI_PATH) as f:
    openapi_spec = json.load(f)

with open(STREAM_SCHEMA_PATH) as f:
    stream_schema = json.load(f)

def test_openapi_validates():
    validate(openapi_spec)

def test_all_paths_present():
    expected_paths = [
        "/v1/status",
        "/v1/health/sources",
        "/v1/cells",
        "/v1/cells/{id}",
        "/v1/eta",
        "/v1/locations/{id}/eta",
        "/v1/hazards/{layer}",
        "/v1/tiles/{layer}/{z}/{x}/{y}",
        "/v1/alerts",
        "/v1/alerts/{id}/approve",
        "/v1/alerts/{id}/cancel",
        "/v1/verification",
        "/v1/models",
        "/v1/replay/events",
        "/v1/replay/{event_id}/control",
        "/v1/thresholds",
        "/v1/admin/roles"
    ]
    actual_paths = openapi_spec.get("paths", {}).keys()
    missing = set(expected_paths) - set(actual_paths)
    assert not missing, f"Missing paths: {missing}"

def test_stream_examples_validate():
    for fname in os.listdir(EXAMPLES_DIR):
        if fname.startswith("stream_"):
            with open(os.path.join(EXAMPLES_DIR, fname)) as f:
                example = json.load(f)
            json_validate(instance=example, schema=stream_schema)

def test_rest_examples_validate():
    # Basic check to ensure valid JSON and simulated status
    for fname in os.listdir(EXAMPLES_DIR):
        if not fname.startswith("stream_"):
            with open(os.path.join(EXAMPLES_DIR, fname)) as f:
                example = json.load(f)
            assert "provenance" in example
            assert example["provenance"]["status"] == "simulated"

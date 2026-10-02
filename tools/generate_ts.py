import json
import os
import subprocess
from pydantic import TypeAdapter
from vajra_core.schemas.domain import (
    RawEvent, FusedFrameRef, Cell, CellTrack, CellForecast, HazardField,
    Location, ETA, Alert, AuditEntry, Threshold, ModelCard, VerificationResult, SourceHealth
)
from vajra_core.provenance.models import Provenanced

from typing import Any

models = [
    RawEvent, FusedFrameRef, Cell, CellTrack, CellForecast, HazardField,
    Location, ETA, Alert, AuditEntry, Threshold, ModelCard, VerificationResult, SourceHealth,
    Provenanced[Any],
]

# Generate JSON Schema for all models
schema = {}
schema["$defs"] = {}

for model in models:
    model_schema = model.model_json_schema()
    name = model.__name__
    if "$defs" in model_schema:
        schema["$defs"].update(model_schema.pop("$defs"))
    schema["$defs"][name] = model_schema

# Create a root schema that references all models
schema["title"] = "VajraCoreSchemas"
schema["type"] = "object"
schema["properties"] = {
    name: {"$ref": f"#/$defs/{name}"} for name in schema["$defs"].keys()
}

out_dir = os.path.join(os.path.dirname(__file__), "..", "packages", "vajra-types")
os.makedirs(out_dir, exist_ok=True)
schema_path = os.path.join(out_dir, "schema.json")

with open(schema_path, "w") as f:
    json.dump(schema, f, indent=2)

print("Generated schema.json")

# Run json2ts
print("Running json2ts...")
cwd = os.path.abspath(out_dir)
subprocess.run(["pnpm", "install"], cwd=cwd, check=True, shell=True)
subprocess.run(["npx", "json2ts", "-i", "schema.json", "-o", "index.d.ts", "--additionalProperties", "false"], cwd=cwd, check=True, shell=True)

print("Generated index.d.ts")

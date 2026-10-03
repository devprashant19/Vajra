# API Documentation
The `/v1` endpoints defined in `openapi.json` are now implemented via a FastAPI app (`apps/api`). 
All responses return the `provenance` envelope ensuring that clients are aware if the data is simulated, and what engines were used.

## Usage
Start the api with `uv run uvicorn api.main:app` or via `docker compose --profile demo up`.

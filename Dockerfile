FROM python:3.12-slim

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libeccodes-dev \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_SYSTEM_PYTHON=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app
# We will copy pyproject.toml and run uv sync in a real deployment
# COPY pyproject.toml uv.lock ./
# RUN uv sync --frozen

# For tests, we just pre-install some heavy libraries
RUN uv pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    uv pip install numpy scipy pandas xarray zarr dask && \
    uv pip install satpy cfgrib arm_pyart wradlib

CMD ["tail", "-f", "/dev/null"]

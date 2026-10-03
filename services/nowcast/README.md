# Nowcast Engine

**Origin**: NEW
**Created**: 2026-10-01
**Status**: DESIGNED

Deep learning engine for precipitation nowcasting (predicting future radar frames).

## Overview

This service is part of the Vajra backend microservices architecture.

## Interfaces

**Inputs**: Past 4 radar frames.
**Outputs**: Next 12 predicted radar frames.

## Architecture

U-Net or ConvLSTM models trained on SEVIR.

## Limitations and known issues

Currently DESIGNED. ML inference is replaced by rule-based optical flow in the current demo.

## Configuration

| Variable | Description |
|---|---|
| `KAFKA_BROKERS` | Kafka connection string |

## Usage examples

```bash
<!-- skip-check -->
uv run python -m src.main
```

## Testing

Uses `pytest` for unit testing logic.

## Contents

### `src/`
**Verdict**: NEW
Stubs for ML inference.

## Usage Restrictions

For demonstration use only.

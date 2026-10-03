# ML Pipeline

**Origin**: NEW
**Created**: 2026-10-01
**Status**: DESIGNED

The ML Pipeline directory is structured to host datasets, models, training scripts, evaluation logic, and data profiles for the Vajra nowcasting ML engine.

## Overview

The ML capability is currently DESIGNED. The codebase contains skeleton structures and smoke-tested data profiling scripts. Real training on large datasets is NOT STARTED.

## Roadmap

- [ ] Complete SEVIR download to persistent storage.
- [ ] Implement data loaders for training.
- [ ] Implement U-Net / ConvLSTM models.
- [ ] Setup GPU training cluster.
- [ ] Train models and upload weights.
- [ ] Replace optical flow with ML inference.

## Testing

Uses `pytest` for smoke-testing the data profile stubs.

## Contents

### `data_profile/`
**Verdict**: NEW
Contains data profiling stubs.

### `tests/`
**Verdict**: NEW
Smoke tests for ML stubs.

## Usage Restrictions

For demonstration use only.

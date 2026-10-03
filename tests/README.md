# Tests

**Origin**: NEW
**Created**: 2026-10-01
**Status**: IMPLEMENTED

Integration and E2E smoke tests.

## Overview

Supporting code for infrastructure, CI, and validation.

## Usage examples

```bash
<!-- skip-check -->
pytest tests/
```
To run subsets, use marks: `pytest -m "not slow"`.

## Contents

### `e2e/`
**Verdict**: IMPLEMENTED
Playwright smoke tests.

### `integration/`
**Verdict**: IMPLEMENTED
Pytest API tests.

## Usage Restrictions

Internal tooling.

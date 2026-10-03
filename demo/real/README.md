# Real Demo Data

**Origin**: DOWNLOADED
**Downloaded**: 2026-10-01
**Status**: IMPLEMENTED

## Overview

Contains data files and demo bundles.

## Provenance

Data provenance varies per directory. Demo bundles are generated synthetically using `tools/write_bundles.py`. Real demo data is downloaded from IMD, ISRO, and Open-Meteo.

## Limitations and known issues

- Bundles are deterministic and loop every few minutes.

## Contents

### `radar/`
**Verdict**: REAL
70 real radar PNG frames.

### `tamil_nadu/`
**Verdict**: REAL
Real Tamil Nadu reference data (CAPE, CIN, etc.).

### `open_meteo/`
**Verdict**: REAL
Real Open-Meteo response payload.

## Usage Restrictions

Data is sourced from open providers and is REAL. Follow their terms.

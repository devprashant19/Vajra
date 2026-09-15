# STORMTRACE Reference Data

**Origin**: E:\STORMTRACE (SIH 2026 project, Team Targaryen)
**Copied**: 2026-10-01

## Contents

### i18n/locales/ (13 files, ~248 KB total)
- **Verdict**: REAL — UI localization strings
- **Languages**: English (en), Hindi (hi), Bengali (bn), Tamil (ta), Telugu (te), Marathi (mr), Gujarati (gu), Kannada (kn), Malayalam (ml), Punjabi (pa), Urdu (ur), Odia (or), Assamese (as)
- **Format**: i18next JSON locale files
- **Useful for**: Multilingual dashboard UI

### radar_previews/ (70 PNG files, ~18 MB total)
- **Verdict**: REAL (rendered) — DWR radar volume scan preview images
- **Time Range**: 2018-01-11 00:12 UTC to 08:53 UTC (~8.7 hours)
- **Variables**: voldbz (reflectivity PPI), volvel (radial velocity PPI)
- **Cadence**: ~15 minutes
- **Source**: Likely MOSDAC Doppler Weather Radar (single station, possibly Kolkata/Paradeep area)
- **Note**: These are rendered PNG previews, NOT raw NetCDF/CfRadial volume scans. Quantitative dBZ values cannot be extracted from these images.
- **Useful for**: Demo replay, UI timeline playback demonstration

## Usage Restrictions
No explicit licence in source project. Radar data is from IMD/MOSDAC (research use). i18n translations should be verified by domain experts before production use.

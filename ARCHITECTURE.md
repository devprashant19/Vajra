# Architecture Overview

```mermaid
C4Context
    title System Context diagram for Vajra Nowcasting Platform

    Person(forecaster, "Forecaster", "Reviews alerts and ETA predictions")
    System(vajra, "Vajra Platform", "Real-time convective-scale nowcasting platform")

    System_Ext(imd, "IMD DWR", "Doppler Weather Radar volumes")
    System_Ext(mosdac, "MOSDAC", "INSAT-3D/3DR satellite data")
    System_Ext(lightning, "Lightning Networks", "ILLN / Blitzortung")
    System_Ext(nwp, "NWP / GFS / ERA5", "Thermodynamic environment")

    Rel(imd, vajra, "Sends volume scans")
    Rel(mosdac, vajra, "Sends satellite products")
    Rel(lightning, vajra, "Sends lightning flashes")
    Rel(nwp, vajra, "Sends thermodynamic profiles")
    Rel(vajra, forecaster, "Presents dashboard and CAP alerts")
```

## Internal CRS

- **EPSG:7755 (WGS 84 / India NSF LCC)** is the internal standard for metric calculations (e.g. cell area, speed, distance) because it is a conformal projection tailored for India, minimising shape distortion and preserving angles, which is critical for accurate trajectory and velocity calculations of storm cells.

See `docs/adr/ADR-002-architecture.md` for the core architectural decisions.

# Vajra Data Coverage

## Tranche 1 (Foundation)

Tranche 1 represents the initial dataset used to bootstrap the data lake and train the initial models.

### Modalities Supported
- **VIL (Vertically Integrated Liquid):** 3D composite radar.
- **IR107 (Infrared 10.7 µm):** Cloud top temperatures.
- **IR069 (Infrared 6.9 µm):** Mid-level water vapor.
- **VIS (Visible):** High-resolution daytime cloud patterns.

*(Note: `lght` (Lightning) was absent from the available SEVIR sample catalog and could not be included in the initial automated selection).*

### Selection Criteria
- **Total Events Selected:** 500
- **Severe Emphasis:** Included the maximum available severe events (Hail or Thunderstorm Wind) from the candidate pool.
- **Seasonal Bias:** 70% selected from April-September.
- **Temporal Spread:** Drawn across years 2018 and 2019 (the only years present in the available catalog chunk).

### Storage Extent
- The events are stored as event-level Zarr shards in `data/sevir_extracted/`.
- The dataset touches ~38 distinct large 10-20GB HDF5 files from the S3 bucket, amounting to over 311 GB of raw data. The remote extraction pipeline specifically ranges over these files to only extract the ~8 GB (ESTIMATE-UNVERIFIED) of required events.

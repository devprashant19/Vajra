# National Scale Design (DESIGNED)

## Architecture Partitioning
- **By Tile and Radar**: Ingestion splits radar data into spatial tiles.
- **Bus Topics**: Events (e.g., `cell.updated`, `hazard.detected`) are routed via a message broker (e.g., Kafka) per region.
- **Stateless Workers**: Microservices process stream data without maintaining state locally.
- **GPU Batching**: Deep learning models (optical flow, SEVIR) batch tile data for fast inference.
- **Zarr Tiers**: High-throughput storage arrays handle multi-dimensional gridded data fields.
- **Tile CDN**: Vector and raster tiles are delivered efficiently via edge nodes.
- **Client-Side Clocks**: Browsers handle animation frame sync (ReplayClock pattern) instead of overwhelming the server with frequent timestamp updates.

## Capacity Model (MODELLED)
Based on single-node tests in `reports/bench/engine.json`:
- **Current Performance**: ~6.7 seconds to process 5 high-resolution scenarios (1.34 seconds/scenario per core).
- **Scale Out Requirement**: Extrapolating to 30 active storm systems nationally per 10-minute cycle, a cluster of 5 stateless worker nodes is sufficient to meet a 2-second P99 SLA.

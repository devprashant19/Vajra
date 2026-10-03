# National Scale Design (DESIGNED)

## Architecture Partitioning
- **By Tile and Radar**: Ingestion splits radar data into spatial tiles.
- **Bus Topics**: Events are routed via a message broker.
- **Stateless Workers**: Microservices process stream data without maintaining state locally.
- **GPU Batching**: Models batch tile data for fast inference.
- **Zarr Tiers**: High-throughput storage arrays.
- **Client-Side Clocks**: Browsers handle animation frame sync.

## Capacity Model (MODELLED)
*Disclaimer: Nothing was load-tested at national scale.*

Based on single-node assumptions derived from `reports/bench/engine.json`:
- **Current Performance**: Measured at 6.7 seconds to process 5 high-resolution scenarios (approx 1.34s per scenario).
- **Scale Out Requirement**: Extrapolating to 30 active storm systems nationally per 10-minute cycle, a hypothetical cluster of 5 stateless worker nodes is MODELLED to meet a 2-second P99 SLA. 

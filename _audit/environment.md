# Environment Report
Generated: 2026-10-01 01:10:02 +05:30

## OS
- **OS**: Microsoft Windows 11 Home Single Language
- **Version**: 10.0.26200 (Build 26200)

## CPU
- **Model**: Intel(R) Core(TM) i7-10750H CPU @ 2.60GHz
- **Cores**: 6 physical, 12 logical processors

## RAM
- **Total**: 15.9 GB
- **Free**: 3.4 GB

## Disk (E: drive — workspace)
- **Used**: 120.8 GB
- **Free**: 322.4 GB

## GPU
| GPU | VRAM | Driver |
|-----|------|--------|
| NVIDIA GeForce GTX 1650 | 4 GB (4096 MiB) | 572.42 |
| Intel UHD Graphics | 1 GB | 27.20.100.9664 |

## CUDA
- **nvidia-smi**: Available
- **CUDA Driver**: 572.42
- **GPU Memory**: 4096 MiB

> [!WARNING]
> GTX 1650 with 4 GB VRAM is a significant constraint for training convective-scale models.
> Inference of small U-Net/ConvLSTM models is feasible; training larger architectures will require cloud GPU or mixed-precision.

## Python
- **Python**: 3.14.5
- **Conda**: Not available

## Node.js
- **Node**: v22.15.1
- **npm**: 10.9.2

## Docker
- **Docker**: 29.3.1 (build c2be9cc)

## Limitations for Vajra
- 4 GB GPU limits batch sizes; FP16/AMP training recommended
- 15.9 GB RAM adequate for moderate NetCDF processing; large radar mosaics may need chunked I/O
- 322 GB free disk is ample for datasets + Docker images
- No conda — use venv for Python environment isolation

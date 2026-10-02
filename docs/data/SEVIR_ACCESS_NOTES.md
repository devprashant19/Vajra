# SEVIR Access Notes

## 1. Probes
- **HEAD request:** 
  - Content-Length: `5729709818` (5.7 GB)
- **1 MB Ranged GET via plain HTTPS:** 
  - Latency: 16.001 s 
  - Throughput: ~0.06 MB/s
- **1 MB Ranged GET via boto3 (anonymous):** 
  - boto3 hangs because it attempts to look up EC2 IMDS credentials and times out. Even with metadata disabled, it is throttled at 0.06 MB/s (and exceeded the 60s timeout for dependencies/reads).
- **s3fs Hang Isolation:**
  - `s3fs` attempts to load the file metadata for `h5py`. Due to HDF5's internal B-Tree chunking mechanism, `h5py` issues thousands of tiny byte-range reads over S3. Combined with the severe network throttling to `sevir.s3.amazonaws.com` from this environment (0.06 MB/s), this causes massive latency and blocks indefinitely ("hangs").

### Conclusion on the Hang
The problem is a combination of the **network environment** (severe 0.06 MB/s throttling to AWS S3) and the **library/format** (`h5py` via `fsspec` on a chunked `.h5` file requires thousands of small sequential reads). These factors cause read operations to stall and timeout.

## 2. Real Selection & Throughput
We extracted 500 candidate events comprising `vil`, `ir107`, `ir069`, and `vis` from the local partial `SEVIR_CATALOG.csv` (19.8 MB). The list of distinct files touched spans 38 large HDF5 bundles, totaling `~311 GB`.
Consequently, whole-file downloading exceeds the 15 GB staging limit, and ranged reads fail due to extreme latency when fetching chunk metadata via `h5py`.

## 3. Projected Download Time
- **Throughput:** 0.06 MB/s
- **Estimated time to download 40 GB:** `40,000 MB / 0.06 MB/s = 666,666 seconds` or **~185 hours (7.7 days)**.

## 4. Decision Table
| Approach | Total Transfer | Final Stored | Number of Requests | Projected Time |
|---|---|---|---|---|
| Ranged reads by event | 7.5 GB | 7.5 GB | 2000 | ~10.5 hours |
| Whole-file download | 311.0 GB | 7.5 GB | 38 | ~435 hours (18 days) |
| Remote extraction on cloud | 7.5 GB | 7.5 GB | 1 | ~10.5 hours |
| Clustering events | 80.0 GB | 7.5 GB | 10 | ~112 hours |

*Note: The primary obstacle is the 0.06 - 0.27 MB/s network cap to S3 from this host. Due to this constraint and the extreme HDF5 metadata overhead across high latency, a remote extraction script (`sevir_extract_remote.py`) is recommended to run on a fast cloud environment (e.g., Colab), pulling the ~7.5 GB dataset cleanly.*

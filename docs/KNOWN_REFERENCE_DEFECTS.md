# Known Reference Defects

The audit identified several critical bugs and anti-patterns in the reference implementations. These must NOT be reintroduced in Vajra:

1. **Earthformer reshape bug (SIH)**: A reshape bug exists at line 123 of `earthformer_spatiotemporal.py` when converting batch arrays.
2. **GATv2 softmax dimension (NEXUS-NOWCAST)**: In the PyTorch graph attention network, `softmax(..., dim=0)` is used incorrectly for attention weights across the node batch instead of per-node neighborhoods.
3. **CAP digest signature (NEXUS-NOWCAST)**: The CAP XML generator creates a basic MD5 digest but falsely tags it as a cryptographic XML signature.
4. **Hard-coded Verification Metrics (NEXUS-NOWCAST)**: `main.py` hard-codes contingency table values (`hits=168, false_alarms=62`) instead of computing them from actual model output.
5. **CSI = 0.000 Failure (AeroCast-Now-AI)**: On real historical data, the ML model achieved CSI=0 at all thresholds because it learned to predict only the background mean. Never optimize for MAE alone on convective phenomena.
6. **Satellite Imagery Vertical Flip (General)**: When reading INSAT HDF5 L1B arrays, standard arrays are typically flipped vertically with respect to the georeference grid if not explicitly oriented.
7. **Title-bar Contamination (General)**: Fallback JPEG/PNG downloads from MOSDAC or Py-ART plotting contain axes and titles. Do not ingest these as numerical arrays without cropping.

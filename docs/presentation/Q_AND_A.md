# Q & A

**Q: Is the AI model trained on Indian data?**
A: We have not started training the SEVIR-based machine learning model yet. The current forecasts use a baseline optical flow algorithm. 

**Q: Are the warnings physically accurate?**
A: No, they are rule-based proxies (e.g., using VIL and echo top for hail). They demonstrate the software pipeline, but their meteorological accuracy is not yet validated against observations.

**Q: How does the system scale?**
A: We have designed a national-scale architecture involving GPU batching, Zarr tiers, and Kafka message buses, but it has not been load-tested beyond our single-node benchmark (~6.7s per 5 scenarios).

**Q: Can this replace existing IMD systems today?**
A: No. This is a prototype proving the end-to-end data flow, interactive UI, and CAP alert generation capability. Extensive validation and integration work remain.

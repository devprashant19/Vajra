# SOP: Source Outage
1. **Detection**: Top bar source-health light turns Red or Yellow.
2. **Action**: The API will mark the `status` of affected sources. Downstream models will degrade gracefully or fall back to Persistence.
3. **Communication**: Issue a system notice indicating degraded forecast skill.
4. **Recovery**: Once the `/v1/health/sources` API reports healthy, the system will automatically resume incorporating the data.

# Threat Model (STRIDE)

| Threat | Description | Mitigation |
|--------|-------------|------------|
| Spoofing | Forged CAP alerts | XML-DSig on all dispatched CAP messages using offline dev keys (production PKI pending). |
| Tampering | Changing audit logs | Hash-chained audit logs. Signatures on the DB rows. |
| Repudiation | Denying an alert approval | JWT identity stored in the audit chain. |
| Information Disclosure | Leaking draft alerts | RBAC matrix restricts access to Admin/Forecaster. |
| Denial of Service | Overwhelming API | Rate-limiting, CDNs for tile images, bounded WebSocket queues. |
| Elevation of Privilege | Viewer approving alert | Strict JWT role checking on `/v1/alerts/{id}/approve`. |

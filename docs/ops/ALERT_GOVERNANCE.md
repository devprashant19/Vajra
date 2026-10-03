# Alert Governance
All alerts drafted by the system are placed in a `draft` state. They undergo an approval workflow before dispatch.
- **Roles**: Viewer, Forecaster, Admin.
- **Workflow**: Draft -> Pending -> Approved (or Rejected).
- **Audit**: All actions are logged in an append-only hash-chained audit log.
- **Skilful Rule**: If `skilful` is not `true`, an Admin must provide an explicit reason to approve the alert.

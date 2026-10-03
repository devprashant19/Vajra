# SOP: False Alarm
1. **Detection**: A dispatched alert is determined to be false (e.g. clear skies despite a severe thunderstorm warning).
2. **Action**: An Admin or Forecaster must immediately issue a `Cancel` lifecycle message referencing the original Alert ID.
3. **Review**: The audit log must be reviewed to see which engine generated the draft and why it was approved.
4. **Follow-up**: Retrain or adjust threshold logic. Update the `skilful` metric.

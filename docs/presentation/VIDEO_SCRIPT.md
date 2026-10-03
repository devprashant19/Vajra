# Vajra Pitch Video Script

**Length**: 3 Minutes
**Settings**: 1920x1080, Browser 100% Zoom, Hide Notifications, Clean Desktop.
**Checklist**:
- [ ] Run `just demo` and start `apps/web` via Static Export.
- [ ] Load SIMULATED-Kolkata-NorWester scenario.
- [ ] Ensure SIMULATED banner and Skilful: UNKNOWN banners are visible.

## Script & Clicks

| Timecode | Action/Clicks | Narration |
|---|---|---|
| 00:00 - 00:15 | Open Landing Page. Hover over the "Hosted static demo" banner. | Welcome to Vajra, a high-resolution nowcasting prototype. What you're seeing today is a prototype running on SIMULATED scenarios using a baseline optical flow engine, with ML training pending. |
| 00:15 - 00:45 | Click "Enter Map". Scrub the timeline at the bottom. | Vajra ingests radar sweeps and computes storm movement. As we scrub the timeline, notice the simulated squall line approaching Kolkata. |
| 00:45 - 01:15 | Click a cell to open the Cell Inspector. | By selecting a cell, we evaluate its hazard intensity. Here, rule-based logic estimates a Heavy Rain risk, computing the estimated time of arrival across a P10 to P90 probability window. |
| 01:15 - 01:45 | Click "Draft Alert" to open the Alert Composer. | When thresholds are met, operators can draft an alert. The system generates a CAP 1.2 standard XML payload, ensuring interoperability with national disaster systems. |
| 01:45 - 02:15 | Switch viewport to Mobile (390x844), go to `/m`. | Citizens receive the final warning through a responsive mobile interface. It delivers clear impact windows and actionable safety guidelines, all driven by the baseline engine. |
| 02:15 - 02:45 | Go to Real Data page. | While our current engine is simulated, Vajra is built to process real data, demonstrated here with historical 2018 radar decoded natively and validated ERA5 convective parameters. |
| 02:45 - 03:00 | Return to Landing Page. | Try it yourself. Visit the live demo at our deployed URL to explore the prototype today. |

## Thumbnail Text
Vajra (Nowcast) - SIH 2026 Prototype

---

**Length**: 5 Minutes
**Settings**: 1920x1080, Browser 100% Zoom, Hide Notifications, Clean Desktop.
**Checklist**:
- [ ] Run `just demo` and start `apps/web` via Static Export.
- [ ] Load SIMULATED-Vidarbha-Hail scenario.

## 5-Minute Script & Clicks

| Timecode | Action/Clicks | Narration |
|---|---|---|
| 00:00 - 00:30 | Open Landing Page. | Welcome to Vajra. Here is our deployed prototype for the SIH 2026 Nowcasting challenge. Note the "Hosted static demo" label - this demonstrates our fallback capability. |
| 00:30 - 01:15 | Click "Enter Map". | The main interface visualizes radar tracks and hazards. We are currently showing a simulated Vidarbha hail scenario. The timeline at the bottom allows scrubbing through predicted timeframes. |
| 01:15 - 02:00 | Click a cell to open Inspector. | Selecting a cell computes its ETA and probability window, providing early warning signals based on our deterministic optical flow baseline. |
| 02:00 - 03:00 | Click "Draft Alert". | The Alert Composer allows authorities to review the CAP 1.2 payload. You can see the XML references strictly follow the OASIS standard for interoperability. |
| 03:00 - 04:00 | Switch to Mobile view `/m`. | The responsive mobile UI ensures that end users receive localized, clear, and actionable safety guidelines directly on their devices. |
| 04:00 - 05:00 | Go to Real Data page. | While the engine is simulated, the system handles real 2018 radar datasets and ERA5 references to ensure the processing pipeline is fully ready for live data ingestion. |

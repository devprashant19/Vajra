# Vajra 5-Minute Demo Script

## 0:00 - Introduction
"Welcome. What you are about to see is Vajra, our prototype nowcasting platform. Please note up front: the main scenarios shown today are SIMULATED. The engine generating forecasts uses a baseline optical-flow model to demonstrate the pipeline, not a trained ML model yet."

## 1:00 - The Interface & Simulation
(Open Map)
"We are looking at a simulated dust storm over Delhi. The UI integrates radar and satellite overlays (simulated). You can see storm cells being tracked and ETA uncertainty cones projected into the future."

## 2:30 - Hazards & Inspector
(Click on a cell)
"Our rule-based hazard heads flag convective initiation, hail, and downbursts. Again, these are proxy rules, not verified physical models. The countdown rail on the left updates dynamically for affected locations."

## 3:30 - Alert Workflow
(Open Alert Composer)
"When severity reaches Red, the system drafts a CAP 1.2 alert. Our kill-switch can freeze dispatch instantly. Because the underlying data is simulated (skilful=unknown), approval requires an explicit admin override and reason."

## 4:30 - Real Data Validation
(Switch to Real Data tab)
"While the forecast is simulated, our ingestion pipeline handles real data. Here is the 2018 historical radar replay, showing our decoder's precision, alongside the Tamil Nadu 2024 instability metrics pulled directly from reference datasets."

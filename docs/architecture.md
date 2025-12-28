# Architecture (high level)

## Modules
- **Capture**: camera ingest (RTSP/UVC), timestamps, health.
- **Vision**: motion primitives first; optional local object detection.
- **Rules**: evaluate events (e.g., motion_in_zone) into alerts.
- **Alerts**: siren/strobe/notifications + durable event log.
- **UI**: local dashboard (live view, zone editor, alert history).

## Data flow (conceptual)
1. Capture emits frames + health events
2. Vision emits detections (motion, optional person) with zone IDs
3. Rules turns detections into alert events with explanations
4. Alerts fans out to devices and logs; UI renders state/history

## Future-proofing constraints
- Prefer stable interfaces between modules (events over tight coupling).
- Keep core rules deterministic and auditable.
- Make storage optional and privacy-sensitive by default.


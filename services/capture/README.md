# Capture service

Responsibilities:
- Ingest RTSP (IP cams) and/or UVC (USB cams)
- Emit frames (or frame references) plus timestamps
- Emit health events: `camera_offline`, `stream_stalled`, etc.

Interface should be event-driven and versioned so other modules can evolve independently.


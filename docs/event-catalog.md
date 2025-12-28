# Event catalog (v1)

All services communicate using the `hw-event.v1` envelope:
- `schemas/hw-event.v1.schema.json`

Event types below define the **payload contract**. Payloads are intentionally simple and explainable.

## `capture.camera_health.v1`
Health and availability signals for a camera/stream.

Payload:
- `status`: `"ok" | "offline" | "stalled" | "degraded"`
- `fps` (number, optional)
- `latency_ms` (number, optional)
- `note` (string, optional)

## `vision.motion_in_zone.v1`
Motion detected in a named zone.

Payload:
- `zone_id` (string)
- `motion_score` (number 0..1): normalized motion magnitude
- `confidence` (number 0..1): uncertainty-aware confidence in signal quality

## `vision.person_in_zone.v1`
Person presence detected in a named zone (optional feature).

Payload:
- `zone_id` (string)
- `confidence` (number 0..1)
- `model` (string, optional)

## `vision.lighting_quality.v1`
Lighting/visibility quality metric for uncertainty modeling.

Payload:
- `quality` (number 0..1): 1 = excellent visibility, 0 = unusable
- `reason` (string, optional): `"low_light" | "glare" | "blur" | "dirty_lens" | "unknown"`

## `vision.tamper_or_occlusion.v1`
Camera moved, lens covered, or view occluded.

Payload:
- `status`: `"ok" | "tampered" | "occluded"`
- `confidence` (number 0..1)


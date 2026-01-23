from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

EventType = Literal[
    "capture.camera_health.v1",
    "vision.motion_in_zone.v1",
    "vision.person_in_zone.v1",
    "vision.lighting_quality.v1",
    "vision.tamper_or_occlusion.v1",
]


class EventSource(BaseModel):
    service: str
    instance_id: str
    version: str | None = None


class HwEventV1(BaseModel):
    schema_version: Literal[1] = 1
    event_id: str
    type: EventType
    ts: datetime
    site_id: str | None = None
    camera_id: str | None = None
    source: EventSource
    correlation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    evidence: dict[str, Any] | None = None


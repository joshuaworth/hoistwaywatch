from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Severity = Literal["info", "warning", "critical"]


class ExplanationInput(BaseModel):
    name: str
    value: Any
    note: str | None = None


class AlertExplanation(BaseModel):
    rule_id: str
    why: str
    inputs: list[ExplanationInput] = Field(default_factory=list)


class AlertTrigger(BaseModel):
    event_ids: list[str]
    correlation_id: str | None = None


class AlertEvidence(BaseModel):
    frame_refs: list[str] = Field(default_factory=list)
    zone_overlay_ref: str | None = None


class HwAlertPacketV1(BaseModel):
    schema_version: Literal[1] = 1
    alert_id: str
    ts: datetime
    site_id: str | None = None
    camera_id: str | None = None
    severity: Severity
    hazard_score: float = Field(ge=0, le=100)
    summary: str
    recommended_action: str | None = None
    explanation: AlertExplanation
    trigger: AlertTrigger
    evidence: AlertEvidence | None = None
    debug: dict[str, Any] | None = None


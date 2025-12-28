from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import yaml

from hoistwaywatch.contracts.alerts import (
    AlertExplanation,
    AlertTrigger,
    ExplanationInput,
    HwAlertPacketV1,
)
from hoistwaywatch.contracts.events import HwEventV1


@dataclass(frozen=True)
class RuleMatch:
    rule_id: str
    severity: str
    hazard_score: float
    summary: str
    recommended_action: str | None
    why: str


class RulesEngine:
    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._rules: list[dict[str, Any]] = list(config.get("rules", []))

    @staticmethod
    def load_yaml(path: str) -> RulesEngine:
        with open(path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        if not isinstance(cfg, dict):
            raise ValueError("rules config must be a mapping")
        return RulesEngine(cfg)

    def evaluate(self, event: HwEventV1) -> list[HwAlertPacketV1]:
        alerts: list[HwAlertPacketV1] = []
        for rule in self._rules:
            match = self._match_rule(rule, event)
            if match is None:
                continue
            alerts.append(self._to_alert(match, event))
        return alerts

    def _match_rule(self, rule: dict[str, Any], event: HwEventV1) -> RuleMatch | None:
        rid = rule.get("id")
        when = rule.get("when", {})
        then = rule.get("then", {})
        if not rid or not isinstance(when, dict) or not isinstance(then, dict):
            return None

        if when.get("event_type") != event.type:
            return None

        # Common filters (simple, explainable)
        payload = event.payload or {}

        zone_id = when.get("zone_id")
        if zone_id is not None and payload.get("zone_id") != zone_id:
            return None

        status_in = when.get("status_in")
        if status_in is not None:
            status = payload.get("status")
            if status not in status_in:
                return None

        def _gte(field: str, key: str) -> bool:
            threshold = when.get(key)
            if threshold is None:
                return True
            try:
                return float(payload.get(field, 0)) >= float(threshold)
            except Exception:
                return False

        if not _gte("motion_score", "motion_score_gte"):
            return None
        if not _gte("confidence", "confidence_gte"):
            return None

        severity = then.get("severity", "warning")
        hazard_score = float(then.get("hazard_score", 50))
        summary = str(then.get("summary", rid))
        recommended_action = then.get("recommended_action")

        # Human-readable why (the “genius” part: trustable, auditable)
        why_parts: list[str] = [f"matched {rid}"]
        why_parts.append(f"type={event.type}")
        if "zone_id" in payload:
            why_parts.append(f"zone_id={payload.get('zone_id')}")
        if "motion_score" in payload:
            why_parts.append(f"motion_score={payload.get('motion_score')}")
        if "confidence" in payload:
            why_parts.append(f"confidence={payload.get('confidence')}")
        if "status" in payload:
            why_parts.append(f"status={payload.get('status')}")

        return RuleMatch(
            rule_id=rid,
            severity=severity,
            hazard_score=hazard_score,
            summary=summary,
            recommended_action=recommended_action,
            why=", ".join(why_parts),
        )

    def _to_alert(self, match: RuleMatch, event: HwEventV1) -> HwAlertPacketV1:
        now = datetime.now(UTC)
        return HwAlertPacketV1(
            alert_id=f"al_{uuid.uuid4().hex}",
            ts=now,
            site_id=event.site_id,
            camera_id=event.camera_id,
            severity=match.severity,  # type: ignore[arg-type]
            hazard_score=match.hazard_score,
            summary=match.summary,
            recommended_action=match.recommended_action,
            explanation=AlertExplanation(
                rule_id=match.rule_id,
                why=match.why,
                inputs=[
                    ExplanationInput(name="event_id", value=event.event_id),
                    ExplanationInput(name="event_type", value=event.type),
                    ExplanationInput(name="payload", value=event.payload),
                ],
            ),
            trigger=AlertTrigger(event_ids=[event.event_id], correlation_id=event.correlation_id),
        )


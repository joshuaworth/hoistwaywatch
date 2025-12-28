from __future__ import annotations

from datetime import UTC, datetime

from hoistwaywatch.contracts.events import HwEventV1
from hoistwaywatch.rules.engine import RulesEngine


def test_motion_in_car_path_triggers_alert(tmp_path) -> None:
    rules = tmp_path / "rules.yaml"
    rules.write_text(
        """\
version: 1
rules:
  - id: "R001.motion_in_car_path"
    when:
      event_type: "vision.motion_in_zone.v1"
      zone_id: "car_path"
      motion_score_gte: 0.15
      confidence_gte: 0.50
    then:
      severity: "critical"
      hazard_score: 90
      summary: "Motion detected in car path"
      recommended_action: "Stop."
""",
        encoding="utf-8",
    )

    engine = RulesEngine.load_yaml(str(rules))
    event = HwEventV1(
        event_id="evt_1",
        type="vision.motion_in_zone.v1",
        ts=datetime.now(UTC),
        site_id="site",
        camera_id="cam1",
        source={"service": "vision", "instance_id": "v1"},
        payload={"zone_id": "car_path", "motion_score": 0.2, "confidence": 0.8},
    )
    alerts = engine.evaluate(event)
    assert len(alerts) == 1
    assert alerts[0].severity == "critical"
    assert alerts[0].hazard_score == 90
    assert alerts[0].explanation.rule_id == "R001.motion_in_car_path"
    assert alerts[0].trigger.event_ids == ["evt_1"]


from __future__ import annotations

import argparse
import asyncio
import os
import sys

from hoistwaywatch.bus.nats_bus import NatsBus
from hoistwaywatch.contracts.events import HwEventV1
from hoistwaywatch.observability import get_logger, setup_logging
from hoistwaywatch.rules.engine import RulesEngine
from hoistwaywatch.util import wait_for_shutdown


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="hw-rules", description="HoistwayWatch rules service")
    p.add_argument("--nats", default=os.getenv("HW_NATS_URL", "nats://127.0.0.1:4222"))
    p.add_argument("--rules", default=os.getenv("HW_RULES_PATH", "configs/rules.yaml"))
    p.add_argument("--sub", default="hw.events.>")
    p.add_argument("--pub", default="hw.alerts.v1")
    p.add_argument("--queue", default="rules")
    return p.parse_args(argv)


async def _run(args: argparse.Namespace) -> int:
    setup_logging(service="rules")
    log = get_logger("hoistwaywatch.rules", service="rules")
    engine = RulesEngine.load_yaml(args.rules)
    bus = NatsBus(args.nats)
    await bus.connect()
    stop = wait_for_shutdown()

    async def on_event(msg: dict) -> None:
        try:
            event = HwEventV1.model_validate(msg)
        except Exception:
            # Fail-loud but keep service alive: ignore malformed payloads.
            log.warning("dropped invalid event")
            return
        alerts = engine.evaluate(event)
        for alert in alerts:
            await bus.publish_json(args.pub, alert.model_dump(mode="json"))
        if alerts:
            log.info("emitted alerts", extra={"count": len(alerts), "event_type": event.type})

    await bus.subscribe_json(args.sub, on_event, queue=args.queue)
    await stop.wait()
    log.info("shutting down")
    await bus.close()
    return 0


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    raise SystemExit(asyncio.run(_run(args)))


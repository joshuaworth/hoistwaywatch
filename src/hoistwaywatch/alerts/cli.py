from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime

from hoistwaywatch.bus.nats_bus import NatsBus
from hoistwaywatch.contracts.alerts import HwAlertPacketV1


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="hw-alerts", description="HoistwayWatch alerts service")
    p.add_argument("--nats", default=os.getenv("HW_NATS_URL", "nats://127.0.0.1:4222"))
    p.add_argument("--sub", default="hw.alerts.v1")
    p.add_argument(
        "--log",
        default=os.getenv("HW_ALERT_LOG", "alerts.ndjson"),
        help="Append alerts as NDJSON to this path.",
    )
    p.add_argument(
        "--exec",
        default=os.getenv("HW_ALERT_EXEC", ""),
        help="Optional shell command to execute on every alert (e.g. trigger siren/strobe).",
    )
    return p.parse_args(argv)


async def _run(args: argparse.Namespace) -> int:
    bus = NatsBus(args.nats)
    await bus.connect()

    async def on_alert(msg: dict) -> None:
        alert = HwAlertPacketV1.model_validate(msg)
        line = json.dumps(alert.model_dump(mode="json"), separators=(",", ":"), ensure_ascii=False)
        # stdout for operator visibility / journald
        print(line, flush=True)
        # durable local log
        with open(args.log, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        if args.exec:
            # keep it simple: delegate hardware to an explicit operator-provided command
            proc = await asyncio.create_subprocess_shell(
                args.exec,
                env={
                    **os.environ,
                    "HW_ALERT_SEVERITY": alert.severity,
                    "HW_ALERT_ID": alert.alert_id,
                },
            )
            await proc.wait()

    await bus.subscribe_json(args.sub, on_alert, queue="alerts")
    await asyncio.Event().wait()
    return 0


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    # touch log early with a header comment for human readers
    if args.log:
        with open(args.log, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts": datetime.now(UTC).isoformat(),
                        "note": "hoistwaywatch alerts log start",
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )
    raise SystemExit(asyncio.run(_run(args)))


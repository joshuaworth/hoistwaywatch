from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
import uuid
from datetime import UTC, datetime

import cv2

from hoistwaywatch.bus.nats_bus import NatsBus
from hoistwaywatch.observability import get_logger, setup_logging
from hoistwaywatch.util import wait_for_shutdown


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="hw-capture",
        description="HoistwayWatch capture health service",
    )
    p.add_argument("--nats", default=os.getenv("HW_NATS_URL", "nats://127.0.0.1:4222"))
    p.add_argument("--site-id", default=os.getenv("HW_SITE_ID", "site_default"))
    p.add_argument("--camera-id", default=os.getenv("HW_CAMERA_ID", "cam1"))
    p.add_argument(
        "--source",
        default=os.getenv("HW_CAMERA_SOURCE", "0"),
        help="OpenCV VideoCapture source (device index like 0, or RTSP URL).",
    )
    p.add_argument("--health-interval-sec", type=float, default=2.0)
    p.add_argument("--offline-after-sec", type=float, default=3.0)
    p.add_argument("--pub", default="hw.events.capture")
    return p.parse_args(argv)


def _open_capture(source: str) -> cv2.VideoCapture:
    # Numeric device index support
    if source.isdigit():
        return cv2.VideoCapture(int(source))
    return cv2.VideoCapture(source)


async def _run(args: argparse.Namespace) -> int:
    setup_logging(service="capture")
    log = get_logger("hoistwaywatch.capture", service="capture")
    bus = NatsBus(args.nats)
    await bus.connect()

    instance_id = f"capture-{uuid.uuid4().hex[:8]}"
    stop = wait_for_shutdown()

    cap = _open_capture(args.source)
    last_ok = time.time()
    last_health = 0.0

    try:
        while not stop.is_set():
            ok, frame = cap.read()

            now = time.time()
            if ok and frame is not None:
                last_ok = now
            else:
                # Attempt to reopen if source is unhealthy
                if now - last_ok >= args.offline_after_sec and (not cap.isOpened()):
                    log.warning("reopening camera source")
                    cap.release()
                    cap = _open_capture(args.source)

            # Publish health periodically (even if frames are OK, to provide heartbeat)
            if now - last_health >= args.health_interval_sec:
                age = now - last_ok
                if cap.isOpened() and age < args.offline_after_sec:
                    status = "ok"
                elif cap.isOpened():
                    status = "stalled"
                else:
                    status = "offline"

                evt = {
                    "schema_version": 1,
                    "event_id": f"evt_{uuid.uuid4().hex}",
                    "type": "capture.camera_health.v1",
                    "ts": datetime.now(UTC).isoformat(),
                    "site_id": args.site_id,
                    "camera_id": args.camera_id,
                    "source": {"service": "capture", "instance_id": instance_id},
                    "payload": {
                        "status": status,
                        "latency_ms": round(age * 1000.0),
                        "note": f"last_ok_age_sec={round(age, 3)}",
                    },
                }
                await bus.publish_json(args.pub, evt)
                last_health = now

            await asyncio.sleep(0)
    finally:
        cap.release()
        log.info("shutting down")
        await bus.close()


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    raise SystemExit(asyncio.run(_run(args)))


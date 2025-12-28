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
    p.add_argument("--interval-sec", type=float, default=2.0)
    p.add_argument("--pub", default="hw.events.capture")
    return p.parse_args(argv)


def _open_capture(source: str) -> cv2.VideoCapture:
    # Numeric device index support
    if source.isdigit():
        return cv2.VideoCapture(int(source))
    return cv2.VideoCapture(source)


async def _run(args: argparse.Namespace) -> int:
    bus = NatsBus(args.nats)
    await bus.connect()

    instance_id = f"capture-{uuid.uuid4().hex[:8]}"

    while True:
        start = time.time()
        cap = _open_capture(args.source)
        ok, frame = cap.read()
        cap.release()

        status = "ok" if ok and frame is not None else "offline"
        fps = None
        if ok:
            fps = None  # OpenCV doesn't provide reliable instantaneous FPS across sources

        evt = {
            "schema_version": 1,
            "event_id": f"evt_{uuid.uuid4().hex}",
            "type": "capture.camera_health.v1",
            "ts": datetime.now(UTC).isoformat(),
            "site_id": args.site_id,
            "camera_id": args.camera_id,
            "source": {"service": "capture", "instance_id": instance_id},
            "payload": {"status": status, "fps": fps},
        }
        await bus.publish_json(args.pub, evt)

        elapsed = time.time() - start
        await asyncio.sleep(max(0.0, args.interval_sec - elapsed))


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    raise SystemExit(asyncio.run(_run(args)))


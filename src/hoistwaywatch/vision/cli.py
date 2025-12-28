from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import cv2
import numpy as np

from hoistwaywatch.bus.nats_bus import NatsBus
from hoistwaywatch.observability import get_logger, setup_logging
from hoistwaywatch.util import wait_for_shutdown


@dataclass(frozen=True)
class Zone:
    zone_id: str
    polygon_norm: list[tuple[float, float]]


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="hw-vision",
        description="HoistwayWatch vision service (motion-in-zone)",
    )
    p.add_argument("--nats", default=os.getenv("HW_NATS_URL", "nats://127.0.0.1:4222"))
    p.add_argument("--site-id", default=os.getenv("HW_SITE_ID", "site_default"))
    p.add_argument("--camera-id", default=os.getenv("HW_CAMERA_ID", "cam1"))
    p.add_argument(
        "--source",
        default=os.getenv("HW_CAMERA_SOURCE", "0"),
        help="OpenCV VideoCapture source (device index like 0, or RTSP URL).",
    )
    p.add_argument("--zones", default=os.getenv("HW_ZONES_PATH", "configs/example-zones.json"))
    p.add_argument(
        "--motion-threshold",
        type=float,
        default=float(os.getenv("HW_MOTION_THRESHOLD", "0.15")),
    )
    p.add_argument(
        "--min-confidence",
        type=float,
        default=float(os.getenv("HW_MIN_CONFIDENCE", "0.5")),
    )
    p.add_argument("--publish-interval-ms", type=int, default=250)
    p.add_argument(
        "--occlusion-quality-lt",
        type=float,
        default=float(os.getenv("HW_OCCLUSION_Q_LT", "0.08")),
    )
    p.add_argument(
        "--occlusion-after-sec",
        type=float,
        default=float(os.getenv("HW_OCCLUSION_AFTER_SEC", "2.5")),
    )
    p.add_argument(
        "--tamper-diff-gt",
        type=float,
        default=float(os.getenv("HW_TAMPER_DIFF_GT", "0.25")),
    )
    p.add_argument(
        "--tamper-after-sec",
        type=float,
        default=float(os.getenv("HW_TAMPER_AFTER_SEC", "3.0")),
    )
    p.add_argument("--pub", default="hw.events.vision")
    return p.parse_args(argv)


def _open_capture(source: str) -> cv2.VideoCapture:
    if source.isdigit():
        return cv2.VideoCapture(int(source))
    return cv2.VideoCapture(source)


def _load_zones(path: str) -> list[Zone]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    zones = []
    for z in data.get("zones", []):
        zid = z["id"]
        poly = [(float(x), float(y)) for x, y in z["polygon"]]
        zones.append(Zone(zone_id=zid, polygon_norm=poly))
    return zones


def _zone_mask(frame_shape: tuple[int, int], zone: Zone) -> np.ndarray:
    h, w = frame_shape
    pts = np.array([[int(x * w), int(y * h)] for x, y in zone.polygon_norm], dtype=np.int32)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    return mask


def _lighting_quality(gray: np.ndarray) -> tuple[float, str | None]:
    # Extremely simple but field-useful: mean brightness & contrast proxy
    mean = float(np.mean(gray)) / 255.0
    std = float(np.std(gray)) / 255.0
    quality = max(0.0, min(1.0, (mean * 0.7 + std * 0.3)))
    reason = None
    if mean < 0.12:
        reason = "low_light"
    elif std < 0.05:
        reason = "blur"
    return quality, reason


async def _run(args: argparse.Namespace) -> int:
    setup_logging(service="vision")
    log = get_logger("hoistwaywatch.vision", service="vision")
    zones = _load_zones(args.zones)
    if not zones:
        raise SystemExit(f"no zones found in {args.zones}")

    bus = NatsBus(args.nats)
    await bus.connect()
    instance_id = f"vision-{uuid.uuid4().hex[:8]}"
    stop = wait_for_shutdown()

    cap = _open_capture(args.source)
    if not cap.isOpened():
        raise SystemExit("failed to open camera source")

    subtractor = cv2.createBackgroundSubtractorMOG2(
        history=200,
        varThreshold=16,
        detectShadows=False,
    )

    masks: dict[str, np.ndarray] = {}
    last_emit: dict[str, float] = {}
    ref_gray: np.ndarray | None = None
    bad_quality_since: float | None = None
    tamper_since: float | None = None

    try:
        while not stop.is_set():
            ok, frame = cap.read()
            if not ok or frame is None:
                await asyncio.sleep(0.2)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if ref_gray is None:
                ref_gray = gray.copy()
            h, w = gray.shape[:2]
            if not masks:
                for z in zones:
                    masks[z.zone_id] = _zone_mask((h, w), z)

            fg = subtractor.apply(frame)
            fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)[1]

            # Lighting quality affects confidence (uncertainty-aware)
            quality, reason = _lighting_quality(gray)

            now = time.time()
            # Publish lighting quality at ~1Hz
            if now - last_emit.get("_lighting", 0.0) >= 1.0:
                evt = {
                    "schema_version": 1,
                    "event_id": f"evt_{uuid.uuid4().hex}",
                    "type": "vision.lighting_quality.v1",
                    "ts": datetime.now(UTC).isoformat(),
                    "site_id": args.site_id,
                    "camera_id": args.camera_id,
                    "source": {"service": "vision", "instance_id": instance_id},
                    "payload": {"quality": round(quality, 3), "reason": reason},
                }
                await bus.publish_json(args.pub, evt)
                last_emit["_lighting"] = now

            # Occlusion / unusable view detection (fail-loud)
            if quality < args.occlusion_quality_lt:
                bad_quality_since = bad_quality_since or now
            else:
                bad_quality_since = None

            if (
                bad_quality_since is not None
                and (now - bad_quality_since) >= args.occlusion_after_sec
            ):
                if now - last_emit.get("_occlusion", 0.0) >= 1.0:
                    evt = {
                        "schema_version": 1,
                        "event_id": f"evt_{uuid.uuid4().hex}",
                        "type": "vision.tamper_or_occlusion.v1",
                        "ts": datetime.now(UTC).isoformat(),
                        "site_id": args.site_id,
                        "camera_id": args.camera_id,
                        "source": {"service": "vision", "instance_id": instance_id},
                        "payload": {
                            "status": "occluded",
                            "confidence": round(float(1.0 - quality), 3),
                        },
                    }
                    await bus.publish_json(args.pub, evt)
                    last_emit["_occlusion"] = now

            # Tamper detection (large persistent global change under decent visibility)
            if ref_gray is not None and quality >= 0.35:
                diff = cv2.absdiff(gray, ref_gray)
                diff_score = float(np.mean(diff)) / 255.0
                if diff_score > args.tamper_diff_gt:
                    tamper_since = tamper_since or now
                else:
                    tamper_since = None

                if tamper_since is not None and (now - tamper_since) >= args.tamper_after_sec:
                    if now - last_emit.get("_tamper", 0.0) >= 2.0:
                        evt = {
                            "schema_version": 1,
                            "event_id": f"evt_{uuid.uuid4().hex}",
                            "type": "vision.tamper_or_occlusion.v1",
                            "ts": datetime.now(UTC).isoformat(),
                            "site_id": args.site_id,
                            "camera_id": args.camera_id,
                            "source": {"service": "vision", "instance_id": instance_id},
                            "payload": {"status": "tampered", "confidence": round(diff_score, 3)},
                        }
                        await bus.publish_json(args.pub, evt)
                        last_emit["_tamper"] = now

            # Motion-in-zone
            for zone_id, mask in masks.items():
                zone_pixels = int(np.count_nonzero(mask))
                if zone_pixels == 0:
                    continue
                motion_pixels = int(np.count_nonzero(cv2.bitwise_and(fg, fg, mask=mask)))
                motion_score = motion_pixels / zone_pixels

                # Confidence penalized by low visibility
                confidence = max(0.0, min(1.0, quality))

                if motion_score >= args.motion_threshold and confidence >= args.min_confidence:
                    # Debounce per-zone (avoid flooding)
                    if now - last_emit.get(zone_id, 0.0) < (args.publish_interval_ms / 1000.0):
                        continue
                    evt = {
                        "schema_version": 1,
                        "event_id": f"evt_{uuid.uuid4().hex}",
                        "type": "vision.motion_in_zone.v1",
                        "ts": datetime.now(UTC).isoformat(),
                        "site_id": args.site_id,
                        "camera_id": args.camera_id,
                        "source": {"service": "vision", "instance_id": instance_id},
                        "payload": {
                            "zone_id": zone_id,
                            "motion_score": round(float(motion_score), 4),
                            "confidence": round(float(confidence), 4),
                        },
                    }
                    await bus.publish_json(args.pub, evt)
                    last_emit[zone_id] = now

            await asyncio.sleep(0)  # yield
    finally:
        cap.release()
        log.info("shutting down")
        await bus.close()


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    raise SystemExit(asyncio.run(_run(args)))


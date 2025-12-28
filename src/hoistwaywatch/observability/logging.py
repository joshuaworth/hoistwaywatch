from __future__ import annotations

import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Merge extra fields (best-effort)
        for k, v in record.__dict__.items():
            if k in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }:
                continue
            if k.startswith("_"):
                continue
            if k not in payload:
                payload[k] = v

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def setup_logging(*, service: str, level: str | None = None) -> None:
    lvl = (level or os.getenv("HW_LOG_LEVEL", "INFO")).upper()
    logging.basicConfig(
        level=getattr(logging, lvl, logging.INFO),
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    root = logging.getLogger()
    for h in root.handlers:
        h.setFormatter(_JsonFormatter())

    # Inject service name into all records via a LoggerAdapter-like pattern
    logging.getLogger("hoistwaywatch").info(
        "logging configured",
        extra={"service": service, "level": lvl},
    )


def get_logger(name: str, *, service: str) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logging.getLogger(name), {"service": service})


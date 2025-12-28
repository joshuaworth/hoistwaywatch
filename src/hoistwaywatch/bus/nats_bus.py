from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable

from nats.aio.client import Client as NATS


class NatsBus:
    def __init__(self, url: str, *, name: str = "hoistwaywatch") -> None:
        self._url = url
        self._nc = NATS()
        self._log = logging.getLogger(name)

    async def connect(self) -> None:
        async def _disconnected_cb() -> None:
            self._log.warning("nats disconnected")

        async def _reconnected_cb() -> None:
            self._log.info("nats reconnected", extra={"url": str(self._nc.connected_url)})

        async def _closed_cb() -> None:
            self._log.warning("nats connection closed")

        async def _error_cb(e: Exception) -> None:
            self._log.error("nats error", exc_info=e)

        await self._nc.connect(
            servers=[self._url],
            name="hoistwaywatch",
            allow_reconnect=True,
            reconnect_time_wait=1,
            max_reconnect_attempts=-1,
            disconnected_cb=_disconnected_cb,
            reconnected_cb=_reconnected_cb,
            closed_cb=_closed_cb,
            error_cb=_error_cb,
        )

    async def close(self) -> None:
        try:
            await self._nc.drain()
        finally:
            await self._nc.close()

    async def publish_json(self, subject: str, payload: dict) -> None:
        data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        await self._nc.publish(subject, data)

    async def subscribe_json(
        self,
        subject: str,
        handler: Callable[[dict], Awaitable[None]],
        *,
        queue: str | None = None,
    ) -> None:
        async def _on_msg(msg) -> None:  # nats callback signature
            body = json.loads(msg.data.decode("utf-8"))
            await handler(body)

        await self._nc.subscribe(subject, cb=_on_msg, queue=queue)


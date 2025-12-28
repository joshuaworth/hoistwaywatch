from __future__ import annotations

import json
from collections.abc import Awaitable, Callable

from nats.aio.client import Client as NATS


class NatsBus:
    def __init__(self, url: str) -> None:
        self._url = url
        self._nc = NATS()

    async def connect(self) -> None:
        await self._nc.connect(servers=[self._url])

    async def close(self) -> None:
        await self._nc.drain()

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


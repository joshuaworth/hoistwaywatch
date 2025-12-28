from __future__ import annotations

import asyncio
import signal
from collections.abc import Iterable


def wait_for_shutdown(
    signals: Iterable[signal.Signals] = (signal.SIGINT, signal.SIGTERM),
) -> asyncio.Event:
    """
    Return an asyncio.Event that gets set on SIGINT/SIGTERM.
    Works on Linux (field devices) and degrades gracefully elsewhere.
    """
    stop = asyncio.Event()
    loop = asyncio.get_event_loop()

    def _set() -> None:
        stop.set()

    for s in signals:
        try:
            loop.add_signal_handler(s, _set)
        except NotImplementedError:
            # Windows / limited event loops
            signal.signal(s, lambda *_: _set())
        except RuntimeError:
            # Called outside running loop; caller can still await stop manually.
            pass

    return stop


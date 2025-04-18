import asyncio
import threading
from typing import Coroutine


class AsyncDispatcher:
    def __init__(self) -> None:
        self._async_event_loop = asyncio.new_event_loop()
        threading.Thread(target=self._start_event_loop, daemon=True).start()

    def schedule_async_to_thread(self, coro: Coroutine) -> None:
        asyncio.run_coroutine_threadsafe(coro, self._async_event_loop)

    def _start_event_loop(self) -> None:  # This method must be called from a worker thread
        asyncio.set_event_loop(self._async_event_loop)
        self._async_event_loop.run_forever()

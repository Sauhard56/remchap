import asyncio
import threading
from typing import Coroutine

import customtkinter


class BaseWindow(customtkinter.CTk):

    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.__async_event_loop = asyncio.new_event_loop()

        threading.Thread(target=self.__start_event_loop, daemon=True).start()

    def _schedule_async_to_thread(self, coro: Coroutine) -> None:
        "**Important**: Use `self.after` to modify GUI controls."

        asyncio.run_coroutine_threadsafe(coro, self.__async_event_loop)

    def __start_event_loop(self) -> None:  # This method must be called from a worker thread
        asyncio.set_event_loop(self.__async_event_loop)
        self.__async_event_loop.run_forever()

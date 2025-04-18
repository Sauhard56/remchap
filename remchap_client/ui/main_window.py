import customtkinter

from .startup_window import StartupWindow
from .helper import AsyncDispatcher


class MainWindow(customtkinter.CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.withdraw() # Hide the window

        self.dispatcher = AsyncDispatcher()
        self.startup_wnd = StartupWindow(self, self.dispatcher)
        self.startup_wnd.on_close(self._after_startup_closed)

    def _after_startup_closed(self) -> None:
        client = self.startup_wnd.client
        if client is None:
            self.destroy()
            return

        self.destroy() # Just for now...

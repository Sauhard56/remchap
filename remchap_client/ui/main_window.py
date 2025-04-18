import customtkinter

from .connection_window import ConnectionWindow
from .helper import AsyncDispatcher


class MainWindow(customtkinter.CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.withdraw() # Hide the window

        self.dispatcher = AsyncDispatcher()
        self.connection_wnd = ConnectionWindow(self, self.dispatcher)
        self.connection_wnd.on_close(self._after_startup_closed)

    def _after_startup_closed(self) -> None:
        client = self.connection_wnd.client
        if client is None:
            self.destroy()
            return

        self.destroy() # Just for now...

from typing import Callable

import customtkinter


class TopLevelBase(customtkinter.CTkToplevel):
    def on_close(self, cb: Callable):
        self.protocol("WM_DELETE_WINDOW", cb)

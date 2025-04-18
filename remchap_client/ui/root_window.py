import customtkinter

from .startup_window import StartupWindow


class RootWindow(customtkinter.CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.withdraw() # Hide the window

    def main(self) -> None:
        try:
            startup_wnd = StartupWindow(self)
            startup_wnd.mainloop()
        finally:
            self.destroy()

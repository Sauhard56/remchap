from .base_window import BaseWindow


class MainWindow(BaseWindow):
    def __init__(self) -> None:
        super().__init__()

        self.title("Remchap")
        self.geometry("1024x640")

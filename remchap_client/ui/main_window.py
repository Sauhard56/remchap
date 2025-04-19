import random

import customtkinter

# from .connection_window import ConnectionWindow
from .helper import AsyncDispatcher
from .connection_window import ConnectionWindow


class MainWindow(customtkinter.CTk):
    def __init__(self, fg_color = None, **kwargs):
        customtkinter.set_appearance_mode("dark")

        super().__init__(fg_color, **kwargs)

        self._dispatcher = AsyncDispatcher()

        self.title("Remchap")
        self.geometry("1024x612")
        self.minsize(612, 306)
        self.withdraw() # Hide the window

        chatframe = ChatFrame(self)
        chatframe.pack(fill="both", expand=True)

        self._connection_wnd = ConnectionWindow(self, self._dispatcher)
        self._connection_wnd.on_close(self._after_startup_closed)

    def _after_startup_closed(self) -> None:
        client = self._connection_wnd.client
        if client is None:
            self.destroy()
            return


class ChatFrame(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTk, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        # Message box and button
        self.message_entry = customtkinter.CTkEntry(self, height=40,
                                               placeholder_text="Enter message...",
                                               font=customtkinter.CTkFont(size=14))
        send_button = customtkinter.CTkButton(self, text="Send", width=40, height=40,
                                              corner_radius=20, command=self._send_button_callback)

        self.message_entry.bind("<Return>", lambda _: (send_button.invoke(), send_button.focus()))
        send_button.bind("<Key>", lambda e: (self.message_entry.focus(),
                                             self.message_entry.insert("end", e.char)))

        self.message_entry.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        send_button.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 5))

        self.message_listframe = customtkinter.CTkScrollableFrame(self)
        self.message_listframe.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

    def _send_button_callback(self) -> None:
        if not (message := self.message_entry.get().strip()):
            return

        # TODO: add send message logic

        self.after(0, lambda: self.message_entry.delete(0, customtkinter.END))

    def _add_message_to_list(self, message_frame: "MessageFrame") -> None:
        message_frame.pack(anchor="w", fill="x", pady=2)

        # Scroll to bottom
        self.after(1, lambda: self.message_listframe._parent_canvas.yview_moveto(1.0)) # pylint: disable=protected-access

class MessageFrame(customtkinter.CTkFrame):
    _prev_color = None

    def __init__(self, master, name: str, message: str, **kwargs) -> None:
        super().__init__(master, fg_color="#1A1A1E", **kwargs)

        while True:
            name_color = random.choice((
                "red", "gold", "green2", "cornflower blue", "khaki1", "blue violet"
            ))

            if not name_color == self._prev_color:
                MessageFrame._prev_color = name_color
                break

        name_label = customtkinter.CTkLabel(self, height=1, text=name, text_color=name_color,
                                            font=customtkinter.CTkFont("Ariel", 12, "bold"))
        message_label = customtkinter.CTkLabel(self, height=1, text=message, justify="left")
        message_label.bind('<Configure>', lambda e: message_label.configure(
            wraplength=message_label.winfo_width()))

        name_label.pack(anchor="w", padx=12)
        message_label.pack(anchor="w", padx=12)

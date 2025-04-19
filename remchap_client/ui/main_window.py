import json
import random
import asyncio
from tkinter import messagebox

import customtkinter

from .helper import AsyncDispatcher
from .connection_window import ConnectionWindow
from ..networking import Client


class MainWindow(customtkinter.CTk):
    def __init__(self, fg_color = None, **kwargs):
        customtkinter.set_appearance_mode("dark")

        super().__init__(fg_color, **kwargs)

        self._dispatcher = AsyncDispatcher()
        self._client: Client = None

        self.title("Remchap")
        self.geometry("1024x612")
        self.minsize(612, 306)
        self.withdraw() # Hide the window

        self._chatframe = ChatFrame(self, self._dispatcher)
        self._chatframe.pack(fill="both", expand=True)

        self._connection_wnd = ConnectionWindow(self, self._dispatcher)
        self._connection_wnd.on_close(self._after_connection_wnd_closed)

    def _after_connection_wnd_closed(self) -> None:
        client = self._connection_wnd.client
        if client is None:
            self.destroy()
            return

        self._client = client
        self._chatframe.set_client(client)
        self.deiconify()
        self._dispatcher.schedule_async_to_thread(self._client_keepalive())
        self._dispatcher.schedule_async_to_thread(self._client_start_reading())

    async def _client_keepalive(self) -> None:
        # Keep the client alive by sending timed pings
        while self._client.connected:
            json_encoded = json.dumps({"type" : "ping"}).encode()

            payload = len(json_encoded).to_bytes(4, "big")
            payload += json_encoded

            await self._client.write(payload)
            await asyncio.sleep(3) # Every 3 seconds

    async def _client_start_reading(self) -> None:
        try:
            strikes = 0
            while self._client and self._client.connected and strikes < 3:
                buffer = bytearray()
                while len(buffer) < 4:
                    bytes_read = await self._client.read(4 - len(buffer))
                    if not bytes_read:
                        return
                    buffer.extend(bytes_read)

                try:
                    payload_size = int.from_bytes(buffer, "big")
                except ValueError:
                    print("Server sent invalid bytes...")
                    strikes += 1
                    continue

                buffer.clear()

                while len(buffer) < payload_size:
                    bytes_read = await self._client.read(payload_size - len(buffer))
                    if not bytes_read:
                        return
                    buffer.extend(bytes_read)

                try:
                    content = buffer.decode()
                    parsed: dict[str] = json.loads(content)

                    assert parsed.get("message")
                except (UnicodeDecodeError, AssertionError, json.JSONDecodeError):
                    print("Server sent invalid bytes...")
                    strikes += 1
                    continue

                self.after(0, lambda: self._chatframe.add_message_to_list(parsed.get("name"),
                                                                        parsed.get("message")))
        finally:
            messagebox.showinfo("Disconnected", "Disconnected from the server! Exiting...")
            self.after(0, self.destroy)

class ChatFrame(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTk, dispatcher: AsyncDispatcher, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self._client: Client = None
        self._dispatcher = dispatcher

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
                                             self.message_entry.insert("end", e.char))
                                             if e.char.isprintable() else None)

        self.message_entry.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        send_button.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 5))

        self.message_listframe = customtkinter.CTkScrollableFrame(self)
        self.message_listframe.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

    def _send_button_callback(self) -> None:
        if not (message := self.message_entry.get().strip()):
            return

        if len(message) > 2000:
            messagebox.showerror("Message Too Large",
                                "Your message exceeds text limit of 2000 characters.")
            return

        if self._client and self._client.connected:
            json_encoded = json.dumps({"message" : message, "type" : "message"}).encode()

            payload = len(json_encoded).to_bytes(4, "big")
            payload += json_encoded

            self._dispatcher.schedule_async_to_thread(self._client.write(payload))

        self.after(0, lambda: self.message_entry.delete(0, customtkinter.END))

    def add_message_to_list(self, name: str | None, message: str) -> None:
        message_frame = MessageFrame(self.message_listframe, name, message)
        message_frame.pack(anchor="w", fill="x", pady=2)

        # Scroll to bottom
        self.after(1, lambda: self.message_listframe._parent_canvas.yview_moveto(1.0)) # pylint: disable=protected-access

    def set_client(self, client: Client) -> None:
        self._client = client

class MessageFrame(customtkinter.CTkFrame):
    _prev_color = None

    def __init__(self, master, name: str | None, message: str, **kwargs) -> None:
        super().__init__(master, fg_color="#1A1A1E", **kwargs)

        while True:
            name_color = random.choice((
                "red", "gold", "green2", "cornflower blue", "khaki1", "blue violet"
            ))

            if not name_color == self._prev_color:
                MessageFrame._prev_color = name_color
                break

        if name:
            message_color = None
        else:
            # Server message
            message_color = "cyan"
            name = "[Server]"
            name_color = "orange"

        name_label = customtkinter.CTkLabel(self, height=1, text=name, text_color=name_color,
                                            font=customtkinter.CTkFont("Arial", 12, "bold"))
        message_label = customtkinter.CTkLabel(self, height=1, text=message,
                                               justify="left", text_color=message_color)
        message_label.bind('<Configure>', lambda e: message_label.configure(
            wraplength=message_label.winfo_width()))

        name_label.pack(anchor="w", padx=12)
        message_label.pack(anchor="w", padx=12)

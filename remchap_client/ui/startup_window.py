from ipaddress import ip_address
from tkinter import messagebox

import customtkinter

from .base_window import BaseWindow
from ..networking import Client


class StartupWindow(BaseWindow):
    def __init__(self):
        super().__init__()

        self._client = None

        self.title("Remchap - Connect")
        self.geometry("320x200")
        self.resizable(False, False)

        self._host_var = customtkinter.StringVar(self, "127.0.0.1")
        self._port_var = customtkinter.StringVar(self, "8080")

        host_label = customtkinter.CTkLabel(self, text="Hostname/IP Address:", anchor="w")
        host_label.pack(fill="both", padx=20)

        host_entry = customtkinter.CTkEntry(self, textvariable=self._host_var)
        host_entry.pack(fill="both", padx=20)

        port_label = customtkinter.CTkLabel(self, text="Port:", anchor="w")
        port_label.pack(fill="both", padx=20, pady=(10, 0))

        port_entry = customtkinter.CTkEntry(self, textvariable=self._port_var)
        port_entry.pack(fill="both", padx=20)

        connect_button = customtkinter.CTkButton(
            self,
            text="Connect",
            command=lambda: self._schedule_async_to_thread(
                self._connect_button_callback()
            )
        )
        connect_button.pack(pady=(30, 0))

        # Enter key callbacks
        host_entry.bind("<Return>", lambda _: self.port_entry.focus())
        port_entry.bind("<Return>", lambda _: (self.focus(), connect_button.invoke()))

    async def _connect_button_callback(self) -> None:
        host = self._host_var.get()
        try:
            _ = ip_address(host)
            port = int(self._port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid host or port")
            return

        if not 1 <= port <= 65535:
            messagebox.showerror("Error", "Port out of range (1 - 65535)")
            return

        try:
            client = Client()
            await client.connect(host, port)
        except ConnectionRefusedError:
            messagebox.showerror("Connection error", "Unable to connect to host")
            return

        self._client = client
        self.after(0, self.destroy)

    @property
    def client(self) -> Client | None:
        return self._client

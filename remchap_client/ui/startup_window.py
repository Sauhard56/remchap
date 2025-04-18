from tkinter import messagebox

import customtkinter

from .helper import AsyncDispatcher
from .toplevel_base import TopLevelBase
from ..networking import Client


class StartupWindow(TopLevelBase):
    def __init__(self, root: customtkinter.CTk, dispatcher: AsyncDispatcher):
        super().__init__(root)

        self._client = None

        self.title("Remchap - Connect")
        self.geometry("320x200")
        self.resizable(False, False)

        self._host_var = customtkinter.StringVar(self, "127.0.0.1")
        self._port_var = customtkinter.StringVar(self, "8080")

        host_label = customtkinter.CTkLabel(self, text="Hostname/IP Address:", anchor="w")
        host_label.pack(fill="both", padx=20)

        self._host_entry = customtkinter.CTkEntry(self, textvariable=self._host_var)
        self._host_entry.pack(fill="both", padx=20)

        port_label = customtkinter.CTkLabel(self, text="Port:", anchor="w")
        port_label.pack(fill="both", padx=20, pady=(10, 0))

        self._port_entry = customtkinter.CTkEntry(self, textvariable=self._port_var)
        self._port_entry.pack(fill="both", padx=20)

        self._connect_button = customtkinter.CTkButton(
            self,
            text="Connect",
            command=lambda: dispatcher.schedule_async_to_thread(
                self._connect_button_callback()))
        self._connect_button.pack(pady=(30, 0))

        # Enter key callbacks
        self._host_entry.bind("<Return>", lambda _: self._port_entry.focus())
        self._port_entry.bind("<Return>", lambda _: (self.focus(), self._connect_button.invoke()))

    async def _connect_button_callback(self) -> None:
        self._host_entry.configure(state="disabled")
        self._port_entry.configure(state="disabled")
        self._connect_button.configure(state="disabled")

        try:
            host = self._host_var.get()
            try:
                port = int(self._port_var.get())
            except ValueError:
                messagebox.showerror("Parsing Error", "Invalid port.")
                return

            if not 1 <= port <= 65535:
                messagebox.showerror("Parsing Error", "Port out of range (1 - 65535).")
                return

            try:
                client = Client()
                await client.connect(host, port, timeout=5.0)
            except ConnectionRefusedError:
                messagebox.showerror("Connection Error", "Unable to connect to host.")
                return
            except TimeoutError:
                messagebox.showerror("Connection Error",
                                     "Connection timed out (took longer than 5.0s).")
                return
        finally:
            self._host_entry.configure(state="normal")
            self._port_entry.configure(state="normal")
            self._connect_button.configure(state="normal")

        self._client = client
        self.after(0, self.destroy)

    @property
    def client(self) -> Client | None:
        return self._client

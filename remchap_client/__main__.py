import asyncio

from .ui import MainWindow, StartupWindow


async def main() -> None:
    startup_wnd = StartupWindow()
    startup_wnd.mainloop()

    client = startup_wnd.client

    if not client:
        return

    app = MainWindow()
    app.mainloop() # Start the UI


asyncio.run(main())

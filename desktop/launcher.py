"""AgentOS Windows desktop shell. v0.1 is LOCAL ONLY and has no user auth."""
import os
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

def frontend_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "frontend"
    return Path(__file__).resolve().parents[1] / "apps" / "web" / "out"

def reserve_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]

def main() -> None:
    local_data = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share")))
    os.environ.setdefault("AGENTOS_DB_PATH", str(local_data / "AgentOS" / "state.sqlite3"))

    import uvicorn
    import webview
    from fastapi.staticfiles import StaticFiles
    from agentos.main import app

    web_files = frontend_path()
    if not (web_files / "index.html").is_file():
        raise RuntimeError("AgentOS web interface was not included in this build.")
    app.mount("/", StaticFiles(directory=str(web_files), html=True), name="web")

    port = reserve_local_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    address = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            if not thread.is_alive():
                raise RuntimeError("AgentOS API stopped before the UI could start.")
            try:
                with urlopen(address + "/healthz", timeout=0.3) as response:
                    if response.status == 200:
                        break
            except (OSError, URLError):
                time.sleep(0.1)
        else:
            raise RuntimeError("Timed out starting the AgentOS local API.")
        webview.create_window("AgentOS", address, width=1420, height=900, min_size=(900, 640))
        webview.start()
    finally:
        server.should_exit = True
        thread.join(timeout=8)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, str(exc), "AgentOS failed to start", 0x10)
        else:
            raise

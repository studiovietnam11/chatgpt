"""Windows desktop launcher for FoxProfile Studio.

All stages are logged before the Flet UI is started. A fatal startup failure
is presented through a native Windows dialog, never silently swallowed by
PyInstaller's --windowed subsystem.
"""
from __future__ import annotations

import faulthandler
import logging
import os
import sys
import time
import traceback
from pathlib import Path


def app_root() -> Path:
    return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "FoxProfileStudio"


def log_file() -> Path:
    p = app_root() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p / "startup-latest.log"


def note(message: str) -> None:
    with log_file().open("a", encoding="utf-8") as h:
        h.write(time.strftime("%Y-%m-%d %H:%M:%S") + " " + message + "\n")


def show_fatal(message: str) -> None:
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, message, "FoxProfile Studio - Loi khoi dong", 0x10)
            return
        except Exception:
            pass
    print(message, file=sys.__stderr__)


def configure() -> Path:
    root = app_root()
    root.mkdir(parents=True, exist_ok=True)
    (root / "profiles").mkdir(exist_ok=True)
    (root / "logs").mkdir(exist_ok=True)
    os.environ.setdefault("FOXPROFILE_PROFILES_FILE", str(root / "profiles.json"))
    os.environ.setdefault("FOXPROFILE_DATA_DIR", str(root / "profiles"))
    os.environ.setdefault("FOXPROFILE_LOG_DIR", str(root / "logs"))
    os.environ.setdefault("FOXPROFILE_LANG", "vi")
    os.environ.setdefault("FOXPROFILE_API_HOST", "127.0.0.1")
    if getattr(sys, "frozen", False):
        runtime = Path(sys.executable).resolve().parent / "browser-runtime"
        if not runtime.is_dir():
            raise FileNotFoundError("Thieu du lieu Camoufox: " + str(runtime))
        import camoufox.pkgman as pkgman
        pkgman.INSTALL_DIR = runtime
        note("browser-runtime present")
    return root


def main() -> None:
    # PyInstaller --windowed sets stdout/stderr to None. Uvicorn assumes an isatty() stream.
    if sys.stdout is None:
        sys.stdout = log_file().open("a", encoding="utf-8", buffering=1)
    if sys.stderr is None:
        sys.stderr = log_file().open("a", encoding="utf-8", buffering=1)
    note("START argv=" + repr(sys.argv[1:]) + " executable=" + sys.executable)
    note("Windows=" + os.name + " frozen=" + str(getattr(sys, "frozen", False)))
    with log_file().open("a", encoding="utf-8") as h:
        try:
            faulthandler.enable(file=h)
        except Exception:
            pass
        root = configure()
        note("configuration complete")
        if "--self-test" in sys.argv:
            from src.api.app import _PANEL
            from src.ui.theme.page import ASSETS_DIR
            from src.ui.app import App
            from camoufox.async_api import AsyncCamoufox
            if not _PANEL.exists() or not (Path(ASSETS_DIR) / "icon.png").exists():
                raise RuntimeError("Missing packaged web/assets")
            note("IMPORT_SELF_TEST_OK")
            print("GUI_OK", flush=True)
            return

        if "--smoke-desktop" in sys.argv:
            # Don't collide with desktop instances on CI test runners.
            os.environ["FOXPROFILE_API_PORT"] = "18765"
            os.environ["FOXPROFILE_PROFILES_FILE"] = str(root / "smoke-profiles.json")
            os.environ["FOXPROFILE_DATA_DIR"] = str(root / "smoke-data")
        note("about to import application startup")
        from src.main import main as run_app
        note("about to start FastAPI and Flet desktop")
        run_app()
        note("UI_EXITED_NORMALLY")


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        err = traceback.format_exc()
        try:
            note("FATAL_EXCEPTION\n" + err)
        except Exception:
            pass
        if "--self-test" not in sys.argv:
            show_fatal("FoxProfile khong khoi dong duoc.\n\n"
                       "Loi da luu tai:\n" + str(log_file()) + "\n\n"
                       "Mo file nay va gui noi dung de sua loi.\n\n" + err[-700:])
        raise SystemExit(1)

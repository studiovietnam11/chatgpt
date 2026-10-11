"""Isolated Windows console runner preserving the browser stdout protocol."""
from __future__ import annotations
import os
import sys
import asyncio
import traceback
from pathlib import Path

def prepare():
    if not getattr(sys, "frozen", False):
        return
    root = Path(sys.executable).resolve().parent
    if root.name.lower() == "worker":
        root = root.parent
    browser = root / "browser-runtime"
    if not browser.is_dir():
        raise FileNotFoundError("Missing browser-runtime at " + str(browser))
    import camoufox.pkgman as pkgman
    pkgman.INSTALL_DIR = browser

def main():
    prepare()
    args = sys.argv[1:]
    if args == ["--self-test"]:
        from src.services.browser import runner
        from chrome_engine import runner as chrome_runner
        print("WORKER_OK", flush=True)
        return 0
    if len(args) < 4 or args[0] not in ("--camoufox", "--chrome"):
        print("Invalid browser-worker command", flush=True)
        return 2
    engine = args[0]
    sys.argv = [sys.argv[0], *args[1:]]
    if engine == "--chrome":
        from chrome_engine.runner import main as chrome_main
        return chrome_main()
    from src.services.browser.runner import _async_main, _configure_stdio
    _configure_stdio()
    return asyncio.run(_async_main())

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)

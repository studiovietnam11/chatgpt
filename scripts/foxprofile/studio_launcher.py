"""Windows frozen desktop launcher, FoxProfile Studio."""
from __future__ import annotations
import os
import sys
import traceback
from pathlib import Path

def configure():
    base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    root = base / "FoxProfileStudio"
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
            raise FileNotFoundError("Camoufox runtime is missing: " + str(runtime))
        import camoufox.pkgman as pkgman
        pkgman.INSTALL_DIR = runtime
    return root

def main():
    configure()
    if "--self-test" in sys.argv:
        from src.api.app import _PANEL
        from src.ui.theme.page import ASSETS_DIR
        from src.ui.app import App
        from camoufox.async_api import AsyncCamoufox
        if not _PANEL.exists() or not (Path(ASSETS_DIR) / "icon.png").exists():
            raise RuntimeError("Missing packaged web/assets")
        print("GUI_OK", flush=True)
        return
    from src.main import main as run_app
    run_app()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        try:
            base = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "FoxProfileStudio" / "logs"
            base.mkdir(parents=True, exist_ok=True)
            (base / "startup-error.log").write_text(traceback.format_exc(), encoding="utf-8")
        except OSError:
            pass
        traceback.print_exc()
        raise SystemExit(1)

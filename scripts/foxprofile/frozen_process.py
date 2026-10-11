"""Browser subprocess launcher for normal Python and frozen Windows distribution."""
import os
import pathlib
import subprocess
import sys
from collections.abc import Callable
from ...core.logging import get_logger
from ...models.profile import Profile
from . import display

logger = get_logger("browser.process")
_PROJECT_ROOT = str(pathlib.Path(__file__).parents[3])

def runner_command(profile: Profile) -> list[str]:
    if getattr(sys, "frozen", False):
        worker_exe = pathlib.Path(sys.executable).resolve().parent / "worker" / "FoxProfileWorker.exe"
        if not worker_exe.is_file():
            raise FileNotFoundError(f"Missing profile worker: {worker_exe}")
        runner = [str(worker_exe), "--chrome" if profile.engine == "chrome" else "--camoufox"]
    elif profile.engine == "chrome":
        runner = [sys.executable, "-m", "chrome_engine.runner"]
    else:
        runner = [sys.executable, str(pathlib.Path(__file__).parent / "runner.py")]
    return [*runner, profile.name, str(profile.proxy), profile.os_type, profile.timezone or "", profile.locale or ""]

def spawn_browser(profile: Profile) -> subprocess.Popen:
    env = os.environ.copy()
    previous = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = _PROJECT_ROOT + (os.pathsep + previous if previous else "")
    return subprocess.Popen(runner_command(profile),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=pathlib.Path.cwd(), env=env, text=True, encoding="utf-8",
        errors="replace", bufsize=1)

def terminate(proc: subprocess.Popen, name: str, timeout: int = 5) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
        try:
            proc.wait(timeout=timeout)
            logger.info("Browser %s terminated gracefully", name)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=1)
            logger.warning("Browser %s force killed", name)
    except Exception as exc:
        logger.exception("Failed terminating %s: %s", name, exc)
    finally:
        cleanup(proc)

def cleanup(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        display.stop_for_runner(proc.pid)

def wait_for_exit(proc: subprocess.Popen, name: str, notify_stopped: Callable[[], None]) -> None:
    try:
        proc.wait()
    except Exception as exc:
        logger.exception("Browser wait %s failed: %s", name, exc)
    finally:
        cleanup(proc)
        notify_stopped()

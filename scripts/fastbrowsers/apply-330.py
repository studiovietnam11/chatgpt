"""FASTBROWSERS 3.3.0 source migration: persist session, compare browser environment."""
from pathlib import Path
root=Path("app")
def edit(rel,old,new):
 p=root/rel
 text=p.read_text(encoding="utf-8")
 if old not in text:
  raise RuntimeError(f"Missing expected code in {rel}: {old[:100]}")
 p.write_text(text.replace(old,new),encoding="utf-8")

edit("src/services/browser/control.py","import base64\n","import asyncio\nimport base64\n")
edit("src/services/browser/control.py","def __init__(self, context: Any) -> None:\n        self._context = context",
"""def __init__(self, context: Any, shutdown_event: asyncio.Event | None = None) -> None:
        self._shutdown_event = shutdown_event
        self._context = context""")
edit("src/services/browser/control.py","    async def environment(self) -> dict[str, Any]:",
"""    async def save_and_close(self) -> dict[str, Any]:
        # A Windows process kill prevents Firefox and Chromium from committing
        # the profile's cookies and session state to disk.
        if self._shutdown_event is None:
            raise ControlError("Graceful shutdown unavailable")
        asyncio.get_running_loop().call_later(0.3, self._shutdown_event.set)
        return {"accepted": True, "persistence_pending": True}

    async def environment(self) -> dict[str, Any]:""")
edit("src/services/browser/control.py","    ACTIONS = (\n","    ACTIONS = (\n        \"save_and_close\",\n")
edit("src/services/browser/control.py","async def serve(context: Any) -> tuple[web.AppRunner, int, str]:","async def serve(context: Any, shutdown_event: asyncio.Event | None = None) -> tuple[web.AppRunner, int, str]:")
edit("src/services/browser/control.py","build_app(PageController(context), token)","build_app(PageController(context, shutdown_event), token)")
edit("src/services/browser/control.py","                cpu: navigator.hardwareConcurrency || null,\n                screen:","                cpu: navigator.hardwareConcurrency || null,\n                memory: navigator.deviceMemory || null,\n                vendor: navigator.vendor || '',\n                pixelRatio: window.devicePixelRatio || null,\n                colorDepth: screen.colorDepth || null,\n                screen:")

for file in ("src/services/browser/runner.py","chrome_engine/runner.py"):
 edit(file,"os.path.join(os.getcwd(), DATA_DIR, profile_name)","os.path.join(DATA_DIR, profile_name)")
 edit(file,"control.serve(context)","control.serve(context, _shutdown)")

edit("chrome_engine/branded_runner.py","            server,port,token=await control.serve(context)","            shutdown=asyncio.Event()\n            server,port,token=await control.serve(context,shutdown)")
edit("chrome_engine/branded_runner.py","                await close.wait()",'''                closing=asyncio.create_task(close.wait())
                stopping=asyncio.create_task(shutdown.wait())
                try:
                    await asyncio.wait([closing,stopping],return_when=asyncio.FIRST_COMPLETED)
                finally:
                    for task in (closing,stopping):
                        if not task.done():task.cancel()
                    await asyncio.gather(closing,stopping,return_exceptions=True)
                if RESTORE_TABS:
                    session.save(str(data_dir),[p.url for p in context.pages if not p.is_closed()])''')

file="src/services/browser/launcher.py"
p=root/file
s=p.read_text(encoding="utf-8")
a=s.index("    def shutdown_all(self) -> None:")
b=s.index("    def start_thread(",a)
s=s[:a]+'''    def shutdown_all(self) -> None:
        # No process waits or network calls under the session lock.
        with self._lock:
            names=list(self._active_sessions)
        for name in names:
            self.stop_profile(name,timeout=15)
        logger.info("All browser sessions shut down")

'''+s[b:]
a=s.index("    def stop_profile(self, profile_name: str, timeout: int = 2) -> bool:")
b=s.index("    def control(",a)
s=s[:a]+'''    def stop_profile(self, profile_name: str, timeout: int = 15) -> bool:
        """Flush persistent browser profile, then exit worker; kill only on timeout."""
        with self._lock:
            proc=self._active_sessions.get(profile_name)
            endpoint=self._controls.get(profile_name)
        if proc is None:
            return False
        if proc.poll() is None and endpoint:
            try:
                reply=self.control(profile_name,"save_and_close",timeout=4)
                if not reply.get("accepted"):
                    raise RuntimeError("Shutdown not accepted")
                proc.wait(timeout=timeout)
                logger.info("Saved persistent session on close: %s",profile_name)
            except (BrowserControlError,subprocess.TimeoutExpired,OSError,RuntimeError,ValueError) as exc:
                logger.warning("Clean shutdown failed for %s: %s",profile_name,exc)
                terminate(proc,profile_name,timeout=3)
        elif proc.poll() is None:
            terminate(proc,profile_name,timeout=3)
        with self._lock:
            if self._active_sessions.get(profile_name) is proc:
                self._active_sessions.pop(profile_name,None)
                notify=self._stop_notifiers.pop(profile_name,None)
                self._controls.pop(profile_name,None)
            else:
                notify=None
        if notify:
            notify.set()
        return True

'''+s[b:]
old='''                if msg == "BROWSER_CLOSED":
                    logger.info("Browser close detected for profile: %s", name)
                    notify_stopped()
                    terminate(proc, name, timeout=1)
                    continue'''
if old not in s:raise RuntimeError("BROWSER_CLOSED block mismatch")
s=s.replace(old,'''                if msg == "BROWSER_CLOSED":
                    # Browser still needs to commit cookies. Never hard-kill here.
                    logger.info("Browser closed for %s; waiting for clean exit",name)
                    continue''')
p.write_text(s,encoding="utf-8")
edit("src/services/browser/process.py","cwd=pathlib.Path.cwd(),",'cwd=pathlib.Path(os.environ.get("FOXPROFILE_DATA_DIR") or pathlib.Path.cwd()).resolve().parent,')

(root/"src/services/browser/environment_check.py").write_text('''"""Verify requested settings against JavaScript-visible measurements."""
def compare(settings,os_type,engine,observation):
    checks={}
    def add(key,configured,observed):
        status="not_checked" if observed in (None,"","—") else ("match" if str(configured).lower()==str(observed).lower() else "mismatch")
        checks[key]={"configured":configured,"observed":observed,"status":status}
    if settings.get("cpu_cores"):add("cpu_cores",settings["cpu_cores"],observation.get("cpu"))
    if engine=="camoufox" and settings.get("screen","auto")!="auto":
        add("screen",settings["screen"],observation.get("screen"))
    ip=observation.get("ip")
    checks["exit_ip"]={"configured":"proxy or direct connection","observed":ip,"status":"verified" if ip else "not_checked"}
    checks["os"]={"configured":os_type,"observed":observation.get("platform"),"status":"observed" if observation.get("platform") else "not_checked"}
    checks["engine"]={"configured":engine,"observed":observation.get("userAgent"),"status":"observed" if observation.get("userAgent") else "not_checked"}
    return {"checks":checks,"mismatch_count":sum(c["status"]=="mismatch" for c in checks.values()),"limitations":"Browser JS observation is not a guarantee of external anti-bot results."}
''',encoding="utf-8")

edit("src/services/profile/workspace.py",'for field in ("device_id", "webgl", "previous_ip", "ip_changed"):','for field in ("device_id", "webgl", "previous_ip", "ip_changed", "device_memory", "browser_vendor", "pixel_ratio", "color_depth"):')
edit("src/services/profile/workspace.py","timezone=?,cpu_cores=?,screen=?,device_id=?,webgl=?,error=?,previous_ip=?,ip_changed=? WHERE profile=?","timezone=?,cpu_cores=?,screen=?,device_id=?,webgl=?,error=?,previous_ip=?,ip_changed=?,device_memory=?,browser_vendor=?,pixel_ratio=?,color_depth=? WHERE profile=?")
edit("src/services/profile/workspace.py","str(result.get(\"webgl\") or \"\")[:280],error[:500],old_ip,int(ip_changed),profile))","str(result.get(\"webgl\") or \"\")[:280],error[:500],old_ip,int(ip_changed),\n                       str(result.get(\"memory\") or \"\")[:30],str(result.get(\"vendor\") or \"\")[:100],\n                       str(result.get(\"pixelRatio\") or \"\")[:30],str(result.get(\"colorDepth\") or \"\")[:30],profile))")

p=root/"src/ui/app.py";s=p.read_text(encoding="utf-8")
old="        audits=self.workspace.list_audits()\n"
assert old in s
s=s.replace(old,'''        audits=self.workspace.list_audits()
        from ..services.browser.environment_check import compare
        def signal_status(a):
            profile=self.pm.profiles.get(a["profile"])
            if profile is None:return "Profile không tồn tại"
            report=compare(profile.settings or {},profile.os_type,profile.engine,
                           {"cpu":a.get("cpu_cores"),"screen":a.get("screen"),
                            "platform":a.get("platform"),"ip":a.get("exit_ip"),
                            "userAgent":a.get("user_agent")})
            if a["status"] != "checked":return "Chưa xác minh: "+str(a.get("error") or "đang đo")[:70]
            return "Đã đối chiếu" if not report["mismatch_count"] else f"Lệch {report['mismatch_count']} chỉ số"
''')
needle="f\"{a['status'].upper()}  •  IP ra mạng:"
assert needle in s
s=s.replace(needle,"f\"{signal_status(a)}  •  {a['status'].upper()}  •  IP ra mạng:")
needle="f\"CPU: {a['cpu_cores'] or '—'}  •  Màn hình:"
assert needle in s
s=s.replace(needle,"f\"CPU: {a['cpu_cores'] or '—'}  •  RAM API: {a.get('device_memory') or '—'}  •  Màn hình:")
needle="f\"Timezone: {a['timezone'] or '—'}  •  Profile Device ID:"
assert needle in s
s=s.replace(needle,"f\"Timezone: {a['timezone'] or '—'}  •  Language: {a.get('language') or '—'}  •  UA: {a.get('user_agent') or '—'}  •  Vendor: {a.get('browser_vendor') or '—'}  •  DPR: {a.get('pixel_ratio') or '—'}  •  Profile Device ID:")
p.write_text(s,encoding="utf-8")

edit("studio_launcher.py",'APP_VERSION = "3.2.0"','APP_VERSION = "3.3.0"')
for f in ("windows/FASTBROWSERS.iss","windows/build-FASTBROWSERS.ps1"):
 p=root/f; text=p.read_text(encoding="utf-8").replace("3.2.1","3.3.0").replace("3.2.0","3.3.0");p.write_text(text,encoding="utf-8")
print("FASTBROWSERS 3.3 patch applied")

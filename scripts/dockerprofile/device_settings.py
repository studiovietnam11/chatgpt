"""Validated optional browser device configuration."""
from collections.abc import Mapping

DEFAULTS = {
    "device_class":"desktop", "os_version":"auto", "screen":"auto",
    "cpu_cores":0, "ram_gb":0, "group":"", "note":"",
}
DEVICE_CLASSES=("desktop","laptop","workstation","virtual_machine")
OS_VERSIONS={"windows":("auto","windows10","windows11"),"macos":("auto","macos14","macos15","macos26"),"linux":("auto","linux6")}
SCREENS=("auto","1280x720","1366x768","1440x900","1600x900","1920x1080","2560x1440")
CPU_CORES=(0,2,4,6,8,12,16,20)
RAM_GB=(0,4,8,16,32,64)

def validate_settings(raw:Mapping|None, os_type:str="windows")->dict:
    if raw is None:
        return DEFAULTS.copy()
    if not isinstance(raw,Mapping) or set(raw)-set(DEFAULTS):
        raise ValueError("Unknown or invalid device settings")
    s={**DEFAULTS,**raw}
    for key,allowed in (("device_class",DEVICE_CLASSES),("os_version",OS_VERSIONS.get(os_type,("auto",))),("screen",SCREENS),("cpu_cores",CPU_CORES),("ram_gb",RAM_GB)):
        if s[key] not in allowed or isinstance(s[key],bool):
            raise ValueError("Invalid device setting "+key)
    for key,limit in (("group",50),("note",500)):
        if not isinstance(s[key],str) or len(s[key])>limit:
            raise ValueError("Invalid device setting "+key)
        s[key]=s[key].strip()
    return s

def support(engine:str)->dict:
    return {"cpu_cores":"runtime","screen":"runtime" if engine=="camoufox" else "metadata",
            "os_version":"runtime" if engine=="chrome" else "metadata",
            "device_class":"metadata","ram_gb":"metadata"}

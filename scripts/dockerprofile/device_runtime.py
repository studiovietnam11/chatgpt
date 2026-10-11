"""Use profile configuration only where its browser engine supports it."""
import json
from pathlib import Path
from ...core.config import PROFILES_FILE
from ...models.device_settings import validate_settings

def read_settings(name:str,os_type:str)->dict:
    try:
        with Path(PROFILES_FILE).open(encoding="utf-8") as h:
            raw=json.load(h).get(name,{}).get("settings")
        return validate_settings(raw,os_type)
    except (OSError,ValueError,TypeError):
        return validate_settings(None,os_type)

def apply_camoufox(fp:dict,settings:dict)->dict:
    fp=json.loads(json.dumps(fp))
    if settings.get("cpu_cores"):
        fp.setdefault("navigator",{})["hardwareConcurrency"]=settings["cpu_cores"]
    if settings.get("screen") not in ("auto",None):
        w,h=map(int,settings["screen"].split("x"))
        f=fp.setdefault("screen",{})
        f["width"],f["height"]=w,h
        f["availWidth"]=min(f.get("availWidth",w),w)
        f["availHeight"]=min(f.get("availHeight",h),h)
    return fp

def chrome_persona_overrides(settings:dict)->dict:
    o={}
    if settings.get("cpu_cores"):
        o["hardware_concurrency"]=settings["cpu_cores"]
    mapping={"windows10":"10.0.0","windows11":"19.0.0","macos14":"14.7.6",
             "macos15":"15.6.1","macos26":"26.0.1","linux6":"6.8.0"}
    if settings.get("os_version") in mapping:
        o["platform_version"]=mapping[settings["os_version"]]
    return o

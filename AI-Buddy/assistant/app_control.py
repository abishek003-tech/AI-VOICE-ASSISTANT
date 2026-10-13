import logging
import os
import shutil
import subprocess
import time
from typing import Optional, Tuple
import psutil

import config
from assistant.actions import ActionResult

logger = logging.getLogger("ai_assistant.app_control")

def resolve_app_key(query: str) -> Optional[str]:
    """Match spoken app name against registered application aliases."""
    query_clean = query.lower().strip()
    # Check exact match
    if query_clean in config.APP_REGISTRY:
        return query_clean
    # Check substring matches
    for key in config.APP_REGISTRY:
        if key in query_clean or query_clean in key:
            return key
    return None

def find_executable(app_info: dict) -> Optional[str]:
    """Locate the executable path for the given application configuration."""
    for exe in app_info.get("executables", []):
        if os.path.isabs(exe) and os.path.isfile(exe):
            return exe
        resolved = shutil.which(exe)
        if resolved and os.path.isfile(resolved):
            return resolved
    return None

def launch_application(app_name: str) -> ActionResult:
    """Safely launch a registered desktop application and verify success."""
    app_key = resolve_app_key(app_name)
    if not app_key:
        msg = f"I couldn't find {app_name} in my supported applications list."
        return ActionResult(success=False, message=msg, detail=f"App '{app_name}' not in registry")

    app_info = config.APP_REGISTRY[app_key]
    display_name = app_info.get("display_name", app_key.title())
    exe_path = find_executable(app_info)
    uri = app_info.get("uri")

    try:
        if exe_path:
            logger.info(f"Launching {display_name} via executable: {exe_path}")
            proc = subprocess.Popen([exe_path], shell=False)
            # Short verification pause to ensure process didn't instantly exit with error
            time.sleep(0.3)
            if proc.poll() is not None and proc.returncode != 0:
                msg = f"Failed to open {display_name}."
                return ActionResult(success=False, message=msg, detail=f"Exited with code {proc.returncode}")
        elif uri:
            logger.info(f"Launching {display_name} via URI scheme: {uri}")
            os.startfile(uri)
            time.sleep(0.3)
        else:
            msg = f"{display_name} executable was not found on this computer."
            return ActionResult(success=False, message=msg, detail="Executable path not found")

        # Dynamic confirmation message based on response mode
        if config.RESPONSE_MODE == "tanglish":
            msg = f"{display_name} open panniten."
        else:
            msg = f"{display_name} is open."
        return ActionResult(success=True, message=msg, detail=f"Successfully launched {display_name}")

    except Exception as e:
        logger.error(f"Error launching {display_name}: {e}")
        fail_msg = f"Sorry, {display_name} open panna mudiyala." if config.RESPONSE_MODE == "tanglish" else f"Sorry, I couldn't open {display_name}."
        return ActionResult(success=False, message=fail_msg, detail=str(e))

def close_application(app_name: str) -> ActionResult:
    """Safely terminate all running instances of a registered application."""
    app_key = resolve_app_key(app_name)
    if not app_key:
        msg = f"Sorry, I couldn't find any registered application named {app_name}."
        return ActionResult(success=False, message=msg, detail=f"App '{app_name}' not in registry")

    app_info = config.APP_REGISTRY[app_key]
    display_name = app_info.get("display_name", app_key.title())
    process_names = [p.lower() for p in app_info.get("process_names", [])]

    if not process_names:
        return ActionResult(success=False, message=f"No process definitions found for {display_name}.")

    terminated_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                p_name = proc.info.get('name') or ""
                if p_name.lower() in process_names:
                    proc.terminate()
                    terminated_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if terminated_count == 0:
            if config.RESPONSE_MODE == "tanglish":
                msg = f"{display_name} ippo open-la illa."
            else:
                msg = f"{display_name} is not open."
            return ActionResult(success=True, message=msg, detail="Process not running")

        time.sleep(0.4)
        if config.RESPONSE_MODE == "tanglish":
            msg = f"{display_name} close panniten."
        else:
            msg = f"{display_name} is closed."
        return ActionResult(success=True, message=msg, detail=f"Terminated {terminated_count} processes")

    except Exception as e:
        logger.error(f"Error terminating {display_name}: {e}")
        fail_msg = f"Sorry, {display_name} close panna mudiyala." if config.RESPONSE_MODE == "tanglish" else f"Sorry, I couldn't close {display_name}."
        return ActionResult(success=False, message=fail_msg, detail=str(e))

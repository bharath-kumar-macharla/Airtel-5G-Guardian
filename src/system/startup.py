"""
Startup Manager
---------------
v0.5.0 - Registers/unregisters Guardian to launch automatically when
Windows starts, using the current user's Run registry key. No admin
rights required (HKEY_CURRENT_USER is per-user).

Safe to import on non-Windows platforms — every method degrades to a
no-op / False so the rest of the app never has to special-case the OS.
"""

import sys
from pathlib import Path

APP_REG_NAME = "AirtelGuardian5G"


def _is_windows() -> bool:
    return sys.platform == "win32"


def _launch_command() -> str:
    """
    Builds the command Windows should run at logon.

    - Frozen (PyInstaller) build → run the .exe directly with --minimized.
    - Source checkout → run pythonw.exe run_gui.py --minimized so no
      console window flashes on boot.
    """
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable).resolve()
        return f'"{exe}" --minimized'

    project_root = Path(__file__).resolve().parent.parent.parent
    entry = project_root / "run_gui.py"
    pythonw = Path(sys.executable).resolve()
    # Prefer pythonw.exe (no console) if it sits next to the interpreter
    pythonw_candidate = pythonw.parent / "pythonw.exe"
    interpreter = pythonw_candidate if pythonw_candidate.exists() else pythonw
    return f'"{interpreter}" "{entry}" --minimized'


def is_enabled() -> bool:
    """Returns True if Guardian is currently registered to launch at startup."""
    if not _is_windows():
        return False
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        )
        try:
            winreg.QueryValueEx(key, APP_REG_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def enable() -> bool:
    """Adds Guardian to the current user's startup entries."""
    if not _is_windows():
        return False
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, _launch_command())
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[Startup] Could not enable launch-on-startup: {e}")
        return False


def disable() -> bool:
    """Removes Guardian from the current user's startup entries."""
    if not _is_windows():
        return False
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            winreg.DeleteValue(key, APP_REG_NAME)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[Startup] Could not disable launch-on-startup: {e}")
        return False


def set_enabled(enabled: bool) -> bool:
    """Convenience toggle used by the Settings panel."""
    return enable() if enabled else disable()

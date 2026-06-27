"""
Application Configuration
-------------------------
v0.2.0 - All values now loaded from config/config.json via ConfigManager.
Hardcoded constants kept as fallback defaults.
"""

import json
from pathlib import Path


# ── Fallback constants (used only if config.json is missing) ──────────────────

APP_NAME    = "Airtel 5G Guardian"
APP_VERSION = "0.2.0"

ADB_PATH             = r"C:\platform-tools\platform-tools\adb.exe"
CHECK_INTERVAL       = 5
LOG_FILE             = "logs/guardian.log"
NOTIFICATION_TIMEOUT = 5

NETWORK_5G      = "5G"
NETWORK_4G      = "4G"
NETWORK_UNKNOWN = "UNKNOWN"


# ── ConfigManager ─────────────────────────────────────────────────────────────

class ConfigManager:
    """
    Loads all application settings from config/config.json.
    Falls back to constants above if the file is missing.
    """

    _CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.json"

    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        if not self._CONFIG_PATH.exists():
            print(
                f"[Config] WARNING: config.json not found at {self._CONFIG_PATH}\n"
                "[Config] Using hardcoded defaults."
            )
            return {}
        with open(self._CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[Config] Loaded config.json ✓")
        return data

    # ── app ───────────────────────────────────────────────────────────────────

    @property
    def app_name(self) -> str:
        return self._data.get("app", {}).get("name", APP_NAME)

    @property
    def app_version(self) -> str:
        return self._data.get("app", {}).get("version", APP_VERSION)

    # ── adb ───────────────────────────────────────────────────────────────────

    @property
    def adb_path(self) -> str:
        return self._data.get("adb", {}).get("path", ADB_PATH)

    @property
    def phone_ip(self) -> str:
        return self._data.get("adb", {}).get("phone_ip", "192.168.43.1")

    @property
    def adb_port(self) -> int:
        return self._data.get("adb", {}).get("port", 5555)

    @property
    def adb_target(self) -> str:
        """Returns 'ip:port' e.g. 192.168.43.1:5555"""
        return f"{self.phone_ip}:{self.adb_port}"

    @property
    def reconnect_attempts(self) -> int:
        return self._data.get("adb", {}).get("reconnect_attempts", 5)

    @property
    def reconnect_delay(self) -> int:
        return self._data.get("adb", {}).get("reconnect_delay_seconds", 10)

    # ── monitor ───────────────────────────────────────────────────────────────

    @property
    def check_interval(self) -> int:
        return self._data.get("monitor", {}).get("check_interval_seconds", CHECK_INTERVAL)

    # ── notification ──────────────────────────────────────────────────────────

    @property
    def notification_timeout(self) -> int:
        return self._data.get("notification", {}).get("timeout_seconds", NOTIFICATION_TIMEOUT)

    # ── log ───────────────────────────────────────────────────────────────────

    @property
    def log_file(self) -> str:
        return self._data.get("log", {}).get("file", LOG_FILE)

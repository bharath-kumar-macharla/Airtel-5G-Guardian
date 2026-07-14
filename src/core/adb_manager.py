"""
ADB Manager
-----------
v1.0.0 — Smart startup flow with polished Recovery Mode messages.
  1. Try last saved IP wirelessly.
  2. If fails → enter Recovery Mode (wait for USB indefinitely).
  3. USB detected → enable TCP/IP → read new IP → update config.json.
  4. Reconnect wirelessly → resume monitoring.

Legacy module-level functions (run_adb_command, get_telephony_dump, etc.)
are still present for the CLI path (run.py) but now lazy-initialize their
internal singleton on first call instead of at import time — preventing a
redundant ConfigManager load every time a module imports adb_manager.py.
"""

import json
import re
import subprocess
import time
from pathlib import Path

from src.config import ConfigManager
from src.utils import print_recovery_banner, print_recovery_success


class ADBManager:

    HOTSPOT_INTERFACE  = "wlan1"
    FALLBACK_INTERFACE = "wlan0"
    USB_POLL_INTERVAL  = 3  # seconds between USB checks in recovery mode

    def __init__(self, config: ConfigManager):
        self.config  = config
        self._adb    = config.adb_path
        self._target = config.adb_target  # ip:port from config.json

    # ── Internal runner ───────────────────────────────────────────────────────

    def _run(self, args: list, timeout: int = 10) -> tuple:
        import sys
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        try:
            result = subprocess.run(
                [self._adb] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=creationflags
            )
            return result.stdout.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", 1
        except FileNotFoundError:
            print(
                f"[ADB] ERROR: adb.exe not found at → {self._adb}\n"
                "[ADB] Open Settings and use Browse… to locate adb.exe."
            )
            return "", 1
        except PermissionError as exc:
            print(f"[ADB] ERROR: Permission denied running adb → {exc}")
            return "", 1
        except Exception as exc:  # noqa: BLE001
            print(f"[ADB] ERROR: Unexpected error running adb → {exc}")
            return "", 1

    # ── Connection helpers ────────────────────────────────────────────────────

    def is_connected(self) -> bool:
        """Check if our wireless target is currently connected."""
        stdout, _ = self._run(["devices"])
        return self._target in stdout

    def connect(self) -> bool:
        """Attempt a single wireless connect. Returns True on success."""
        print(f"[ADB] Connecting to {self._target}...")
        stdout, _ = self._run(["connect", self._target], timeout=15)

        if "connected" in stdout.lower() and "unable" not in stdout.lower():
            print(f"[ADB] ✓ Connected to {self._target}")
            return True

        print(f"[ADB] ✗ Connection failed → {stdout}")
        return False

    def disconnect(self):
        """Gracefully disconnect from the wireless device."""
        self._run(["disconnect", self._target])

    # ── USB helpers ───────────────────────────────────────────────────────────

    def _get_usb_device(self) -> str | None:
        """Returns USB device serial, ignoring wireless targets."""
        stdout, _ = self._run(["devices"])
        for line in stdout.splitlines()[1:]:
            if "\tdevice" in line:
                serial = line.split()[0]
                if "." not in serial and ":" not in serial:
                    return serial
        return None

    def _enable_tcpip(self, serial: str) -> bool:
        """Enable wireless ADB mode on port 5555."""
        stdout, code = self._run(["-s", serial, "tcpip", "5555"], timeout=10)
        if code == 0 or "restarting" in stdout.lower():
            print(f"  ✓ TCP/IP enabled on port 5555")
            time.sleep(2)
            return True
        print(f"  ✗ Failed to enable TCP/IP mode")
        return False

    def _fetch_ip_via_usb(self, serial: str) -> str | None:
        """Fetch phone's current hotspot IP via USB ADB."""
        for interface in [self.HOTSPOT_INTERFACE, self.FALLBACK_INTERFACE]:
            stdout, code = self._run(
                ["-s", serial, "shell", f"ip addr show {interface}"],
                timeout=10
            )
            if code == 0 and "inet " in stdout:
                match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/", stdout)
                if match:
                    ip = match.group(1)
                    print(f"  ✓ New IP detected → {ip} (via {interface})")
                    return ip
        return None

    def _update_ip(self, new_ip: str):
        """Save new IP to config.json AND update self._target in memory."""
        config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            old_ip = data["adb"]["phone_ip"]
            data["adb"]["phone_ip"] = new_ip

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print(f"  ✓ Configuration updated: {old_ip} → {new_ip}")
        except Exception as e:
            print(f"  ✗ Could not update config.json → {e}")

        self._target = f"{new_ip}:{self.config.adb_port}"

    # ── Recovery Mode ─────────────────────────────────────────────────────────

    def _recovery_mode(self) -> bool:
        """
        Entered when saved IP fails. Waits indefinitely for USB.
        Once USB detected → fixes IP → reconnects wirelessly → resumes.
        """
        print_recovery_banner()

        dots = 0
        while True:
            serial = self._get_usb_device()

            if serial:
                print(f"  ✓ USB device detected → {serial}\n")

                if not self._enable_tcpip(serial):
                    print("\n  Replug USB and try again.\n")
                    time.sleep(self.USB_POLL_INTERVAL)
                    continue

                ip = self._fetch_ip_via_usb(serial)
                if not ip:
                    print("\n  ✗ Could not read IP. Make sure hotspot is ON.\n")
                    time.sleep(self.USB_POLL_INTERVAL)
                    continue

                self._update_ip(ip)

                print(f"\n  Reconnecting wirelessly to {self._target}...")
                if self.connect():
                    print_recovery_success()
                    return True
                else:
                    print("  ✗ Wireless connect failed. Retrying...\n")
                    time.sleep(self.USB_POLL_INTERVAL)
                    continue

            # No USB yet — animate waiting dots
            dots = (dots % 3) + 1
            print(f"\r  Waiting for USB{'.' * dots}   ", end="", flush=True)
            time.sleep(self.USB_POLL_INTERVAL)

    # ── Main connection entry point ───────────────────────────────────────────

    def ensure_connected(self) -> bool:
        """
        Step 1 → Try saved IP wirelessly.
        Step 2 → If fail → Recovery Mode (wait for USB, auto fix, reconnect).
        """
        print(f"[ADB] Trying saved IP → {self._target}")
        if self.is_connected() or self.connect():
            return True

        return self._recovery_mode()

    # ── Shell command ─────────────────────────────────────────────────────────

    def shell(self, command: str) -> str | None:
        """Run shell command. Enters recovery mode if connection is lost."""
        if not self.is_connected():
            print("\n[ADB] Connection lost mid-session.")
            if not self._recovery_mode():
                return None

        stdout, code = self._run(["-s", self._target, "shell", command])
        return stdout if code == 0 else None

    def get_telephony_dump(self) -> str | None:
        return self.shell("dumpsys telephony.registry")


# ── Legacy module-level functions (CLI / run.py path) ─────────────────────────
# These are lazy-initialized on first call so importing this module does
# NOT trigger a ConfigManager read or subprocess spawn at import time.

_legacy_manager = None


def _get_legacy_manager() -> "ADBManager":
    """Returns (and lazy-creates) the module-level ADB manager for the CLI."""
    global _legacy_manager  # noqa: PLW0603
    if _legacy_manager is None:
        _legacy_manager = ADBManager(ConfigManager())
    return _legacy_manager


def run_adb_command(command):
    mgr = _get_legacy_manager()
    stdout, code = mgr._run(command)
    return stdout if code == 0 else None


def get_connected_devices():
    output = run_adb_command(["devices"])
    if output is None:
        return []
    devices = []
    for line in output.splitlines()[1:]:
        if "\tdevice" in line:
            devices.append(line.split()[0])
    return devices


def is_device_connected():
    return _get_legacy_manager().is_connected()


def get_telephony_dump():
    return _get_legacy_manager().get_telephony_dump()


def wait_for_device():
    return _get_legacy_manager().ensure_connected()

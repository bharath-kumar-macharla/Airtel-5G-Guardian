"""
Network Monitor
---------------
v1.0.0 — Accepts an ADBManager instance so the GUI path uses the same
          connection object as the rest of the application instead of
          the module-level legacy singleton in adb_manager.py.

          The CLI path passes no argument and falls back to the legacy
          module-level function so run.py continues to work unchanged.
"""

from src.config import (
    NETWORK_5G,
    NETWORK_4G,
    NETWORK_UNKNOWN,
)


class NetworkMonitor:

    def __init__(self, adb_manager=None):
        """
        Parameters
        ----------
        adb_manager : ADBManager | None
            When provided (GUI path), telephony dumps are fetched via this
            instance — meaning the same ADB connection, path, and IP that
            the GUI set up.  When None (CLI path), falls back to the
            module-level legacy function for backwards compatibility.
        """
        self.previous_status = None
        self._adb = adb_manager

    def get_current_network(self) -> str:
        if self._adb is not None:
            dump = self._adb.get_telephony_dump()
        else:
            # CLI / legacy path — import lazily to avoid circular import at
            # module level and to prevent the singleton from being created
            # unless it is actually needed.
            from src.core.adb_manager import get_telephony_dump  # noqa: PLC0415
            dump = get_telephony_dump()

        if dump is None:
            return NETWORK_UNKNOWN

        for line in dump.splitlines():
            line = line.strip()
            if line.startswith("mTelephonyDisplayInfo="):
                if "overrideNetwork=NR_NSA" in line:
                    return NETWORK_5G
                if "overrideNetwork=NONE" in line:
                    return NETWORK_4G
                if "overrideNetwork=LTE_CA" in line:
                    return NETWORK_UNKNOWN

        return NETWORK_UNKNOWN

    def has_changed(self) -> tuple:
        current = self.get_current_network()
        changed = current != self.previous_status
        self.previous_status = current
        return changed, current
"""
Network Monitor
---------------
Detects the current network status (4G / 5G)
"""

from src.core.adb_manager import get_telephony_dump
from src.config import (
    NETWORK_5G,
    NETWORK_4G,
    NETWORK_UNKNOWN
)


class NetworkMonitor:

    def __init__(self):

        self.previous_status = None

    def get_current_network(self):

        dump = get_telephony_dump()

        if dump is None:
            return "UNKNOWN"

        for line in dump.splitlines():

            line = line.strip()

            if line.startswith("mTelephonyDisplayInfo="):

                if "overrideNetwork=NR_NSA" in line:
                    return NETWORK_5G

                elif "overrideNetwork=NONE" in line:
                    return NETWORK_4G

                elif "overrideNetwork=LTE_CA" in line:
                    return NETWORK_UNKNOWN

        return "UNKNOWN"

    def has_changed(self):

        current = self.get_current_network()

        changed = current != self.previous_status

        self.previous_status = current

        return changed, current
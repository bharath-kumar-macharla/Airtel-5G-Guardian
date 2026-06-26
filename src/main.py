"""
Main Application
"""

import time

from src.config import (
    CHECK_INTERVAL,
    NETWORK_4G,
    NETWORK_5G
)

from src.core.network_monitor import NetworkMonitor
from src.core.adb_manager import wait_for_device
from src.services.logger import GuardianLogger
from src.services.notifier import GuardianNotifier
from src.services.sound_manager import SoundManager
from src.utils import banner

def main():
    wait_for_device()

    monitor = NetworkMonitor()

    logger = GuardianLogger()

    notifier = GuardianNotifier()
    
    banner()
    try:
        while True:

            changed, network = monitor.has_changed()

            if changed:

                if network == NETWORK_5G:

                    print("🟢 Connected to 5G")

                    logger.write("Connected to 5G")

                    notifier.show(
                        "🟢 5G Connected",
                        "Unlimited Data Active 🚀"
                    )
                    SoundManager.play_5g()

                elif network == NETWORK_4G:

                    print("🔴 Switched to 4G")

                    logger.write("Switched to 4G")

                    notifier.show(
                        "🔴 4G Detected",
                        "Your Daily Data is now being used."
                    )
                    SoundManager.play_4g()

            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\nStopping Airtel 5G Guardian...")
        logger.write("Guardian stopped.")
        print("Goodbye 👋")
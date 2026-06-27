"""
Main Application
----------------
v0.2.1 - Polished startup banner and recovery messages.
"""

import time

from src.config import ConfigManager, NETWORK_4G, NETWORK_5G
from src.core.network_monitor import NetworkMonitor
from src.core.adb_manager import ADBManager
from src.services.logger import GuardianLogger
from src.services.notifier import GuardianNotifier
from src.services.sound_manager import SoundManager
from src.utils import print_startup_banner


def main():

    # ── Load config ───────────────────────────────────────────────────────────
    config = ConfigManager()

    # ── Startup banner ────────────────────────────────────────────────────────
    print_startup_banner(
        version=config.app_version,
        target=config.adb_target
    )

    # ── Connect (tries saved IP → Recovery Mode if needed) ───────────────────
    adb = ADBManager(config)

    if not adb.ensure_connected():
        print("[Guardian] Could not connect. Exiting.")
        return

    # ── Services ──────────────────────────────────────────────────────────────
    monitor  = NetworkMonitor()
    logger   = GuardianLogger()
    notifier = GuardianNotifier()

    print("[Guardian] Monitoring started. Press Ctrl+C to stop.\n")

    # ── Monitoring loop ───────────────────────────────────────────────────────
    try:
        while True:

            changed, network = monitor.has_changed()

            if changed:

                if network == NETWORK_5G:
                    print("🟢 Connected to 5G")
                    logger.write("Connected to 5G")
                    notifier.show("🟢 5G Connected", "Unlimited Data Active 🚀")
                    SoundManager.play_5g()

                elif network == NETWORK_4G:
                    print("🔴 Switched to 4G")
                    logger.write("Switched to 4G")
                    notifier.show("🔴 4G Detected", "Your Daily Data is now being used.")
                    SoundManager.play_4g()

            time.sleep(config.check_interval)

    except KeyboardInterrupt:
        print("\n\nStopping Airtel 5G Guardian...")
        logger.write("Guardian stopped.")
        adb.disconnect()
        print("Goodbye 👋")

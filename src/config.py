"""
Application Configuration
-------------------------
All configurable values for Airtel 5G Guardian.
"""

APP_NAME = "Airtel 5G Guardian"
APP_VERSION = "1.1"

# Path to ADB
ADB_PATH = r"C:\platform-tools\platform-tools\adb.exe"

# Network monitoring
CHECK_INTERVAL = 5      # seconds

# Logging
LOG_FILE = "logs/guardian.log"

# Notification duration
NOTIFICATION_TIMEOUT = 5

NETWORK_5G = "5G"
NETWORK_4G = "4G"
NETWORK_UNKNOWN = "UNKNOWN"
"""
Guardian Notifications
----------------------
v0.2.0 - App name and timeout loaded from ConfigManager.
"""

from plyer import notification
from src.config import ConfigManager


class GuardianNotifier:

    def __init__(self):
        config          = ConfigManager()
        self._app_name  = config.app_name
        self._timeout   = config.notification_timeout

    def show(self, title: str, message: str):

        notification.notify(
            title    = title,
            message  = message,
            app_name = self._app_name,
            timeout  = self._timeout
        )

"""
Guardian Notifications
----------------------
v0.5.0 - App name and timeout loaded from ConfigManager.
Notification failures (no OS backend, permissions, headless session)
are swallowed so they never interrupt monitoring — stability over
completeness for a background service.
"""

from plyer import notification
from src.config import ConfigManager


class GuardianNotifier:

    def __init__(self):
        config          = ConfigManager()
        self._app_name  = config.app_name
        self._timeout   = config.notification_timeout

    def show(self, title: str, message: str):
        try:
            notification.notify(
                title    = title,
                message  = message,
                app_name = self._app_name,
                timeout  = self._timeout
            )
        except Exception:
            # A missing/broken toast backend should never take monitoring down.
            pass

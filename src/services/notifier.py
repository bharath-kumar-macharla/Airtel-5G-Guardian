"""
Guardian Notifications
"""

from plyer import notification

from src.config import (
    APP_NAME,
    NOTIFICATION_TIMEOUT
)


class GuardianNotifier:

    def show(self,title: str,message: str):

        notification.notify(

            title=title,

            message=message,

            app_name=APP_NAME,

            timeout=NOTIFICATION_TIMEOUT
        )
"""
Sound Manager
-------------
Plays system sounds for Guardian events.
"""

import winsound


class SoundManager:

    @staticmethod
    def play_4g():
        winsound.PlaySound(
            "SystemExclamation",
            winsound.SND_ALIAS
        )

    @staticmethod
    def play_5g():
        winsound.PlaySound(
            "SystemAsterisk",
            winsound.SND_ALIAS
        )

    @staticmethod
    def play_error():
        winsound.PlaySound(
            "SystemHand",
            winsound.SND_ALIAS
        )
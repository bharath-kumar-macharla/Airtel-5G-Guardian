"""
Sound Manager
-------------
v0.5.0 - Plays system sounds for Guardian events.

Hardened for stability: winsound is Windows-only. Importing it
unconditionally used to crash Guardian on any non-Windows environment
(and any environment where playback fails). All calls are now wrapped
so a missing backend or playback error never takes down monitoring.
"""

import sys

try:
    import winsound
    _SOUND_AVAILABLE = sys.platform == "win32"
except ImportError:
    winsound = None
    _SOUND_AVAILABLE = False


class SoundManager:

    @staticmethod
    def _play(alias: str):
        if not _SOUND_AVAILABLE:
            return
        try:
            winsound.PlaySound(alias, winsound.SND_ALIAS)
        except Exception:
            # Never let a sound-device hiccup interrupt monitoring.
            pass

    @staticmethod
    def play_4g():
        SoundManager._play("SystemExclamation")

    @staticmethod
    def play_5g():
        SoundManager._play("SystemAsterisk")

    @staticmethod
    def play_error():
        SoundManager._play("SystemHand")

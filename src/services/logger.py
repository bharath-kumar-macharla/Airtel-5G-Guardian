"""
Guardian Logger
---------------
v0.2.0 - Log file path loaded from ConfigManager.
"""

from datetime import datetime
from pathlib import Path

from src.config import ConfigManager


class GuardianLogger:

    def __init__(self):
        config   = ConfigManager()
        log_file = config.log_file
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        self._log_file = log_file

    def write(self, message: str):

        now = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

        with open(self._log_file, "a", encoding="utf-8") as file:
            file.write(f"[{now}] {message}\n")

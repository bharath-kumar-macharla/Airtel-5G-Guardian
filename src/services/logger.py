"""
Guardian Logger
"""

from datetime import datetime
from pathlib import Path

from src.config import LOG_FILE


class GuardianLogger:

    def __init__(self):

        Path(LOG_FILE).parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def write(self, message: str):

        now = datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )

        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"[{now}] {message}\n"
            )
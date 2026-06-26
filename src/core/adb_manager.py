"""
ADB Manager
-----------
Handles all communication with Android Debug Bridge.
"""

import subprocess
import time
from src.config import ADB_PATH


def run_adb_command(command):
    """
    Runs an ADB command and returns its output.
    """

    try:

        output = subprocess.check_output(
            [ADB_PATH] + command,
            text=True,
            stderr=subprocess.STDOUT
        )

        return output.strip()

    except subprocess.CalledProcessError as e:

        print("ADB Error:")
        print(e.output)

        return None


def get_connected_devices():
    """
    Returns a list of connected devices.
    """

    output = run_adb_command(["devices"])

    if output is None:
        return []

    devices = []

    for line in output.splitlines()[1:]:

        if "\tdevice" in line:

            devices.append(line.split()[0])

    return devices


def is_device_connected():
    """
    Returns True if at least one device is connected.
    """

    return len(get_connected_devices()) > 0


def get_telephony_dump():
    """
    Returns telephony registry output.
    """

    return run_adb_command(
        ["shell", "dumpsys", "telephony.registry"]
    )


def wait_for_device():

    while True:

        devices = get_connected_devices()

        if devices:

            return True

        print("Waiting for device...")

        time.sleep(5)
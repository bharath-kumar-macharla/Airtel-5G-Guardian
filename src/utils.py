"""
Utility Functions
"""

from datetime import datetime


def current_time():
    return datetime.now().strftime("%I:%M:%S %p")


def current_date():
    return datetime.now().strftime("%d-%m-%Y")


def current_datetime():
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")


def separator():
    print("-" * 60)


def banner():
    print()


def print_startup_banner(version: str, target: str):
    """
    Polished startup banner shown when Guardian launches.
    """
    line = "=" * 50
    print()
    print(line)
    print(f"  📶 Airtel 5G Guardian  v{version}")
    print(line)
    print()
    print("  ✓ Configuration loaded")
    print("  ✓ ADB ready")
    print()
    print("  Target device:")
    print(f"  {target}")
    print()
    print(line)
    print()


def print_recovery_banner():
    """
    Clear, friendly banner shown when Recovery Mode is entered.
    """
    line = "=" * 50
    print()
    print(line)
    print("  ⚠  Recovery Mode")
    print(line)
    print()
    print("  Wireless connection failed.")
    print("  Please connect your phone via USB.")
    print()
    print("  Guardian will automatically:")
    print("    ✓ Enable TCP/IP")
    print("    ✓ Detect new IP")
    print("    ✓ Update configuration")
    print("    ✓ Resume monitoring")
    print()
    print(line)
    print()


def print_recovery_success():
    """Shown when Recovery Mode successfully reconnects."""
    line = "=" * 50
    print()
    print(line)
    print("  ✓  Connection Restored")
    print(line)
    print()
    print("  Guardian is resuming monitoring.")
    print()
    print(line)
    print()

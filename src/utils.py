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

    print("=" * 55)
    print("📶 Airtel 5G Guardian v1.1")
    print("=" * 55)
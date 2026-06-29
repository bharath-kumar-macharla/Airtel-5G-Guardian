"""
Airtel 5G Guardian — GUI Entry Point (v0.3.0)
Run this for the desktop GUI.
Run run.py for the CLI version.
"""
from src.gui.app import GuardianApp

if __name__ == "__main__":
    app = GuardianApp()
    app.mainloop()

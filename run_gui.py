"""
Airtel 5G Guardian — GUI Entry Point (v0.5.0)
Run this for the desktop GUI. Run run.py for the CLI version.

Flags:
  --minimized   Launch straight into the system tray with no visible
                window. Used automatically by the "Launch with Windows"
                startup entry (see src/system/startup.py) so boot-time
                launches don't flash a window on screen.
"""
import sys

from src.gui.app import GuardianApp

if __name__ == "__main__":
    minimized = "--minimized" in sys.argv[1:]
    app = GuardianApp(start_minimized=minimized)
    app.mainloop()

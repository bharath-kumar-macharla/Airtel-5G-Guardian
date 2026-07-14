# User Guide — Airtel 5G Guardian v1.0.0

This guide explains every feature of the Guardian desktop application.

---

## Starting the Application

```bash
python run_gui.py
```

Or double-click `Airtel-5G-Guardian.exe` if you are using the packaged version.

**First launch:** If `adb.exe` is not configured, a **Setup Wizard** will appear to walk you through the one-time configuration.

---

## Dashboard

The Dashboard is the main screen. It contains:

### Status Cards

| Card | Shows |
|------|-------|
| **DEVICE** | Connection state (Connected / Recovery Mode / Failed) |
| **NETWORK** | Current network (5G Unlimited / 4G (Limited) / Unknown) |
| **ADB** | ADB connection method (Wireless / USB Detected) |
| **LAST CHANGE** | Time of the most recent network switch |

### Start / Stop Monitoring

- **▶ Start Monitoring** — connects to your phone via wireless ADB and begins watching for 5G ↔ 4G transitions.
- **■ Stop** — stops monitoring and disconnects from ADB.

### Status Indicator

The dot in the top-right corner reflects the current state:

| Color | Meaning |
|-------|---------|
| 🟡 Yellow | Connecting |
| 🟢 Green | Monitoring active |
| 🔴 Red | Disconnected / error |
| 🟠 Orange | Recovery Mode |
| ⚫ Gray | Idle |

### Live Activity Log

All events are shown in real time:

- **Search** — filter the log by typing in the search box.
- **Clear** — clears the on-screen log (does not affect `logs/guardian.log`).
- **Save** — saves the current log to a `.txt` file.
- **Auto-scroll** — when checked, the log always scrolls to the latest entry.

---

## Recovery Mode

When wireless ADB fails (phone IP changed, hotspot restarted), Guardian enters **Recovery Mode** automatically.

What happens:
1. Guardian displays "Recovery Mode — Plug in USB cable"
2. Connect your phone via USB
3. Guardian detects the USB connection, enables TCP/IP ADB, reads the new IP
4. Configuration is updated automatically
5. Monitoring resumes wirelessly

> You do **not** need to click anything during recovery. Just plug in the USB.

---

## Analytics

Navigate to the **Analytics** tab to see today's monitoring intelligence.

### Summary Cards

| Card | Shows |
|------|-------|
| MONITORING | Total monitoring time today |
| 5G ACTIVE | Time spent connected to 5G |
| 4G RISK | Time on 4G (consuming daily data) |
| SWITCHES | Number of network transitions |
| 5G UPTIME | Percentage of time on 5G |
| LAST 4G DROP | Time of the most recent 4G detection |

### Network Timeline

Shows the last 50 network events with timestamps.

### Export Report

Click **Export Report** to generate:
- `exports/guardian_report_YYYY-MM-DD.txt` — human-readable daily summary
- `exports/guardian_sessions_YYYY-MM-DD.csv` — session data for spreadsheets

---

## Settings

Navigate to the **Settings** tab to configure Guardian.

### Connection Settings

| Field | Description |
|-------|-------------|
| ADB Path | Full path to `adb.exe`. Click **Browse…** to locate it. |
| Phone IP | Your phone's hotspot IP address. |
| Port | ADB port (default: 5555) |
| Check Interval | How often to poll the network (seconds) |
| Notification Timeout | How long desktop notifications stay visible |
| Reconnect Attempts | How many times to retry connection |

Click **Test Connection** to verify without saving.

Click **Save** to write all changes to `config.json`.

### Startup & Behavior

| Toggle | Effect |
|--------|--------|
| Launch Guardian when Windows starts | Adds/removes a Windows startup registry entry |
| Start minimized to tray | Hides the window on launch |
| Minimize to tray instead of closing | (X) button minimizes rather than exits |
| Auto-resume monitoring on launch | Resumes the last session automatically |
| Check for updates automatically | Background GitHub release check on startup |

---

## System Tray

When minimized, Guardian lives in the Windows system tray (bottom-right corner near the clock).

Right-click the tray icon to access:
- **▶ Start Monitoring**
- **⏹ Stop Monitoring**
- **🖥 Open Dashboard** (double-click also works)
- **⚙ Settings**
- **❌ Exit**

The tray icon color reflects Guardian's current status (matches the dashboard dot).

---

## About

Click **ℹ About** in the sidebar to view the application version, developer info, and a link to the GitHub repository.

---

## Notifications

Guardian sends Windows desktop notifications for:
- 🟢 **5G Connected** — "Unlimited Data Active 🚀"
- 🔴 **4G Detected** — "Your Daily Data is now being used."

Different alert sounds play for each transition (Windows system sounds).

---

## Keyboard Shortcuts

There are no keyboard shortcuts at this time. All features are accessible via the GUI or system tray menu.

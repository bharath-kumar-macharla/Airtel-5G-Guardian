# CHANGELOG

All notable changes to **Airtel 5G Guardian** will be documented in this file.

This project follows a simple versioning approach where each release introduces new features, architectural improvements, and stability enhancements.

---

# 🚀 v0.5.0 — Always Running, Always Protecting

## ✨ New Features

### System Tray Integration

* Guardian now minimizes to the Windows system tray instead of closing
* Tray menu: Start Monitoring, Stop Monitoring, Open Dashboard, Settings, Exit
* Monitoring keeps running while minimized
* Tray icon color reflects live status (idle / connecting / monitoring / disconnected / recovery)
* New sidebar shortcut: "Minimize to Tray"

### Launch with Windows

* New Settings toggle: "Launch Guardian when Windows starts"
* Registers Guardian under the current user's Run key (no admin rights required)
* Boot-time launches start silently in the tray via `run_gui.py --minimized`

### Smart Startup

* New Settings toggle: "Auto-resume monitoring on launch"
* When enabled, Guardian loads config, skips the placeholder IP, and resumes
  monitoring automatically — no clicks required

### Automatic Update Checker

* Background check against GitHub releases shortly after launch
* Shows a "🚀 vX.Y.Z Available" dialog with Download / Later
* New Settings toggle: "Check for updates automatically"

### Better Settings

* Browse ADB button opens a file picker instead of hand-typing paths
* Test Connection button verifies ADB reachability without saving
* Full input validation before Save (numeric fields, ADB path existence)
* Native dialogs for ✔ Settings Saved / ⚠ Invalid ADB Path / ❌ Device Not Found
* New "Startup & Behavior" settings card with toggle switches

### Better User Experience

* Status vocabulary unified across the header dot, dashboard cards, and
  tray icon: 🟢 Monitoring · 🟡 Connecting · 🔴 Disconnected · 🟠 Recovery Mode
* Slim indeterminate progress bar during Connecting/Recovery instead of a
  frozen-looking UI
* Live Activity Log gained Search, Save (to .txt), and an Auto-scroll toggle

### Stability Improvements

* Shutdown now driven by a `threading.Event` — Stop/Exit interrupt sleeps
  immediately instead of waiting out the check interval
* `SoundManager` and `GuardianNotifier` no longer crash the app if their
  OS backend is unavailable or playback/notify fails
* System tray import failures (any platform/backend issue) degrade to
  "tray unavailable" instead of crashing Guardian at startup

### Project Structure

* Added `src/system/` — `tray.py`, `startup.py`, `updater.py`
* Removed dead/unused `src/gui/settings_window.py` (superseded by the
  embedded Settings panel, referenced undefined theme constants)

---

# 🚀 v0.4.0 - Analytics & Reports Release

## New Features

### Network Analytics Dashboard

* Added a dedicated Analytics page in the desktop app
* Added daily summary cards for Monitoring Time, 5G Active Time, 4G Risk Time, Network Switches, 5G Uptime, and Last 4G Drop

### Session History

* Tracks each monitoring session
* Saves session start and end time
* Calculates total duration
* Calculates 5G, 4G, and unknown network time
* Counts network switches per session

### Network Timeline

* Records monitoring start and stop events
* Records every network change
* Shows today's latest timeline events inside the app

### Export Reports

* Exports today's summary as a TXT report
* Exports today's session history as a CSV file
* Stores reports under `exports/`

---

# 🚀 v0.3.0 — Desktop GUI Release

## ✨ New Features

### Modern Desktop Interface

* Introduced a modern desktop application built with **CustomTkinter**
* Dark theme user interface
* Sidebar navigation
* Dashboard screen
* Settings page
* Live activity log
* Status cards for:

  * Device Status
  * Network Status
  * ADB Connection
  * Last Network Change

---

### GUI Architecture

* Added dedicated **GUI layer**
* Introduced **GuardianController** as the bridge between GUI and backend
* Theme management system
* Reusable GUI widgets
* Separate GUI entry point (`run_gui.py`)
* CLI version preserved (`run.py`)

---

### Project Structure

* Added `src/gui/`
* Organized GUI components into dedicated modules
* Improved project scalability and maintainability

---

### Improvements

* Cleaner modular architecture
* Better separation between backend and frontend
* Improved project organization
* Enhanced user experience through graphical interface

---

### Known Limitations

* Minor GUI synchronization issues during Start/Stop operations
* Callback system planned for future refinement
* Additional GUI optimizations planned for upcoming releases

---

# 🚀 v0.2.0 — Recovery Mode & Auto IP Detection

## ✨ New Features

### Configuration Management

* Introduced `ConfigManager`
* Centralized configuration using `config/config.json`
* Removed hardcoded settings

---

### Smart Recovery Mode

When the saved wireless IP fails:

* Displays recovery instructions
* Waits indefinitely for USB connection
* Detects connected Android device
* Enables ADB over TCP/IP
* Detects latest hotspot IP
* Updates configuration automatically
* Reconnects wirelessly
* Resumes monitoring without restarting

---

### Automatic Recovery

* Mid-session recovery when wireless ADB disconnects
* Automatic reconnection
* Automatic IP synchronization
* Configuration and in-memory target remain synchronized

---

### Startup Flow

1. Attempt wireless connection using saved IP
2. If successful → Start monitoring
3. If connection fails → Enter Recovery Mode
4. USB connected → Auto recovery → Resume monitoring

---

# 🚀 v0.1.0 — Initial Stable CLI Release

## ✨ Initial Features

* Real-time 4G / 5G network monitoring
* Android Debug Bridge (ADB) integration
* Wireless ADB support
* Desktop notifications
* Sound alerts
* Event logging
* Command-line interface
* Modular backend architecture

---

## 🛣 Roadmap

### v1.0.0

* Production Release
* Windows Installer
* Stable GUI Framework
* Complete Documentation
* Performance Optimizations

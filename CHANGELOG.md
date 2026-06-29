# CHANGELOG

All notable changes to **Airtel 5G Guardian** will be documented in this file.

This project follows a simple versioning approach where each release introduces new features, architectural improvements, and stability enhancements.

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

### v0.4.0

* Network Analytics Dashboard
* Session History
* Daily Statistics
* Charts & Visualizations
* Export Reports

### v0.5.0

* System Tray Integration
* Auto Start with Windows
* Automatic Updates
* Multi-device Support

### v1.0.0

* Production Release
* Windows Installer
* Stable GUI Framework
* Complete Documentation
* Performance Optimizations

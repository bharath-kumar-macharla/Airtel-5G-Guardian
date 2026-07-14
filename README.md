# 🚀 Airtel 5G Guardian

> **A modern Windows desktop application that monitors your Android hotspot's network in real time and instantly alerts you whenever your device switches between 5G and 4G.**

---

# 📖 Overview

**Airtel 5G Guardian** is a Python-based desktop application designed to help Airtel users protect their Unlimited 5G data while using their Android phone as a hotspot.

The application communicates directly with your Android device using **Android Debug Bridge (ADB)** and continuously monitors the mobile network state.

Whenever your device switches from **5G** to **4G**, Guardian immediately notifies you through desktop notifications, sound alerts, and a live dashboard.

Version **v0.4.0** added daily network intelligence with analytics, session history, timeline events, and exportable reports. Version **v0.5.0** introduced system tray integration, launch-with-Windows, smart startup, and an automatic update checker. Version **v1.0.0** is the first stable public release — production-ready, fully packaged, and completely documented.

---

# ✨ Features

## 📶 Real-Time Network Monitoring

* Detects 5G and 4G transitions instantly
* Monitors Android telephony information continuously
* Prevents unnoticed consumption of daily mobile data

---

## 🖥️ Modern Desktop GUI (New in v0.3.0)

* Modern CustomTkinter interface
* Sidebar navigation
* Dashboard view
* Settings page
* Live monitoring controls
* Dark theme

---

## 📊 Network Analytics (New in v0.4.0)

* Daily monitoring summary
* 5G active time
* 4G risk time
* Network switch count
* 5G uptime percentage
* Last 4G drop time
* Network timeline
* TXT and CSV report exports

---

## 🚀 Production Release (New in v1.0.0)

* First-launch setup wizard guides new users through configuration
* About dialog with version info and GitHub link
* Improved error messages with actionable connection failure guidance
* Exit confirmation when monitoring is active
* PyInstaller Windows EXE packaging support
* Inno Setup Windows installer script
* Complete documentation: INSTALLATION, USER_GUIDE, TROUBLESHOOTING, ROADMAP
* MIT License

---

## 🛡️ Background Service Mode (New in v0.5.0)

* System tray integration — closing the window minimizes to tray, monitoring keeps running
* Tray menu: Start / Stop Monitoring, Open Dashboard, Settings, Exit
* Launch Guardian automatically when Windows starts
* Smart Startup — auto-resumes the last monitoring session with no clicks
* Automatic update checker against GitHub releases
* Settings: Browse ADB, Test Connection, full input validation
* Unified status indicators (🟢 Monitoring · 🟡 Connecting · 🔴 Disconnected · 🟠 Recovery Mode)
* Log search, save-to-file, and auto-scroll toggle

---

## 📡 Wireless ADB Support

* Wireless Android Debug Bridge connection
* Automatic reconnection
* USB required only for recovery

---

## 🩺 Smart Recovery Mode

If the saved wireless connection fails Guardian will:

* Wait for USB connection
* Enable ADB over TCP/IP
* Detect the latest phone IP
* Update configuration automatically
* Reconnect wirelessly
* Resume monitoring

---

## ⚙️ Configuration Management

Guardian uses a centralized configuration system.

Settings include:

* ADB executable path
* Phone IP
* ADB Port
* Monitoring interval
* Notification preferences

---

## 🔔 Desktop Notifications

Receive instant Windows notifications whenever:

* Connected to 5G
* Switched to 4G

---

## 🔊 Sound Alerts

Different notification sounds for:

* 5G Connected
* 4G Connected

---

## 📝 Live Activity Log

The desktop application displays:

* Monitoring started
* Connection established
* Network changes
* Recovery events
* Monitoring stopped

in real time.

---

## 📂 Event Logging

Guardian also saves events into log files for future reference.

---

# 🏗 Architecture

```text
Airtel-5G-Guardian/

assets/
config/
data/
exports/
logs/

src/

├── core/
│   ├── adb_manager.py
│   └── network_monitor.py
│
├── gui/
│   ├── app.py
│   └── theme.py
│
├── services/
│   ├── analytics.py
│   ├── logger.py
│   ├── notifier.py
│   └── sound_manager.py
│
├── system/
│   ├── tray.py
│   ├── startup.py
│   └── updater.py
│
├── config.py
├── main.py
└── utils.py

run.py
run_gui.py
```

---

# 🛠 Technologies Used

* Python 3.11
* CustomTkinter
* Android Debug Bridge (ADB)
* Windows Notifications
* JSON Configuration
* Git
* GitHub

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/bharath-kumar-macharla/Airtel-5G-Guardian.git

cd Airtel-5G-Guardian
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

Activate

### Windows

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 📦 Requirements

* Windows 10 / Windows 11
* Python 3.11+
* Android Phone
* Android Platform Tools (ADB)

System tray integration uses `pystray` + `Pillow` (see `requirements.txt`).
If either is missing, Guardian degrades gracefully — the window simply
closes on the (X) button instead of minimizing to tray.

---

# ⚙ Initial Configuration

Open

```text
config/config.json
```

Update the following values:

```json
{
    "adb": {
        "path": "C:\\platform-tools\\platform-tools\\adb.exe",
        "phone_ip": "YOUR_PHONE_IP",
        "port": 5555
    }
}
```

Change:

* `path` → Your ADB executable
* `phone_ip` → Your phone's hotspot IP
* `port` → Default is 5555

---

# 📱 Android Setup

Enable:

* Developer Options
* USB Debugging

For the first connection:

1. Connect via USB
2. Enable ADB TCP/IP
3. Connect wirelessly
4. Disconnect USB
5. Launch Guardian

---

# ▶ Running the Application

## GUI Version

```bash
python run_gui.py
```

## CLI Version

```bash
python run.py
```

---

# 🚀 Current Version

## v1.0.0 — Stable Public Release

### ✅ All Features

* First-Launch Setup Wizard
* About Dialog
* Improved Error Messages
* Exit Confirmation while Monitoring
* PyInstaller EXE Packaging
* Inno Setup Windows Installer
* System Tray Integration
* Launch with Windows
* Smart Startup (auto-resume monitoring)
* Automatic Update Checker
* Settings: Browse ADB, Test Connection, input validation
* Unified status indicators + progress bar
* Log search, save, and auto-scroll
* Network Analytics Dashboard
* Today Summary Cards
* Session History
* Network Timeline
* Daily Statistics
* Export Reports (TXT + CSV)
* Modern Desktop GUI
* Sidebar Navigation
* Dashboard
* Theme Management
* Real-Time Monitoring
* Wireless ADB
* Smart Recovery Mode
* Live Activity Log
* Desktop Notifications
* Sound Alerts
* Configuration Management

---

# 🗺 Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full roadmap.

## v1.1.0

* Custom branded app icon
* Dark/Light theme toggle
* Log file viewer
* Notification sound customization

## v1.2.0

* Weekly analytics summary
* Session detail view
* Uptime streak tracking

## v2.0.0

* Multi-device support
* Charts and visualizations
* Network quality scoring

# 📚 Documentation

* [Installation Guide](docs/INSTALLATION.md)
* [User Guide](docs/USER_GUIDE.md)
* [Troubleshooting](docs/TROUBLESHOOTING.md)
* [Roadmap](docs/ROADMAP.md)
* [Changelog](CHANGELOG.md)
* [Contributing](CONTRIBUTING.md)

---

# 🤝 Contributing

Suggestions, feature requests and pull requests are always welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

# 👨‍💻 Author

**Macharla Bharath Kumar**

Building practical software that solves real-world problems while learning software engineering through hands-on development.

---

## ⭐ If you found this project interesting

Consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

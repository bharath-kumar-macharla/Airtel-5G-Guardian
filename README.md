# 🚀 Airtel 5G Guardian

> **A modern Windows desktop application that monitors your Android hotspot's network in real time and instantly alerts you whenever your device switches between 5G and 4G.**

---

# 📖 Overview

**Airtel 5G Guardian** is a Python-based desktop application designed to help Airtel users protect their Unlimited 5G data while using their Android phone as a hotspot.

The application communicates directly with your Android device using **Android Debug Bridge (ADB)** and continuously monitors the mobile network state.

Whenever your device switches from **5G** to **4G**, Guardian immediately notifies you through desktop notifications, sound alerts, and a live dashboard.

Version **v0.4.0** adds daily network intelligence with analytics, session history, timeline events, and exportable reports.

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
logs/
sounds/

src/

├── core/
│   ├── adb_manager.py
│   └── network_monitor.py
│
├── gui/
│   ├── app.py
│   ├── settings_window.py
│   └── theme.py
│
├── services/
│   ├── logger.py
│   ├── notifier.py
│   └── sound_manager.py
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

## v0.4.0

### ✅ Completed

* Network Analytics Dashboard
* Today Summary Cards
* Session History
* Network Timeline
* Daily Statistics
* Export Reports
* Modern Desktop GUI
* Sidebar Navigation
* Dashboard
* Settings Window
* Theme Management
* Controller Architecture
* Real-Time Monitoring
* Wireless ADB
* Smart Recovery Mode
* Live Activity Log
* Desktop Notifications
* Sound Alerts
* Configuration Management

---

# 🗺 Roadmap

## v0.5.0

* Charts and Visualizations
* System Tray
* Auto Start
* Multi-device Support
* Automatic Updates

## v1.0.0

* Windows Installer
* Production Release
* Complete Documentation
* Stable GUI Framework

---

# 🤝 Contributing

Suggestions, feature requests and pull requests are always welcome.

---

# 👨‍💻 Author

**Macharla Bharath Kumar**

Building practical software that solves real-world problems while learning software engineering through hands-on development.

---

## ⭐ If you found this project interesting

Consider giving the repository a ⭐ on GitHub.

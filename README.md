# 🚀 Airtel 5G Guardian

> **A smart Windows desktop utility that monitors your Android hotspot's network status in real time and protects your Airtel Unlimited 5G data.**

---

## 📖 Overview

**Airtel 5G Guardian** is a Python-based desktop application that continuously monitors your Android phone's network while it is being used as a hotspot.

If your phone silently switches from **5G** to **4G**, Guardian immediately alerts you through desktop notifications and sound alerts, helping you avoid unwanted consumption of your daily data quota.

The application communicates directly with your Android device using **Android Debug Bridge (ADB)** and is designed with a modular architecture for future expansion.

---

# ✨ Features

## 📶 Real-Time Network Monitoring

* Detects 5G and 4G transitions instantly
* Monitors Android telephony information in real time
* Prevents unnoticed data usage

---

## 📡 Wireless ADB Support

* Connects to your phone wirelessly
* No USB cable required during normal monitoring
* Automatic wireless connection on startup

---

## 🩺 Smart Recovery Mode (v0.2.0)

If the saved wireless connection fails:

* Automatically enters Recovery Mode
* Waits for USB connection
* Enables ADB TCP/IP mode
* Detects the phone's latest hotspot IP
* Updates the configuration automatically
* Reconnects wirelessly
* Resumes monitoring without restarting the application

---

## ⚙️ Configuration Management (v0.2.0)

* Centralized `config.json`
* ConfigManager for managing application settings
* Easily configurable:

  * ADB path
  * Phone IP
  * ADB port
  * Check interval
  * Reconnect settings
  * Notification preferences

---

## 🔔 Notifications

* Windows desktop notifications
* Instant alerts for:

  * Connected to 5G
  * Switched to 4G

---

## 🔊 Sound Alerts

Different sound notifications for:

* 5G Connected
* 4G Connected

---

## 📝 Event Logging

Guardian records important events including:

* Application Started
* Monitoring Started
* Connected to 5G
* Switched to 4G
* Recovery Mode
* Monitoring Stopped

---

## 🏗️ Modular Architecture

```text
src/
│
├── core/
│   ├── adb_manager.py
│   └── network_monitor.py
│
├── services/
│   ├── logger.py
│   ├── notifier.py
│   └── sound_manager.py
│
├── config.py
└── main.py
```

---

# 🛠 Technologies

* Python 3.11
* Android Debug Bridge (ADB)
* Windows Notifications
* JSON Configuration
* Git & GitHub

---

# 🚀 Current Version

## v0.2.0

### ✅ Completed

* Real-time network monitoring
* Wireless ADB support
* Smart Recovery Mode
* Automatic IP detection
* Automatic configuration update
* Desktop notifications
* Sound alerts
* Event logging
* ConfigManager
* Modular project architecture

---

# 🗺️ Roadmap

## v0.3.0

* Modern GUI (CustomTkinter)
* Live network dashboard
* Settings window
* Start/Stop monitoring
* Dark mode

## v0.4.0

* Statistics dashboard
* Network history
* Export logs

## v1.0.0

* Windows installer
* System tray integration
* Auto startup
* Production-ready release

---

# 👨‍💻 Author

**Macharla Bharath Kumar**

Building practical software to solve real-world problems while learning software engineering.

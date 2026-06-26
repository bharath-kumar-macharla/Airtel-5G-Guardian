# 📶 Airtel 5G Guardian

> Never lose your Airtel Unlimited 5G without knowing.

Airtel 5G Guardian is a Python desktop utility that continuously monitors an Android phone's network connection using ADB. It detects when the phone switches between **5G** and **4G**, helping users avoid unintentionally consuming their daily mobile data.

This project was built to solve a real-world problem. When using a phone as a hotspot, Airtel Unlimited 5G works only while the phone remains connected to a 5G network. If the signal drops to 4G, the daily data balance starts getting consumed. Airtel 5G Guardian immediately detects this change and alerts the user.

---

Why I Built This ?
I frequently use my Android phone as a hotspot. Airtel provides unlimited data only while connected to 5G. When the network silently drops to 4G, my daily data gets consumed without me noticing. Existing tools didn't solve this specific problem, so I built Airtel 5G Guardian to monitor network changes in real time and alert me immediately.

---
## ✨ Features

* 📡 Real-time 4G / 5G monitoring
* 📱 Supports Android devices using ADB
* 🌐 Wireless ADB support (no USB required after setup)
* 🔔 Desktop notifications on network changes
* 🔊 Sound alerts
* 📝 Event logging
* 🏗️ Modular project architecture
* ⚡ Lightweight and easy to run

---

## 🛠️ Tech Stack

* Python 3.11+
* Android Debug Bridge (ADB)
* Plyer (Desktop Notifications)
* Winsound (System Alerts)
* Git

---

## 📂 Project Structure

```text
Airtel-5G-Guardian/
│
├── run.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── logs/
├── assets/
├── sounds/
│
└── src/
    ├── config.py
    ├── utils.py
    ├── main.py
    │
    ├── core/
    │   ├── adb_manager.py
    │   └── network_monitor.py
    │
    └── services/
        ├── logger.py
        ├── notifier.py
        └── sound_manager.py
```

---

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Airtel-5G-Guardian.git
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure ADB

Update the ADB path in `src/config.py`.

### Start the application

```bash
python run.py
```

---

## 🧪 Current Status

### Version 0.1.0

* ✅ Wireless ADB support
* ✅ Accurate 4G/5G detection
* ✅ Desktop notifications
* ✅ Logging
* ✅ Sound alerts
* 🔄 More features under development

---

## 🗺️ Roadmap

* [ ] Automatic ADB reconnect
* [ ] Modern GUI (CustomTkinter)
* [ ] System tray integration
* [ ] Daily usage statistics
* [ ] Signal strength monitoring
* [ ] Auto-start with Windows
* [ ] One-click executable (.exe)

---

## 🤝 Contributing

Contributions, suggestions, and feature requests are welcome.

Feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Macharla Bharath Kumar**

Built with ❤️ to solve a real-world mobile hotspot problem.

# Installation Guide — Airtel 5G Guardian v1.0.0

This guide covers installation from source. For the Windows installer, see the [Releases](https://github.com/bharath-kumar-macharla/Airtel-5G-Guardian/releases) page.

---

## System Requirements

| Requirement | Details |
|-------------|---------|
| Operating System | Windows 10 / Windows 11 |
| Python | 3.11 or newer |
| Android Phone | Any Android device with USB Debugging support |
| ADB | Android Platform Tools (free from Google) |

---

## Step 1 — Install Python

Download Python 3.11+ from [python.org](https://www.python.org/downloads/).

During installation, check **"Add Python to PATH"**.

Verify:
```bash
python --version
```

---

## Step 2 — Download Android Platform Tools (ADB)

1. Go to [developer.android.com/tools/releases/platform-tools](https://developer.android.com/tools/releases/platform-tools)
2. Download **Platform Tools for Windows**
3. Extract to a folder, e.g. `C:\platform-tools\`
4. Note the full path to `adb.exe` — you'll need it in the configuration step.

---

## Step 3 — Clone the Repository

```bash
git clone https://github.com/bharath-kumar-macharla/Airtel-5G-Guardian.git
cd Airtel-5G-Guardian
```

---

## Step 4 — Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:
```bash
.venv\Scripts\activate
```

Your terminal prompt should now show `(.venv)`.

---

## Step 5 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `customtkinter` — modern desktop UI framework
- `plyer` — Windows desktop notifications
- `pystray` — system tray integration
- `Pillow` — tray icon rendering

---

## Step 6 — Configure the Application

Open `config/config.json` in a text editor:

```json
{
    "adb": {
        "path": "C:\\platform-tools\\adb.exe",
        "phone_ip": "192.168.43.1",
        "port": 5555
    }
}
```

Update:
- `path` → the full path to your `adb.exe`
- `phone_ip` → your phone's hotspot IP address

> **Tip:** You can also set these values from the Settings page inside Guardian — it's easier.

---

## Step 7 — Prepare Your Android Phone

1. Open **Settings → About Phone** and tap Build Number 7 times to enable Developer Options.
2. Go to **Settings → Developer Options** and enable:
   - **USB Debugging**
3. Connect your phone via USB and accept the ADB authorization prompt on your phone.

Enable Wireless ADB (one-time setup):
```bash
adb tcpip 5555
```

Find your phone's hotspot IP:
```bash
adb shell ip addr show wlan1
```
or
```bash
adb shell ip addr show wlan0
```

Then disconnect USB and connect your PC to the phone's hotspot.

---

## Step 8 — Launch Guardian

```bash
python run_gui.py
```

If ADB is not configured, the **First-Time Setup Wizard** will guide you through the process automatically.

---

## Launch at Windows Startup (Optional)

In Guardian's Settings, enable **"Launch Guardian when Windows starts"**. This adds a registry entry under `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` — no administrator rights required.

---

## Next Steps

- [User Guide](USER_GUIDE.md) — learn how to use the dashboard, analytics, and tray
- [Troubleshooting](TROUBLESHOOTING.md) — fix common issues

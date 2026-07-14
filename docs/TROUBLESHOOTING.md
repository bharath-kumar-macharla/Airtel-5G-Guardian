# Troubleshooting — Airtel 5G Guardian v1.0.0

---

## Guardian won't start

**Error: `ModuleNotFoundError: No module named 'customtkinter'`**

You haven't installed the dependencies, or your virtual environment is not activated.

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python run_gui.py
```

---

**Error: `FileNotFoundError: [WinError 2] The system cannot find the file specified`** (when clicking Start Monitoring)

ADB is not found at the configured path.

1. Open **Settings → ADB Path**
2. Click **Browse…** and locate `adb.exe`
3. Click **Save**

---

## Cannot connect to phone

**Symptom:** Clicking Start Monitoring shows "Could not connect" in the log.

| Possible cause | Fix |
|----------------|-----|
| Hotspot is OFF | Enable Mobile Hotspot on your phone |
| Phone IP changed | Check phone's hotspot settings → find the gateway IP |
| Wireless ADB not enabled | Connect USB, run `adb tcpip 5555`, then disconnect |
| USB Debugging disabled | Settings → Developer Options → USB Debugging → ON |
| PC not connected to phone's hotspot | Connect your PC's Wi-Fi to the phone's hotspot |

**Quick test:**
```bash
adb connect <phone_ip>:5555
```
If this fails, the problem is with ADB or your network, not Guardian.

---

## Test Connection says "Device Not Found"

The same fixes as above apply. Additionally:

- Check that the IP address in Settings matches your phone's current hotspot IP.
- Try `adb devices` to see if any device is listed.
- Ensure only one instance of Guardian is running.

---

## Guardian keeps entering Recovery Mode

**Cause:** Your phone's hotspot IP changes frequently (common with DHCP).

**Fix 1:** Set a static IP in your phone's hotspot settings (Android 10+: Hotspot → Advanced → DHCP lease time / Fixed IP).

**Fix 2:** Keep a USB cable nearby. Recovery Mode is automatic — plug in USB and Guardian recovers on its own.

---

## System tray icon does not appear

**Cause:** `pystray` or `Pillow` is not installed.

```bash
pip install pystray Pillow
```

If already installed and still not working:
- Try running as a regular user (not as administrator)
- Ensure you are on Windows 10 or 11

Without tray support, Guardian still works normally — the (X) button will close the app instead of minimizing.

---

## Desktop notifications not showing

**Cause:** Windows notification settings or `plyer` issue.

1. Open **Windows Settings → System → Notifications**
2. Ensure notifications are ON for Python or for Airtel 5G Guardian.
3. Check that `plyer` is installed: `pip install plyer`

Sound alerts will still play even if desktop notifications are disabled.

---

## Sounds not playing

Sound alerts use Windows system sounds (`SystemAsterisk`, `SystemExclamation`).

If they are silent:
- Check that your PC is not muted
- Check Windows sound settings
- Try: `Start → Settings → System → Sound → System sounds`

---

## Application freezes

Guardian's monitoring loop runs in a background thread and should never block the GUI.

If the window becomes unresponsive:
- Wait a few seconds — it may be connecting or recovering.
- If still frozen, use the system tray → **❌ Exit** to close cleanly.

If this happens repeatedly, please [open an issue](https://github.com/bharath-kumar-macharla/Airtel-5G-Guardian/issues) with the contents of `logs/guardian.log`.

---

## Settings won't save

**Error: `config.json` is read-only**

```bash
attrib -r config\config.json
```

**Error: numbers-only fields contain letters**

Port, Check Interval, Notification Timeout, and Reconnect Attempts must be positive whole numbers.

---

## Analytics show 0 seconds / nothing

Analytics only track sessions started from the current day. Start monitoring for at least a few seconds, then check Analytics.

---

## Export Report fails

Guardian writes reports to `exports/`. Make sure:
- The `exports/` directory exists (created automatically by Guardian)
- You have write permission to the project folder

---

## config.json is missing / corrupted

Guardian will fall back to built-in defaults and display a warning in the log.

The First-Time Setup Wizard will appear on next launch to create a fresh config.

You can also create a new `config/config.json` manually — refer to the sample in [INSTALLATION.md](INSTALLATION.md).

---

## Still stuck?

[Open an issue on GitHub](https://github.com/bharath-kumar-macharla/Airtel-5G-Guardian/issues) and include:
- Your Guardian version (shown in the sidebar)
- Your OS version
- The contents of `logs/guardian.log`
- The error message shown in the Live Activity Log

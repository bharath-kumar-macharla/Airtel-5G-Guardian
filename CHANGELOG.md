# CHANGELOG

## v0.2.0 — Recovery Mode & Auto IP Detection

### New Features

  - `ConfigManager` — all settings from `config/config.json`
  - Auto-reconnect on connection drop
  - `config/config.json` — single file for all settings
  - **Recovery Mode** — when saved IP fails, instead of exiting:
    - Prints clear instructions to plug in USB
    - Polls for USB device every 3 seconds (indefinitely)
    - Once USB detected → enables TCP/IP → reads new IP → updates config.json → reconnects wirelessly
    - Resumes monitoring automatically — no manual commands needed
  - **Mid-session recovery** — if connection drops while monitoring, Recovery Mode kicks in automatically
  - **Auto IP sync** — config.json and in-memory target always updated together

### Startup Flow
1. Try saved IP wirelessly
2. Success → monitor
3. Fail → Recovery Mode (wait for USB)
4. USB plugged → auto fix → reconnect → monitor

---

## v0.1.0 — Stable CLI

### Features
- Real-time 4G / 5G monitoring via ADB
- Wireless ADB, desktop notifications, sound alerts, logging

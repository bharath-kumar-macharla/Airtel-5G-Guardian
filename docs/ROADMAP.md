# Roadmap — Airtel 5G Guardian

---

## ✅ v1.0.0 — Stable Public Release (Current)

**Theme:** Production-ready, stable, documented.

### Completed
- Real-time 5G / 4G monitoring via wireless ADB
- Smart Recovery Mode (USB auto-reconnect, IP auto-update)
- Modern desktop GUI (CustomTkinter, dark theme)
- Dashboard with live status cards and activity log
- Network Analytics with daily session tracking
- TXT and CSV report exports
- System tray integration (minimize, monitoring continues in background)
- Launch with Windows (per-user registry, no admin required)
- Smart Startup (auto-resume last session on launch)
- Automatic update checker against GitHub releases
- About dialog
- First-launch setup wizard
- Improved error messages with actionable guidance
- Exit confirmation when monitoring is active
- PyInstaller EXE packaging
- Inno Setup Windows installer script
- Complete documentation (INSTALLATION, USER_GUIDE, TROUBLESHOOTING)
- MIT License

---

## 🗺 v1.1.0 — Quality of Life

**Theme:** Refine the experience without adding complexity.

### Planned
- **Custom .ico application icon** — replace the generated tray icon with a proper branded icon
- **Dark/Light theme toggle** — respect Windows system theme preference
- **Log file viewer** — view `logs/guardian.log` from inside the app
- **Notification sound customization** — let users choose or disable sounds per event
- **Connection retry indicator** — show reconnect attempt count in the status card

---

## 🗺 v1.2.0 — Analytics Enhancements

**Theme:** Richer data without a charting library dependency.

### Planned
- **Weekly summary view** — review analytics for any day this week
- **Session detail view** — expand any session to see its full event timeline
- **Uptime streak** — track consecutive days of 90%+ 5G uptime
- **CSV history browser** — view past exported CSVs from within the app

---

## 🗺 v2.0.0 — Multi-Device & Charts

**Theme:** Scale to power users.

### Planned
- **Multi-device support** — monitor multiple phones simultaneously
- **Charts and visualizations** — matplotlib-powered uptime graphs
- **Network quality scoring** — composite score based on 5G uptime, switches, and duration
- **Scheduled monitoring** — start/stop monitoring at specific times
- **REST API** — optional local HTTP endpoint for integration with other tools

---

## Ideas Under Consideration

These are not committed to any version:

- Android widget / companion app
- Automatic 5G re-enable (ADB shell command when 4G is detected)
- Email / webhook alerts
- Network event webhook (for integration with Home Assistant, IFTTT, etc.)

---

> Have a feature request? [Open an issue](https://github.com/bharath-kumar-macharla/Airtel-5G-Guardian/issues) on GitHub.

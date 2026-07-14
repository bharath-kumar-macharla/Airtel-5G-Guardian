# Airtel 5G Guardian — v1.0.0 Release Checklist

Use this checklist before tagging `v1.0.0` and creating the GitHub release.

---

## 1. Code

- [ ] `src/config.py` — `APP_VERSION = "1.0.0"`
- [ ] `config/config.json` — `app.version = "1.0.0"`
- [ ] `config/config.json` — `update_repo` points to real GitHub path
- [ ] No placeholder strings remaining (`your-github-username`, `TODO`, `FIXME`)
- [ ] All imports resolve without errors (`python -c "from src.gui.app import GuardianApp"`)
- [ ] `NetworkMonitor` receives `adb_manager=self._adb` in `_start()`
- [ ] No module-level ADB/Config singletons instantiated at import time

---

## 2. Features

- [ ] **Monitoring** — Start → connect → 5G/4G changes logged correctly
- [ ] **Recovery Mode** — Disconnect phone Wi-Fi → USB plug → auto-recovery completes
- [ ] **Analytics** — Navigate to Analytics → all six cards refresh with correct values
- [ ] **Export Reports** — Click Export Report → `.txt` and `.csv` created in `exports/`
- [ ] **System Tray** — Minimize to tray → monitoring continues → restore from tray menu
- [ ] **Settings** — Change phone IP → Save → `config.json` updated → ADB reconnects
- [ ] **Update Checker** — Toggle off → no crash; toggle on → background check runs
- [ ] **Application Exit** — Exit while monitoring → confirmation dialog appears
- [ ] **Background Monitoring** — Window minimized to tray → monitoring thread still alive
- [ ] **Config Loading** — Rename `config.json` → relaunch → first-launch wizard appears
- [ ] **Config Saving** — Change settings → Save → verify all fields written to `config.json`
- [ ] **About Dialog** — Click ℹ About → correct version, developer, GitHub button works
- [ ] **Setup Wizard** — Clear ADB path in config → relaunch → wizard appears and saves
- [ ] **Log Search** — Type in search box → log filters correctly
- [ ] **Log Save** — Click Save → file dialog → `.txt` saved with correct content
- [ ] **Auto-scroll** — Uncheck Auto-scroll → new entries don't scroll; recheck → scrolls again
- [ ] **Restore Defaults** — Click Restore Defaults → all fields reset to factory values

---

## 3. Stability

- [ ] Start and stop monitoring 5+ times — no crashes, no thread leaks
- [ ] Run for 10+ minutes — memory usage stable
- [ ] Close window (X) while monitoring → minimizes to tray (if minimize_to_tray is ON)
- [ ] Close window (X) while monitoring with tray disabled → exit dialog appears
- [ ] Exit from tray → confirmation dialog if monitoring; app closes cleanly

---

## 4. Packaging

- [ ] `Airtel-5G-Guardian.spec` is present at project root
- [ ] `pyinstaller Airtel-5G-Guardian.spec --clean` completes without errors
- [ ] `dist/Airtel-5G-Guardian.exe` launches correctly (no console window)
- [ ] EXE creates `config/`, `data/`, `exports/`, `logs/` beside itself on first run
- [ ] Settings can be saved from EXE (writes `config.json` beside `.exe`)
- [ ] Analytics exports to `exports/` beside `.exe`

---

## 5. Installer

- [ ] `installer/Airtel5GGuardian.iss` is present
- [ ] Inno Setup compiles the script without errors
- [ ] Installer runs silently (per-user, no UAC prompt)
- [ ] Desktop shortcut created (when selected)
- [ ] Start Menu shortcut created
- [ ] Uninstaller works and prompts before deleting user data

---

## 6. Documentation

- [ ] `README.md` — version references updated to v1.0.0
- [ ] `CHANGELOG.md` — v1.0.0 section at the top
- [ ] `LICENSE` — present (MIT)
- [ ] `CONTRIBUTING.md` — present
- [ ] `docs/INSTALLATION.md` — present and accurate
- [ ] `docs/USER_GUIDE.md` — present and covers all features
- [ ] `docs/TROUBLESHOOTING.md` — present
- [ ] `docs/ROADMAP.md` — v1.0.0 marked complete, future plans listed
- [ ] `docs/development/V1_IMPLEMENTATION_PROMPT.md` — present
- [ ] `docs/development/V1_RELEASE_CHECKLIST.md` — present (this file)
- [ ] `docs/development/PACKAGING_GUIDE.md` — present

---

## 7. Repository

- [ ] `.gitignore` excludes: `__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `build/`, `*.spec` output artifacts
- [ ] No secrets or personal data committed (API keys, phone IPs, etc.)
- [ ] `data/events.json` and `data/sessions.json` are in `.gitignore` or cleared
- [ ] `exports/` is in `.gitignore` or cleared of personal reports
- [ ] All changes committed on `main` branch

---

## 8. GitHub Release

- [ ] Tag created: `v1.0.0`
- [ ] Release title: `Airtel 5G Guardian v1.0.0 — First Stable Release`
- [ ] `Airtel-5G-Guardian.exe` attached to release
- [ ] `Airtel5GGuardian-Setup-1.0.0.exe` attached to release (if installer compiled)
- [ ] Release notes summarize v1.0.0 changes (copy from `CHANGELOG.md`)

---

> Complete every item before publishing the release. Leave nothing unchecked.

# Packaging Guide — Airtel 5G Guardian

This guide explains how to build the Windows EXE and create the Windows installer.

---

## Prerequisites

| Tool | Purpose | Download |
|------|---------|---------|
| Python 3.11+ | Runtime | [python.org](https://www.python.org/downloads/) |
| PyInstaller 6+ | Build EXE | `pip install pyinstaller` |
| Inno Setup 6 | Build installer | [jrsoftware.org](https://jrsoftware.org/isinfo.php) |
| UPX (optional) | Compress EXE | [upx.github.io](https://upx.github.io/) |

---

## Step 1 — Install Build Dependencies

```bash
# Activate your virtual environment first
.venv\Scripts\activate

# Install runtime + build deps
pip install -r requirements.txt
pip install pyinstaller
```

---

## Step 2 — Build the EXE

From the project root:

```bash
pyinstaller Airtel-5G-Guardian.spec --clean
```

**Output:** `dist\Airtel-5G-Guardian.exe`

### What the spec does

- **One-file bundle** — everything packed into a single `.exe`
- **No console window** — `console=False` so no terminal flashes on launch
- **Bundled assets** — `config/config.json` (template), `assets/`, `sounds/`
- **Hidden imports** — `customtkinter`, `pystray`, `plyer`, `winsound`, `winreg`

### Path resolution (frozen vs source)

`src/config.py` exposes two helpers:

| Function | Returns |
|----------|---------|
| `get_base_path()` | `sys._MEIPASS` when frozen, project root otherwise |
| `get_data_path()` | Directory beside `.exe` when frozen, project root otherwise |

- **Read-only assets** (bundled config template, sounds, icons) → `get_base_path()`
- **User-writable data** (`data/`, `exports/`, `logs/`) → `get_data_path()`

This means session data and exports persist beside the `.exe` between updates.

---

## Step 3 — Test the EXE

```bash
dist\Airtel-5G-Guardian.exe
```

Verify:
- [ ] Window opens with no console
- [ ] Version in sidebar shows `1.0.0`
- [ ] `config/`, `data/`, `exports/`, `logs/` are created beside the `.exe`
- [ ] Settings can be saved (writes `config.json` beside `.exe`)
- [ ] Analytics export creates files in `exports/` beside `.exe`
- [ ] System tray icon appears
- [ ] App exits cleanly from tray menu

---

## Step 4 — Build the Windows Installer

### 4a. Ensure the EXE is built

```bash
pyinstaller Airtel-5G-Guardian.spec --clean
```

### 4b. Add an app icon (optional but recommended)

Create `assets/guardian.ico` (256×256 ICO with multiple sizes).

Uncomment this line in `Airtel-5G-Guardian.spec`:
```python
# icon="assets/guardian.ico",
```

And this line in `installer/Airtel5GGuardian.iss`:
```ini
SetupIconFile = ..\assets\guardian.ico
```

### 4c. Compile the installer

1. Open **Inno Setup Compiler**
2. Open `installer/Airtel5GGuardian.iss`
3. Press **F9** (Build) or **Compile** from the menu

**Output:** `installer\Output\Airtel5GGuardian-Setup-1.0.0.exe`

---

## Step 5 — Test the Installer

1. Run `Airtel5GGuardian-Setup-1.0.0.exe`
2. Verify:
   - [ ] No UAC prompt (per-user install)
   - [ ] Installs to `%LOCALAPPDATA%\Programs\Airtel 5G Guardian\`
   - [ ] Start Menu shortcut created
   - [ ] Desktop shortcut created (if selected during install)
   - [ ] App launches from shortcut
   - [ ] Uninstaller listed in Windows Settings → Apps
   - [ ] Uninstall prompts before deleting user data

---

## Updating the Version

When releasing a new version, update these locations:

| File | Field |
|------|-------|
| `src/config.py` | `APP_VERSION = "X.Y.Z"` |
| `config/config.json` | `"version": "X.Y.Z"` |
| `installer/Airtel5GGuardian.iss` | `#define AppVersion "X.Y.Z"` |
| `CHANGELOG.md` | New version section at the top |
| `README.md` | Current version section |
| `docs/development/V1_RELEASE_CHECKLIST.md` | Copy and adapt for new version |

---

## Build Artifacts

| File | Description | Commit? |
|------|-------------|---------|
| `dist/Airtel-5G-Guardian.exe` | Built EXE | ❌ No |
| `build/` | PyInstaller build cache | ❌ No |
| `installer/Output/` | Compiled installer | ❌ No |
| `Airtel-5G-Guardian.spec` | Spec file (source) | ✅ Yes |
| `installer/Airtel5GGuardian.iss` | Installer script (source) | ✅ Yes |

Add to `.gitignore`:

```gitignore
dist/
build/
installer/Output/
```

---

## Troubleshooting Builds

### `ModuleNotFoundError` at runtime inside the EXE

Add the missing module to `hiddenimports` in `Airtel-5G-Guardian.spec`:

```python
hiddenimports=[
    "your.missing.module",
    ...
],
```

Then rebuild: `pyinstaller Airtel-5G-Guardian.spec --clean`

### `FileNotFoundError` for config/assets inside the EXE

Ensure the file is listed in `datas` in the spec:

```python
datas=[
    ("config/config.json", "config"),
    ("assets", "assets"),
    ("sounds", "sounds"),
],
```

And accessed via `get_base_path()` in code, not `Path("config/config.json")` directly.

### EXE is very large

Install UPX and rebuild — PyInstaller will compress automatically:

```bash
# UPX must be on PATH
pyinstaller Airtel-5G-Guardian.spec --clean
```

### Antivirus flags the EXE

This is a known false positive with PyInstaller bundles. Options:
1. Submit the EXE to the AV vendor for whitelisting
2. Code-sign the EXE with an Authenticode certificate
3. Document this in `docs/TROUBLESHOOTING.md` for users

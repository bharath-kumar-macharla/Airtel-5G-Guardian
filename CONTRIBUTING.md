# Contributing to Airtel 5G Guardian

Thank you for your interest in contributing! This document explains how to get involved.

---

## Code of Conduct

Be respectful. Be constructive. Focus on the problem, not the person.

---

## How to Contribute

### Reporting Bugs

1. Search [existing issues](https://github.com/bharath-kumar-macharla/Airtel-5G-Guardian/issues) to avoid duplicates.
2. Open a new issue with:
   - A clear title
   - Steps to reproduce
   - Expected vs. actual behavior
   - Your OS version, Python version, and Guardian version
   - Relevant log output (from `logs/guardian.log`)

### Suggesting Features

Open an issue with the label **enhancement**. Describe:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

### Pull Requests

1. **Fork** the repository and create a branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow existing architecture** — keep modules in their correct layer:
   - `src/core/` — ADB and network detection
   - `src/gui/` — UI only (no business logic)
   - `src/services/` — analytics, logging, notifications, sounds
   - `src/system/` — tray, startup, update checker
   - `src/config.py` — configuration management

3. **Style guidelines:**
   - Python 3.11+
   - Follow the existing code style (no linter config is enforced, but match the surrounding code)
   - Use type hints where the existing code uses them
   - All threading must be daemon threads — never leave orphan background threads
   - GUI widget access must always be marshalled via `self.after(0, fn)` from background threads

4. **Test your changes** manually:
   - Launch with `python run_gui.py`
   - Verify Start / Stop monitoring works
   - Verify Settings can be saved and reloaded
   - Verify the system tray menu works
   - Verify the app exits cleanly

5. **Commit message format:**
   ```
   Short summary (max 72 chars)

   Optional longer description explaining the why, not the what.
   ```

6. Open a pull request against `main`. Fill in the PR template.

---

## Project Structure

```
src/
  core/        # ADB connection and network detection
  gui/         # CustomTkinter desktop UI
  services/    # Analytics, logging, sound, notifications
  system/      # Tray icon, Windows startup, update checker
  config.py    # Configuration management
  utils.py     # Shared utility functions
config/        # config.json (user configuration)
data/          # Session and event history (auto-generated)
exports/       # Report exports (auto-generated)
logs/          # guardian.log (auto-generated)
```

---

## Development Setup

```bash
git clone https://github.com/bharath-kumar-macharla/Airtel-5G-Guardian.git
cd Airtel-5G-Guardian
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_gui.py
```

---

## Questions?

Open an issue or start a discussion on GitHub.

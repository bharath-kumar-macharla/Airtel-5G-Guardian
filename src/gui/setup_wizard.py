"""
Setup Wizard
------------
v1.0.0 — Shown on first launch when adb.exe cannot be found at the path
          stored in config.json (or when config.json is missing).

The wizard walks the user through four steps:
  1. Locate adb.exe via a file picker (or type the path).
  2. Validate the path exists and ends in adb.exe.
  3. Enter the phone IP address.
  4. Test the connection — then save and close.

On success  → config.json is updated and the caller receives on_complete().
On skip/cancel → the caller receives on_skip() (usually navigates to Settings).
"""

import json
import subprocess
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from src.gui.theme import (
    BG_CONTENT, BG_CARD, BG_INPUT, BORDER, RADIUS,
    BLUE, GREEN, RED, AMBER, ORANGE,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    F_TITLE, F_HEADING, F_BODY, F_SMALL,
    BTN_NEUTRAL, P, P_SM, P_XS,
)


class SetupWizard(ctk.CTkToplevel):
    """
    Modal first-launch configuration wizard.

    Parameters
    ----------
    master : ctk.CTk
        Parent window.
    config_path : Path
        Absolute path to config.json (will be read + written).
    on_complete : callable
        Called with no arguments when the wizard finishes successfully.
    on_skip : callable
        Called with no arguments if the user dismisses the wizard.
    """

    def __init__(self, master, config_path: Path, on_complete, on_skip):
        super().__init__(master)
        self._config_path = config_path
        self._on_complete = on_complete
        self._on_skip = on_skip

        self.title("Airtel 5G Guardian — First-Time Setup")
        self.geometry("520x480")
        self.resizable(False, False)
        self.configure(fg_color=BG_CONTENT)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._skip)

        self._build()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="📶", font=("Segoe UI Emoji", 24)).pack(side="left", padx=(P, P_SM))
        title_col = ctk.CTkFrame(hdr, fg_color="transparent")
        title_col.pack(side="left", pady=P_SM)
        ctk.CTkLabel(title_col, text="Welcome to Airtel 5G Guardian", font=F_TITLE, text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Let's set up your connection before we start.", font=F_SMALL, text_color=TEXT_MUTED).pack(anchor="w")

        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        # Content area
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=P, pady=P)

        # Step 1 — ADB path
        self._section(content, "Step 1 — Locate adb.exe")
        ctk.CTkLabel(
            content,
            text="Android Debug Bridge (adb.exe) is required to communicate with your phone.\n"
                 "It is included in Android Platform Tools from developer.android.com.",
            font=F_SMALL, text_color=TEXT_MUTED, wraplength=460, justify="left",
        ).pack(anchor="w", pady=(0, P_SM))

        adb_row = ctk.CTkFrame(content, fg_color="transparent")
        adb_row.pack(fill="x", pady=(0, P_SM))
        self._adb_entry = ctk.CTkEntry(
            adb_row, placeholder_text=r"C:\platform-tools\adb.exe",
            fg_color=BG_INPUT, border_color=BORDER, text_color=TEXT_PRIMARY,
            font=F_BODY, height=34,
        )
        self._adb_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            adb_row, text="Browse…", width=80, height=34,
            fg_color=BTN_NEUTRAL, hover_color=BORDER,
            text_color=TEXT_SECONDARY, font=F_SMALL,
            command=self._browse_adb,
        ).pack(side="left", padx=(P_XS, 0))

        # Step 2 — Phone IP
        self._section(content, "Step 2 — Phone IP Address")
        ctk.CTkLabel(
            content,
            text="Enter your Android phone's hotspot IP address.\n"
                 "You can find it in your phone's hotspot settings, or Guardian can\n"
                 "auto-detect it when you plug in a USB cable.",
            font=F_SMALL, text_color=TEXT_MUTED, wraplength=460, justify="left",
        ).pack(anchor="w", pady=(0, P_SM))

        self._ip_entry = ctk.CTkEntry(
            content, placeholder_text="192.168.x.x",
            fg_color=BG_INPUT, border_color=BORDER, text_color=TEXT_PRIMARY,
            font=F_BODY, height=34,
        )
        self._ip_entry.pack(fill="x", pady=(0, P_SM))

        # Status label
        self._status = ctk.CTkLabel(content, text="", font=F_SMALL, text_color=AMBER, wraplength=460, justify="left")
        self._status.pack(anchor="w", pady=(0, P_SM))

        # Buttons
        ctk.CTkFrame(self, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")
        btn_bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=56)
        btn_bar.pack(fill="x", side="bottom")
        btn_bar.pack_propagate(False)

        ctk.CTkButton(
            btn_bar, text="Skip — Configure Later",
            fg_color="transparent", hover_color=BORDER,
            text_color=TEXT_MUTED, font=F_SMALL, height=34,
            command=self._skip,
        ).pack(side="left", padx=P, pady=P_SM)

        self._test_btn = ctk.CTkButton(
            btn_bar, text="Test Connection",
            fg_color=BTN_NEUTRAL, hover_color=BORDER,
            text_color=TEXT_SECONDARY, font=F_SMALL, height=34,
            command=self._test_connection,
        )
        self._test_btn.pack(side="right", padx=(0, P_XS), pady=P_SM)

        self._save_btn = ctk.CTkButton(
            btn_bar, text="Save & Continue",
            fg_color=BLUE, hover_color="#2563eb",
            text_color="white", font=F_HEADING, height=34,
            state="disabled",
            command=self._save_and_close,
        )
        self._save_btn.pack(side="right", padx=(0, P_SM), pady=P_SM)

    def _section(self, parent, title: str):
        ctk.CTkLabel(parent, text=title, font=F_HEADING, text_color=TEXT_PRIMARY).pack(anchor="w", pady=(P_SM, P_XS))
        ctk.CTkFrame(parent, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", pady=(0, P_SM))

    # ── Actions ───────────────────────────────────────────────────────────────

    def _browse_adb(self):
        path = filedialog.askopenfilename(
            title="Locate adb.exe",
            filetypes=[("ADB executable", "adb.exe"), ("All files", "*.*")],
        )
        if path:
            self._adb_entry.delete(0, "end")
            self._adb_entry.insert(0, path)
            self._save_btn.configure(state="disabled")

    def _validate(self) -> tuple[bool, str]:
        adb = self._adb_entry.get().strip()
        ip  = self._ip_entry.get().strip()

        if not adb:
            return False, "⚠  ADB path cannot be empty."
        if not adb.lower().endswith(".exe"):
            return False, "⚠  Expected a path ending in adb.exe."
        if not Path(adb).exists():
            return False, f"⚠  File not found:\n{adb}"
        if not ip:
            return False, "⚠  Phone IP cannot be empty."
        parts = ip.split(".")
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            return False, "⚠  Enter a valid IPv4 address (e.g. 192.168.43.1)."

        return True, ""

    def _test_connection(self):
        ok, err = self._validate()
        if not ok:
            self._set_status(err, RED)
            return

        self._set_status("Testing connection…", AMBER)
        self._test_btn.configure(state="disabled")
        self._save_btn.configure(state="disabled")

        adb  = self._adb_entry.get().strip()
        ip   = self._ip_entry.get().strip()
        target = f"{ip}:5555"

        def _run():
            try:
                result = subprocess.run(
                    [adb, "connect", target],
                    capture_output=True, text=True, timeout=12,
                )
                out = result.stdout.strip().lower()
                connected = "connected" in out and "unable" not in out
            except Exception:
                connected = False

            def _report():
                self._test_btn.configure(state="normal")
                if connected:
                    self._set_status(f"✓ Connected to {target}. Click Save & Continue.", GREEN)
                    self._save_btn.configure(state="normal")
                else:
                    self._set_status(
                        "❌ Could not connect.\n\n"
                        "Possible reasons:\n"
                        "  • Hotspot is OFF on your phone\n"
                        "  • Wireless ADB is disabled — enable it in Developer Options\n"
                        "  • Phone IP has changed — check hotspot settings\n"
                        "  • USB Debugging is disabled\n\n"
                        "Fix the issue and try again.",
                        RED,
                    )
            self.after(0, _report)

        threading.Thread(target=_run, daemon=True).start()

    def _save_and_close(self):
        ok, err = self._validate()
        if not ok:
            self._set_status(err, RED)
            return

        adb = self._adb_entry.get().strip()
        ip  = self._ip_entry.get().strip()

        try:
            if self._config_path.exists():
                with open(self._config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {}

            data.setdefault("app", {})["name"] = "Airtel 5G Guardian"
            data["app"]["version"] = "1.0.0"
            data.setdefault("adb", {})["path"]     = adb
            data["adb"]["phone_ip"] = ip
            data["adb"].setdefault("port", 5555)
            data["adb"].setdefault("reconnect_attempts", 5)
            data["adb"].setdefault("reconnect_delay_seconds", 10)
            data.setdefault("monitor", {}).setdefault("check_interval_seconds", 5)
            data.setdefault("notification", {}).setdefault("timeout_seconds", 5)
            data.setdefault("log", {}).setdefault("file", "logs/guardian.log")
            data.setdefault("system", {}).setdefault("launch_on_startup", False)
            data["system"].setdefault("start_minimized", False)
            data["system"].setdefault("minimize_to_tray", True)
            data["system"].setdefault("auto_start_monitoring", False)
            data["system"].setdefault("check_for_updates", True)
            data["system"].setdefault("update_repo", "bharath-kumar-macharla/Airtel-5G-Guardian")

            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

        except Exception as exc:
            self._set_status(f"✗ Could not save config.json:\n{exc}", RED)
            return

        self.grab_release()
        self.destroy()
        self._on_complete()

    def _skip(self):
        self.grab_release()
        self.destroy()
        self._on_skip()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_status(self, text: str, color: str):
        try:
            self._status.configure(text=text, text_color=color)
        except Exception:
            pass

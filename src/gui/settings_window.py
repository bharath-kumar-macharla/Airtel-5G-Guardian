"""
Settings Window
---------------
Phase 4 — Edit all config values without touching JSON.
"""

import customtkinter as ctk
from src.config import ConfigManager
from src.gui.theme import *


class SettingsWindow(ctk.CTkToplevel):

    def __init__(self, parent, config: ConfigManager, on_save=None):
        super().__init__(parent)

        self.config   = config
        self.on_save  = on_save

        self.title("Settings")
        self.geometry("420x500")
        self.resizable(False, False)
        self.configure(fg_color=BG_PRIMARY)
        self.grab_set()  # Modal

        self._build()

    def _build(self):

        # ── Title ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="⚙  Settings",
            font=FONT_TITLE, text_color=TEXT_PRIMARY
        ).pack(pady=(PAD, PAD_SM), padx=PAD, anchor="w")

        ctk.CTkLabel(
            self, text="Changes are saved to config.json",
            font=FONT_MUTED, text_color=TEXT_MUTED
        ).pack(padx=PAD, anchor="w")

        # ── Fields ────────────────────────────────────────────────────────────
        frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=CORNER_RADIUS)
        frame.pack(fill="x", padx=PAD, pady=PAD)

        self._fields = {}

        fields = [
            ("ADB Path",           "adb_path",           self.config.adb_path),
            ("Phone IP",           "phone_ip",            self.config.phone_ip),
            ("Port",               "adb_port",            str(self.config.adb_port)),
            ("Check Interval (s)", "check_interval",      str(self.config.check_interval)),
            ("Notification Timeout (s)", "notification_timeout", str(self.config.notification_timeout)),
            ("Reconnect Attempts", "reconnect_attempts",  str(self.config.reconnect_attempts)),
        ]

        for label, key, value in fields:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", padx=PAD_SM, pady=4)

            ctk.CTkLabel(
                row, text=label, font=FONT_LABEL,
                text_color=TEXT_MUTED, width=160, anchor="w"
            ).pack(side="left")

            entry = ctk.CTkEntry(
                row, fg_color=BG_INPUT, border_color=BORDER,
                text_color=TEXT_PRIMARY, font=FONT_BODY
            )
            entry.insert(0, value)
            entry.pack(side="left", fill="x", expand=True)
            self._fields[key] = entry

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=PAD, pady=PAD)

        ctk.CTkButton(
            btn_frame, text="Cancel",
            fg_color=BG_CARD, hover_color=BORDER,
            text_color=TEXT_MUTED, font=FONT_BODY,
            command=self.destroy
        ).pack(side="left", expand=True, padx=(0, PAD_SM))

        ctk.CTkButton(
            btn_frame, text="Save",
            fg_color=BTN_SETTINGS, hover_color=BTN_SETTINGS_HV,
            text_color="white", font=FONT_HEADING,
            command=self._save
        ).pack(side="left", expand=True)

    def _save(self):
        import json
        from pathlib import Path

        config_path = Path("config/config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            data["adb"]["path"]                       = self._fields["adb_path"].get()
            data["adb"]["phone_ip"]                   = self._fields["phone_ip"].get()
            data["adb"]["port"]                       = int(self._fields["adb_port"].get())
            data["adb"]["reconnect_attempts"]         = int(self._fields["reconnect_attempts"].get())
            data["monitor"]["check_interval_seconds"] = int(self._fields["check_interval"].get())
            data["notification"]["timeout_seconds"]   = int(self._fields["notification_timeout"].get())

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            if self.on_save:
                self.on_save()

            self.destroy()

        except Exception as e:
            ctk.CTkLabel(
                self, text=f"Error: {e}",
                text_color=ACCENT_ERROR, font=FONT_MUTED
            ).pack(pady=4)

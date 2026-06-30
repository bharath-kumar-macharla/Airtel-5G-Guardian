"""
Airtel 5G Guardian — GUI v0.3.0
---------------------------------
Core design fix:
  - Dashboard and Settings panels are built ONCE and hidden/shown via pack/pack_forget
  - Widgets are NEVER destroyed during navigation — no more TclError crashes
  - No background thread for settings verification — keeps it simple and safe
  - self._running guards prevent double-start
  - Settings always shows current live values from self._cfg
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from src.config import ConfigManager, NETWORK_5G, NETWORK_4G
from src.core.adb_manager import ADBManager
from src.core.network_monitor import NetworkMonitor
from src.services.analytics import GuardianAnalytics
from src.services.logger import GuardianLogger
from src.services.notifier import GuardianNotifier
from src.services.sound_manager import SoundManager
from src.gui.theme import *

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GuardianApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ── Backend ───────────────────────────────────────────────────────────
        self._cfg      = ConfigManager()
        self._adb      = ADBManager(self._cfg)
        self._monitor  = None
        self._logger   = GuardianLogger()
        self._notifier = GuardianNotifier()
        self._analytics = GuardianAnalytics()

        # ── Thread state ──────────────────────────────────────────────────────
        self._running          = False
        self._verify_running   = False   # guard for settings verify thread

        # ── Build UI ──────────────────────────────────────────────────────────
        self._setup_window()
        self._build_sidebar()
        self._build_main_area()   # builds header + content frame
        self._build_dashboard()   # built once, never destroyed
        self._build_analytics()   # built once, never destroyed
        self._build_settings()    # built once, never destroyed

        # Show dashboard first
        self._nav("dashboard")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Window ────────────────────────────────────────────────────────────────

    def _setup_window(self):
        self.title("Airtel 5G Guardian")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(fg_color=BG_WINDOW)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=SIDEBAR_W, fg_color=BG_SIDEBAR, corner_radius=0)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Logo
        logo = ctk.CTkFrame(sb, fg_color="transparent", height=60)
        logo.pack(fill="x")
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="📶", font=("Segoe UI Emoji", 20)).pack(side="left", padx=(P, P_XS))
        ctk.CTkLabel(logo, text="Guardian", font=F_TITLE, text_color=TEXT_PRIMARY).pack(side="left")

        ctk.CTkFrame(sb, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=P_SM, pady=(0, P_SM))

        self._nav_btns = {}
        for key, label in [("dashboard", "⊞  Dashboard"), ("analytics", "◌  Analytics"), ("settings", "⚙  Settings")]:
            btn = ctk.CTkButton(
                sb, text=label, anchor="w",
                fg_color="transparent", hover_color=BG_NAV_SEL,
                text_color=TEXT_SECONDARY, font=F_SIDEBAR,
                corner_radius=8, height=38,
                command=lambda k=key: self._nav(k)
            )
            btn.pack(fill="x", padx=P_SM, pady=2)
            self._nav_btns[key] = btn

        ctk.CTkFrame(sb, fg_color="transparent").pack(fill="y", expand=True)
        ctk.CTkFrame(sb, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=P_SM)
        ctk.CTkLabel(sb, text=f"v{self._cfg.app_version}", font=F_SMALL, text_color=TEXT_MUTED).pack(pady=P_SM)

    # ── Navigation — show/hide, never destroy ─────────────────────────────────

    def _nav(self, key: str):
        # Update sidebar button styles
        for k, btn in self._nav_btns.items():
            btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
        self._nav_btns[key].configure(fg_color=BG_NAV_SEL, text_color=TEXT_PRIMARY)

        # Show/hide panels — never destroy
        if key == "dashboard":
            self._page_title.configure(text="Dashboard")
            self._analytics_panel.pack_forget()
            self._settings_panel.pack_forget()
            self._dashboard_panel.pack(fill="both", expand=True)
        elif key == "analytics":
            self._page_title.configure(text="Analytics")
            self._dashboard_panel.pack_forget()
            self._settings_panel.pack_forget()
            self._refresh_analytics()
            self._analytics_panel.pack(fill="both", expand=True)
        elif key == "settings":
            self._page_title.configure(text="Settings")
            self._dashboard_panel.pack_forget()
            self._analytics_panel.pack_forget()
            self._refresh_settings_fields()   # always show current values
            self._settings_panel.pack(fill="both", expand=True)

    # ── Main area (header + content frame) ───────────────────────────────────

    def _build_main_area(self):
        right = ctk.CTkFrame(self, fg_color=BG_CONTENT, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        # Permanent header — never destroyed
        hdr = ctk.CTkFrame(right, fg_color=BG_SIDEBAR, height=52, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        self._page_title = ctk.CTkLabel(hdr, text="", font=F_HEADING, text_color=TEXT_PRIMARY)
        self._page_title.pack(side="left", padx=P)

        self._status_dot = ctk.CTkLabel(hdr, text="⬤  Idle", font=F_SMALL, text_color=TEXT_MUTED)
        self._status_dot.pack(side="right", padx=P)

        ctk.CTkFrame(right, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")

        # Content frame — panels pack/unpack inside here
        self._content = ctk.CTkFrame(right, fg_color=BG_CONTENT, corner_radius=0)
        self._content.pack(fill="both", expand=True)

    # ── Dashboard — built once, lives forever ─────────────────────────────────

    def _build_dashboard(self):
        self._dashboard_panel = ctk.CTkFrame(self._content, fg_color="transparent")

        dash = ctk.CTkFrame(self._dashboard_panel, fg_color="transparent")
        dash.pack(fill="both", expand=True, padx=P, pady=P)

        # Status cards
        cards_row = ctk.CTkFrame(dash, fg_color="transparent")
        cards_row.pack(fill="x", pady=(0, P_SM))

        self._cards = {}
        for i, (key, label, icon) in enumerate([
            ("device_card",  "DEVICE",      "🔌"),
            ("network_card", "NETWORK",     "📶"),
            ("adb_card",     "ADB",         "📡"),
            ("change_card",  "LAST CHANGE", "🕐"),
        ]):
            card = self._make_card(cards_row, label, icon)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else P_SM, 0))
            cards_row.columnconfigure(i, weight=1)
            self._cards[key] = card

        # Buttons
        btn_bar = ctk.CTkFrame(dash, fg_color=BG_CARD, corner_radius=RADIUS)
        btn_bar.pack(fill="x", pady=(0, P_SM))

        self._btn_start = ctk.CTkButton(
            btn_bar, text="▶   Start Monitoring",
            fg_color=BTN_START_FG, hover_color=BTN_START_HV,
            text_color="white", font=F_HEADING,
            corner_radius=8, height=40,
            command=self._start
        )
        self._btn_start.pack(side="left", expand=True, padx=P, pady=P_SM)

        self._btn_stop = ctk.CTkButton(
            btn_bar, text="■   Stop",
            fg_color=BTN_NEUTRAL, hover_color=BTN_STOP_HV,
            text_color=TEXT_MUTED, font=F_HEADING,
            corner_radius=8, height=40,
            state="disabled",
            command=self._stop
        )
        self._btn_stop.pack(side="left", expand=True, padx=(0, P), pady=P_SM)

        # Live log
        log_frame = ctk.CTkFrame(dash, fg_color=BG_CARD, corner_radius=RADIUS)
        log_frame.pack(fill="both", expand=True)

        log_hdr = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_hdr.pack(fill="x", padx=P_SM, pady=(P_SM, 0))
        ctk.CTkLabel(log_hdr, text="Live Activity Log", font=F_HEADING, text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(
            log_hdr, text="Clear", fg_color="transparent", hover_color=BORDER,
            text_color=TEXT_MUTED, font=F_SMALL, width=48, height=22,
            command=self._clear_log
        ).pack(side="right")
        ctk.CTkFrame(log_frame, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=P_SM)

        self._log_box = ctk.CTkTextbox(
            log_frame, fg_color=BG_LOG, text_color=TEXT_SECONDARY,
            font=F_LOG, corner_radius=8, border_width=0,
            wrap="word", state="disabled"
        )
        self._log_box.pack(fill="both", expand=True, padx=P_SM, pady=P_SM)

        for tag, color in {
            "green": GREEN, "amber": AMBER, "red": RED,
            "blue": BLUE, "purple": PURPLE, "muted": TEXT_MUTED,
        }.items():
            self._log_box._textbox.tag_config(tag, foreground=color)

        self._log(f"Guardian v{self._cfg.app_version} ready.", "muted")
        self._log(f"Target: {self._cfg.adb_target}", "blue")

    def _make_card(self, parent, label, icon):
        frame = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=RADIUS)
        ctk.CTkLabel(frame, text=label, font=F_CARD_LBL, text_color=TEXT_MUTED).pack(anchor="w", padx=P_SM, pady=(P_SM, 0))
        ctk.CTkFrame(frame, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=P_SM, pady=P_XS)
        ctk.CTkLabel(frame, text=icon, font=("Segoe UI Emoji", 22)).pack(pady=(P_XS, 0))
        val = ctk.CTkLabel(frame, text="—", font=F_CARD_VAL, text_color=TEXT_MUTED, wraplength=150)
        val.pack(pady=(P_XS, P_SM), padx=P_SM)
        frame.update = lambda v, c: val.configure(text=v, text_color=c)
        return frame

    # Analytics - v0.4.0 daily intelligence

    def _build_analytics(self):
        self._analytics_panel = ctk.CTkFrame(self._content, fg_color="transparent")

        page = ctk.CTkFrame(self._analytics_panel, fg_color="transparent")
        page.pack(fill="both", expand=True, padx=P, pady=P)

        ctk.CTkLabel(page, text="Today Summary", font=F_TITLE, text_color=TEXT_PRIMARY).pack(anchor="w")

        cards = ctk.CTkFrame(page, fg_color="transparent")
        cards.pack(fill="x", pady=(P_SM, P_SM))

        self._analytics_cards = {}
        analytics_card_defs = [
            ("monitoring", "MONITORING", "Time"),
            ("five_g", "5G ACTIVE", "5G"),
            ("four_g", "4G RISK", "4G"),
            ("switches", "SWITCHES", "No."),
            ("uptime", "5G UPTIME", "%"),
            ("last_4g", "LAST 4G DROP", "Time"),
        ]

        for index, (key, label, icon) in enumerate(analytics_card_defs):
            card = self._make_card(cards, label, icon)
            row = index // 3
            column = index % 3
            card.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else P_SM, 0),
                pady=(0 if row == 0 else P_SM, 0),
            )
            cards.columnconfigure(column, weight=1)
            self._analytics_cards[key] = card

        action_row = ctk.CTkFrame(page, fg_color=BG_CARD, corner_radius=RADIUS)
        action_row.pack(fill="x", pady=(0, P_SM))

        self._analytics_status = ctk.CTkLabel(
            action_row,
            text="Daily analytics refresh when this page opens.",
            font=F_SMALL,
            text_color=TEXT_MUTED,
        )
        self._analytics_status.pack(side="left", padx=P_SM)

        ctk.CTkButton(
            action_row,
            text="Refresh",
            fg_color=BTN_NEUTRAL,
            hover_color=BORDER,
            text_color=TEXT_SECONDARY,
            font=F_SMALL,
            height=30,
            command=self._refresh_analytics,
        ).pack(side="right", padx=(0, P_SM), pady=P_SM)

        ctk.CTkButton(
            action_row,
            text="Export Report",
            fg_color=BLUE,
            hover_color="#2563eb",
            text_color="white",
            font=F_HEADING,
            height=30,
            command=self._export_analytics,
        ).pack(side="right", padx=(0, P_SM), pady=P_SM)

        timeline = ctk.CTkFrame(page, fg_color=BG_CARD, corner_radius=RADIUS)
        timeline.pack(fill="both", expand=True)

        timeline_hdr = ctk.CTkFrame(timeline, fg_color="transparent")
        timeline_hdr.pack(fill="x", padx=P_SM, pady=(P_SM, 0))
        ctk.CTkLabel(timeline_hdr, text="Network Timeline", font=F_HEADING, text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkFrame(timeline, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=P_SM)

        self._timeline_box = ctk.CTkTextbox(
            timeline,
            fg_color=BG_LOG,
            text_color=TEXT_SECONDARY,
            font=F_LOG,
            corner_radius=8,
            border_width=0,
            wrap="word",
            state="disabled",
        )
        self._timeline_box.pack(fill="both", expand=True, padx=P_SM, pady=P_SM)

    def _refresh_analytics(self):
        summary = self._analytics.today_summary()
        updates = {
            "monitoring": (self._analytics.format_duration(summary["monitoring_seconds"]), BLUE),
            "five_g": (self._analytics.format_duration(summary["five_g_seconds"]), GREEN),
            "four_g": (self._analytics.format_duration(summary["four_g_seconds"]), AMBER),
            "switches": (str(summary["switch_count"]), TEAL),
            "uptime": (f"{summary['uptime_percent']}%", GREEN if summary["uptime_percent"] >= 90 else AMBER),
            "last_4g": (self._analytics.format_time(summary["last_4g_drop"]), AMBER),
        }

        for key, (value, color) in updates.items():
            self._analytics_cards[key].update(value, color)

        self._timeline_box.configure(state="normal")
        self._timeline_box.delete("1.0", "end")
        events = summary["events"]
        if not events:
            self._timeline_box.insert("end", "No events recorded today.\n")
        else:
            for event in events:
                when = self._analytics.format_time(event.get("time"))
                self._timeline_box.insert("end", f"{when}  {event.get('message', '')}\n")
        self._timeline_box.configure(state="disabled")

        self._analytics_status.configure(
            text=f"{summary['sessions']} session(s) tracked today.",
            text_color=TEXT_MUTED,
        )

    def _export_analytics(self):
        report_path, csv_path = self._analytics.export_today_report()
        self._analytics_status.configure(
            text=f"Exported: {report_path.name} and {csv_path.name}",
            text_color=GREEN,
        )
        self._log(f"Analytics exported to {report_path} and {csv_path}", "green")

    # ── Settings — built once, lives forever ──────────────────────────────────

    def _build_settings(self):
        self._settings_panel = ctk.CTkFrame(self._content, fg_color="transparent")

        outer = ctk.CTkFrame(self._settings_panel, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=P, pady=P)

        ctk.CTkLabel(outer, text="⚙  Settings", font=F_TITLE, text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(
            outer, text="Changes are saved to config.json and applied immediately.",
            font=F_SMALL, text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(P_XS, P_SM))

        card = ctk.CTkFrame(outer, fg_color=BG_CARD, corner_radius=RADIUS)
        card.pack(fill="x")

        fields = [
            ("ADB Path",                 "adb_path"),
            ("Phone IP",                 "phone_ip"),
            ("Port",                     "adb_port"),
            ("Check Interval (s)",       "check_interval"),
            ("Notification Timeout (s)", "notification_timeout"),
            ("Reconnect Attempts",       "reconnect_attempts"),
        ]

        self._setting_entries = {}
        for i, (label, key) in enumerate(fields):
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=P_SM, pady=3)
            ctk.CTkLabel(row, text=label, font=F_SMALL, text_color=TEXT_SECONDARY, width=180, anchor="w").pack(side="left")
            e = ctk.CTkEntry(row, fg_color=BG_INPUT, border_color=BORDER, text_color=TEXT_PRIMARY, font=F_BODY, height=30)
            e.pack(side="left", fill="x", expand=True)
            self._setting_entries[key] = e
            if i < len(fields) - 1:
                ctk.CTkFrame(card, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=P_SM)

        self._settings_status = ctk.CTkLabel(outer, text="", font=F_SMALL, text_color=GREEN)
        self._settings_status.pack(pady=P_SM)

        btn_row = ctk.CTkFrame(outer, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row, text="Restore Defaults",
            fg_color=BTN_NEUTRAL, hover_color=BORDER,
            text_color=TEXT_MUTED, font=F_SMALL, height=34,
            command=self._restore_defaults
        ).pack(side="left")

        ctk.CTkButton(
            btn_row, text="Save",
            fg_color=BLUE, hover_color="#2563eb",
            text_color="white", font=F_HEADING, height=34,
            command=self._save_settings
        ).pack(side="right")

    def _refresh_settings_fields(self):
        """Always shows current live values — called every time Settings is opened."""
        values = {
            "adb_path":             self._cfg.adb_path,
            "phone_ip":             self._cfg.phone_ip,
            "adb_port":             str(self._cfg.adb_port),
            "check_interval":       str(self._cfg.check_interval),
            "notification_timeout": str(self._cfg.notification_timeout),
            "reconnect_attempts":   str(self._cfg.reconnect_attempts),
        }
        for key, entry in self._setting_entries.items():
            entry.delete(0, "end")
            entry.insert(0, values.get(key, ""))
        self._settings_status.configure(text="")

    def _restore_defaults(self):
        defaults = {
            "adb_path":             r"C:\platform-tools\platform-tools\adb.exe",
            "phone_ip":             "192.168.43.1",
            "adb_port":             "5555",
            "check_interval":       "5",
            "notification_timeout": "5",
            "reconnect_attempts":   "5",
        }
        for key, entry in self._setting_entries.items():
            entry.delete(0, "end")
            entry.insert(0, defaults.get(key, ""))
        self._settings_status.configure(
            text="Defaults restored — click Save, then plug USB to auto-detect IP.",
            text_color=AMBER
        )

    def _save_settings(self):
        # Stop any running verify thread first
        self._verify_running = False
        time.sleep(0.1)

        config_path = Path("config/config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            data["adb"]["path"]                       = self._setting_entries["adb_path"].get()
            data["adb"]["phone_ip"]                   = self._setting_entries["phone_ip"].get()
            data["adb"]["port"]                       = int(self._setting_entries["adb_port"].get())
            data["adb"]["reconnect_attempts"]         = int(self._setting_entries["reconnect_attempts"].get())
            data["monitor"]["check_interval_seconds"] = int(self._setting_entries["check_interval"].get())
            data["notification"]["timeout_seconds"]   = int(self._setting_entries["notification_timeout"].get())

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            # Reload config and ADB with new values
            self._cfg = ConfigManager()
            self._adb = ADBManager(self._cfg)

            if self._running:
                # Don't interfere with active monitoring
                self._settings_status.configure(
                    text="✓ Saved. Will apply on next Start.", text_color=GREEN
                )
                return

            # If IP is the default placeholder, start USB detection
            if self._cfg.phone_ip == "192.168.43.1":
                self._settings_status.configure(
                    text="⚠ Default IP detected. Plug in USB to auto-detect real IP...",
                    text_color=PURPLE
                )
                self._log("⚠ Default IP saved. Plug USB to auto-detect...", "purple")
                self._update_dot("⬤  Detecting IP", PURPLE)
                self._verify_running = True
                threading.Thread(target=self._detect_ip_via_usb, daemon=True).start()
            else:
                self._settings_status.configure(
                    text=f"✓ Saved. IP: {self._cfg.phone_ip}", text_color=GREEN
                )
                self._log(f"✓ Settings saved. IP: {self._cfg.phone_ip}", "blue")

        except ValueError:
            self._settings_status.configure(
                text="✗ Numbers only for Port, Interval, Attempts.", text_color=RED
            )
        except Exception as e:
            self._settings_status.configure(text=f"✗ Error: {e}", text_color=RED)

    def _detect_ip_via_usb(self):
        """
        Background thread — only started when IP is the default placeholder.
        Polls for USB, fetches real IP, updates config.json and self._cfg.
        Stops when self._verify_running is False.
        """
        while self._verify_running and not self._running:
            serial = self._adb._get_usb_device()

            if serial:
                self._settings_status.configure(text=f"✓ USB detected → {serial}", text_color=PURPLE)

                if not self._adb._enable_tcpip(serial):
                    self.after(0, lambda: self._settings_status.configure(
                        text="✗ TCP/IP failed. Replug USB.", text_color=RED
                    ))
                    time.sleep(3)
                    continue

                ip = self._adb._fetch_ip_via_usb(serial)
                if not ip:
                    self.after(0, lambda: self._settings_status.configure(
                        text="✗ Could not read IP. Is hotspot ON?", text_color=RED
                    ))
                    time.sleep(3)
                    continue

                # Update config.json and in-memory ADB target
                self._adb._update_ip(ip)

                # Reload config so Settings fields show new IP
                self._cfg = ConfigManager()
                self._adb = ADBManager(self._cfg)
                self._adb._target = f"{ip}:{self._cfg.adb_port}"

                # Update settings field to show new IP
                self.after(0, lambda i=ip: self._setting_entries["phone_ip"].delete(0, "end") or
                           self._setting_entries["phone_ip"].insert(0, i))

                self.after(0, lambda i=ip: self._settings_status.configure(
                    text=f"✓ IP auto-detected → {i}  Ready. Click Start Monitoring.",
                    text_color=GREEN
                ))
                self._log(f"✓ IP auto-detected → {ip}", "green")
                self._update_dot("⬤  Idle", TEXT_MUTED)
                self._adb.disconnect()
                self._verify_running = False
                break
            else:
                time.sleep(3)

    # ── Log helpers ───────────────────────────────────────────────────────────

    def _log(self, message: str, tag: str = "muted"):
        """Thread-safe. Always works — log box is never destroyed."""
        def _do():
            try:
                ts = datetime.now().strftime("%H:%M:%S")
                self._log_box.configure(state="normal")
                self._log_box._textbox.insert("end", f"{ts}  ", "muted")
                self._log_box._textbox.insert("end", f"{message}\n", tag)
                self._log_box._textbox.see("end")
                self._log_box.configure(state="disabled")
            except Exception:
                pass
        self.after(0, _do)

    def _clear_log(self):
        try:
            self._log_box.configure(state="normal")
            self._log_box.delete("1.0", "end")
            self._log_box.configure(state="disabled")
        except Exception:
            pass

    # ── Card + dot helpers ────────────────────────────────────────────────────

    def _update_card(self, key: str, value: str, color: str):
        def _do():
            try:
                self._cards[key].update(value, color)
            except Exception:
                pass
        self.after(0, _do)

    def _update_dot(self, text: str, color: str):
        def _do():
            try:
                self._status_dot.configure(text=text, text_color=color)
            except Exception:
                pass
        self.after(0, _do)

    def _set_buttons(self, monitoring: bool):
        def _do():
            try:
                if monitoring:
                    self._btn_start.configure(state="disabled", fg_color=BTN_NEUTRAL, text_color=TEXT_MUTED)
                    self._btn_stop.configure(state="normal",   fg_color=BTN_STOP_FG,  text_color="white")
                else:
                    self._btn_start.configure(state="normal",   fg_color=BTN_START_FG, text_color="white")
                    self._btn_stop.configure(state="disabled", fg_color=BTN_NEUTRAL,  text_color=TEXT_MUTED)
            except Exception:
                pass
        self.after(0, _do)

    # ── Start / Stop ──────────────────────────────────────────────────────────

    def _start(self):
        if self._running:
            return

        # Stop any IP detection thread before starting monitoring
        self._verify_running = False

        self._running = True
        self._analytics.start_session()
        self._monitor = NetworkMonitor()  # fresh monitor — clears previous_status

        self._set_buttons(monitoring=True)
        self._update_dot("⬤  Connecting", BLUE)
        self._log("Starting Guardian...", "blue")

        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def _stop(self):
        self._running = False
        self._analytics.end_session()
        self._adb.disconnect()
        self._update_dot("⬤  Stopped", RED)
        self._update_card("device_card",  "—", TEXT_MUTED)
        self._update_card("network_card", "—", TEXT_MUTED)
        self._update_card("adb_card",     "—", TEXT_MUTED)
        self._set_buttons(monitoring=False)
        self._log("Monitoring stopped.", "muted")
        self._refresh_analytics()

    # ── Monitor loop ──────────────────────────────────────────────────────────

    def _monitor_loop(self):
        self._log(f"Connecting to {self._adb._target}...", "blue")
        self._update_card("device_card", "Connecting...", BLUE)

        connected = self._adb.is_connected() or self._adb.connect()

        if not connected:
            self._log("⚠ IP failed. Enter Recovery Mode — plug in USB...", "purple")
            self._update_dot("⬤  Recovery Mode", PURPLE)
            self._update_card("device_card", "Recovery Mode", PURPLE)
            self._update_card("adb_card",    "Waiting USB...", PURPLE)
            connected = self._recovery_mode_gui()

        if not connected:
            self._log("✗ Could not connect. Stopping.", "red")
            self._update_dot("⬤  Failed", RED)
            self._update_card("device_card", "Failed", RED)
            self._set_buttons(monitoring=False)
            self._running = False
            self._analytics.end_session()
            return

        self._log(f"✓ Connected to {self._adb._target}", "green")
        self._update_dot("⬤  Monitoring", GREEN)
        self._update_card("device_card", "Connected", GREEN)
        self._update_card("adb_card",    "Wireless",  BLUE)

        while self._running:
            try:
                if not self._adb.is_connected():
                    self._log("⚠ Connection lost. Plug USB to recover...", "purple")
                    self._update_dot("⬤  Recovery Mode", PURPLE)
                    self._update_card("device_card", "Recovery Mode", PURPLE)
                    self._update_card("adb_card",    "Waiting USB...", PURPLE)

                    recovered = self._recovery_mode_gui()
                    if not recovered:
                        self._log("✗ Recovery failed. Stopping.", "red")
                        self._running = False
                        break

                    self._log("✓ Connection restored.", "green")
                    self._update_dot("⬤  Monitoring", GREEN)
                    self._update_card("device_card", "Connected", GREEN)
                    self._update_card("adb_card",    "Wireless",  BLUE)

                changed, network = self._monitor.has_changed()

                if changed:
                    self._analytics.record_network_change(network)
                    now = datetime.now().strftime("%H:%M:%S")
                    self._update_card("change_card", now, TEAL)

                    if network == NETWORK_5G:
                        self._update_card("network_card", "5G Unlimited", GREEN)
                        self._update_dot("⬤  5G Active", GREEN)
                        self._log("✓ Connected to 5G — Unlimited data active", "green")
                        self._logger.write("Connected to 5G")
                        self._notifier.show("🟢 5G Connected", "Unlimited Data Active 🚀")
                        SoundManager.play_5g()

                    elif network == NETWORK_4G:
                        self._update_card("network_card", "4G (Limited)", AMBER)
                        self._update_dot("⬤  4G Active", AMBER)
                        self._log("⚠ Switched to 4G — Data balance consuming!", "amber")
                        self._logger.write("Switched to 4G")
                        self._notifier.show("🔴 4G Detected", "Your Daily Data is now being used.")
                        SoundManager.play_4g()

                    else:
                        self._update_card("network_card", "Unknown", TEXT_MUTED)

                time.sleep(self._cfg.check_interval)

            except Exception as e:
                self._log(f"✗ Error: {e}", "red")
                time.sleep(2)

        self._analytics.end_session()
        self._log("Monitoring ended.", "muted")
        self._set_buttons(monitoring=False)
        self._update_dot("⬤  Idle", TEXT_MUTED)

    # ── Recovery mode ─────────────────────────────────────────────────────────

    def _recovery_mode_gui(self) -> bool:
        self._log("══ Recovery Mode — Plug in USB cable ══", "purple")

        while self._running:
            serial = self._adb._get_usb_device()

            if serial:
                self._log(f"✓ USB detected → {serial}", "purple")
                self._update_card("adb_card", "USB Detected", PURPLE)

                if not self._adb._enable_tcpip(serial):
                    self._log("✗ TCP/IP failed. Replug USB.", "red")
                    time.sleep(3)
                    continue

                ip = self._adb._fetch_ip_via_usb(serial)
                if not ip:
                    self._log("✗ Could not read IP. Hotspot ON?", "red")
                    time.sleep(3)
                    continue

                self._adb._update_ip(ip)
                self._cfg = ConfigManager()
                self._log(f"✓ IP updated → {ip}", "purple")

                self._update_card("adb_card", "Reconnecting...", PURPLE)
                if self._adb.connect():
                    return True

                self._log("✗ Wireless connect failed. Retrying...", "red")
                time.sleep(3)
            else:
                time.sleep(3)

        return False

    # ── Close ─────────────────────────────────────────────────────────────────

    def _on_close(self):
        self._running        = False
        self._verify_running = False
        self._analytics.end_session()
        self._adb.disconnect()
        self.destroy()

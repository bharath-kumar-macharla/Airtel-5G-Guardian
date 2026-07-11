"""
Airtel 5G Guardian — GUI v0.5.0
---------------------------------
"Always running. Always protecting."

New in v0.5.0:
  - System tray integration — closing the window minimizes to tray instead
    of quitting; monitoring keeps running in the background.
  - Launch with Windows (per-user registry Run key, no admin required).
  - Smart Startup — on open, Guardian can auto-reconnect and resume the
    last monitoring session without any clicks.
  - Background update checker against GitHub releases.
  - Settings: Browse ADB, Test Connection, input validation, and toggle
    switches for all the new background behavior.
  - Status dot / cards / tray icon all agree on one status vocabulary:
    idle | connecting | monitoring | disconnected | recovery.
  - A threading.Event drives shutdown so Stop/Exit interrupt sleeps
    immediately instead of waiting out the check interval.

Design carried over from v0.4.0:
  - Dashboard, Analytics and Settings panels are built ONCE and
    hidden/shown via pack/pack_forget — no destroy/rebuild TclErrors.
  - self._running guards prevent double-start.
"""

import json
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.config import ConfigManager, NETWORK_5G, NETWORK_4G
from src.core.adb_manager import ADBManager
from src.core.network_monitor import NetworkMonitor
from src.services.analytics import GuardianAnalytics
from src.services.logger import GuardianLogger
from src.services.notifier import GuardianNotifier
from src.services.sound_manager import SoundManager
from src.gui.theme import *
from src.system.tray import GuardianTray
from src.system import startup as startup_manager
from src.system import updater as update_checker

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Status vocabulary shared by the header dot, dashboard cards, and tray icon.
STATUS_TEXT = {
    "idle":         ("⬤  Idle",           STATUS_COLORS["idle"]),
    "connecting":   ("⬤  Connecting",     STATUS_COLORS["connecting"]),
    "monitoring":   ("⬤  Monitoring",     STATUS_COLORS["monitoring"]),
    "disconnected": ("⬤  Disconnected",   STATUS_COLORS["disconnected"]),
    "recovery":     ("⬤  Recovery Mode",  STATUS_COLORS["recovery"]),
}


class GuardianApp(ctk.CTk):

    def __init__(self, start_minimized: bool = False):
        super().__init__()

        # ── Backend ───────────────────────────────────────────────────────────
        self._cfg       = ConfigManager()
        self._adb       = ADBManager(self._cfg)
        self._monitor   = None
        self._logger    = GuardianLogger()
        self._notifier  = GuardianNotifier()
        self._analytics = GuardianAnalytics()

        # ── Thread state ──────────────────────────────────────────────────────
        self._running          = False
        self._verify_running   = False   # guard for settings verify thread
        self._detect_token     = 0       # generation counter — invalidates stale detect threads
        self._stop_event       = threading.Event()  # interrupts sleeps for fast shutdown
        self._log_entries      = []      # (timestamp, message, tag) — backs search/save
        self._autoscroll       = True
        self._closing_to_tray  = False

        # ── Build UI ──────────────────────────────────────────────────────────
        self._setup_window()
        self._build_sidebar()
        self._build_main_area()   # builds header + progress bar + content frame
        self._build_dashboard()   # built once, never destroyed
        self._build_analytics()   # built once, never destroyed
        self._build_settings()    # built once, never destroyed

        # Show dashboard first
        self._nav("dashboard")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── System tray ───────────────────────────────────────────────────────
        try:
            self._tray = GuardianTray(
                on_start=self._tray_cb_start,
                on_stop=self._tray_cb_stop,
                on_open=self._tray_cb_open,
                on_settings=self._tray_cb_settings,
                on_exit=self._tray_cb_exit,
                app_name=self._cfg.app_name,
            )
            self._tray.run_detached()
        except Exception as e:
            # System tray is a nice-to-have, not something worth crashing
            # Guardian's startup over. Fall back to a stub that always
            # reports itself unavailable — _on_close() etc. already handle
            # that case by closing normally instead of minimizing to tray.
            print(f"[Tray] System tray failed to start: {e}")
            self._tray = GuardianTray(
                on_start=lambda: None, on_stop=lambda: None, on_open=lambda: None,
                on_settings=lambda: None, on_exit=lambda: None,
            )
            self._tray.available = False

        if not self._tray.available:
            self._log("⚠ System tray unavailable (pystray/Pillow not installed). "
                       "Closing the window will exit Guardian.", "amber")

        if start_minimized:
            self.after(50, self._minimize_to_tray)

        # ── Smart Startup — resume monitoring automatically if configured ──────
        self.after(400, self._smart_startup)

        # ── Background update check ─────────────────────────────────────────────
        if self._cfg.check_for_updates:
            self.after(2500, self._check_updates_async)

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

        # Minimize-to-tray shortcut, always visible
        ctk.CTkButton(
            sb, text="⬇  Minimize to Tray", anchor="w",
            fg_color="transparent", hover_color=BG_NAV_SEL,
            text_color=TEXT_MUTED, font=F_SMALL,
            corner_radius=8, height=30,
            command=self._minimize_to_tray,
        ).pack(fill="x", padx=P_SM, pady=(0, 2))

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

    # ── Main area (header + progress bar + content frame) ───────────────────

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

        # Slim indeterminate progress bar — visible only while connecting/recovering
        self._progress = ctk.CTkProgressBar(
            right, height=3, corner_radius=0, fg_color=BG_CONTENT,
            progress_color=BLUE, mode="indeterminate",
        )
        # Not packed yet — _set_progress() shows/hides it on demand

        # Content frame — panels pack/unpack inside here
        self._content = ctk.CTkFrame(right, fg_color=BG_CONTENT, corner_radius=0)
        self._content.pack(fill="both", expand=True)

    def _set_progress(self, active: bool):
        def _do():
            try:
                if active:
                    self._progress.pack(fill="x", before=self._content)
                    self._progress.start()
                else:
                    self._progress.stop()
                    self._progress.pack_forget()
            except Exception:
                pass
        self.after(0, _do)

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

        self._log_search = ctk.CTkEntry(
            log_hdr, placeholder_text="Search log…", fg_color=BG_INPUT,
            border_color=BORDER, text_color=TEXT_PRIMARY, font=F_SMALL,
            width=150, height=24,
        )
        self._log_search.pack(side="right", padx=(P_SM, 0))
        self._log_search.bind("<KeyRelease>", lambda e: self._render_log())

        ctk.CTkButton(
            log_hdr, text="Save", fg_color="transparent", hover_color=BORDER,
            text_color=TEXT_MUTED, font=F_SMALL, width=42, height=22,
            command=self._save_log
        ).pack(side="right", padx=(P_SM, 0))

        ctk.CTkButton(
            log_hdr, text="Clear", fg_color="transparent", hover_color=BORDER,
            text_color=TEXT_MUTED, font=F_SMALL, width=48, height=22,
            command=self._clear_log
        ).pack(side="right")

        self._autoscroll_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            log_hdr, text="Auto-scroll", variable=self._autoscroll_var,
            font=F_SMALL, text_color=TEXT_MUTED, width=16, height=16,
            checkbox_width=16, checkbox_height=16,
            command=lambda: setattr(self, "_autoscroll", self._autoscroll_var.get()),
        ).pack(side="right", padx=(P_SM, P_SM))

        ctk.CTkFrame(log_frame, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=P_SM)

        self._log_box = ctk.CTkTextbox(
            log_frame, fg_color=BG_LOG, text_color=TEXT_SECONDARY,
            font=F_LOG, corner_radius=8, border_width=0,
            wrap="word", state="disabled"
        )
        self._log_box.pack(fill="both", expand=True, padx=P_SM, pady=P_SM)

        for tag, color in {
            "green": GREEN, "amber": AMBER, "red": RED,
            "blue": BLUE, "purple": PURPLE, "orange": ORANGE,
            "yellow": YELLOW, "muted": TEXT_MUTED,
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
        # NOTE: intentionally named update_value, not update() — CTkFrame
        # (a tkinter.Frame subclass) already has a built-in .update() method
        # used internally by Tk/CTk for redraws; shadowing it here used to
        # raise "TypeError: missing 2 required positional arguments"
        # whenever anything called the real .update() on a card.
        frame.update_value = lambda v, c: val.configure(text=v, text_color=c)
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
            self._analytics_cards[key].update_value(value, color)

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

        outer = ctk.CTkScrollableFrame(self._settings_panel, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=P, pady=P)

        ctk.CTkLabel(outer, text="⚙  Settings", font=F_TITLE, text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(
            outer, text="Changes are saved to config.json and applied immediately.",
            font=F_SMALL, text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(P_XS, P_SM))

        # ── Connection card ──────────────────────────────────────────────────
        ctk.CTkLabel(outer, text="Connection", font=F_HEADING, text_color=TEXT_SECONDARY).pack(anchor="w", pady=(0, P_XS))
        card = ctk.CTkFrame(outer, fg_color=BG_CARD, corner_radius=RADIUS)
        card.pack(fill="x", pady=(0, P_SM))

        fields = [
            ("ADB Path",                 "adb_path",     True),
            ("Phone IP",                 "phone_ip",     False),
            ("Port",                     "adb_port",     False),
            ("Check Interval (s)",       "check_interval", False),
            ("Notification Timeout (s)", "notification_timeout", False),
            ("Reconnect Attempts",       "reconnect_attempts", False),
        ]

        self._setting_entries = {}
        for i, (label, key, browsable) in enumerate(fields):
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=P_SM, pady=3)
            ctk.CTkLabel(row, text=label, font=F_SMALL, text_color=TEXT_SECONDARY, width=180, anchor="w").pack(side="left")
            e = ctk.CTkEntry(row, fg_color=BG_INPUT, border_color=BORDER, text_color=TEXT_PRIMARY, font=F_BODY, height=30)
            e.pack(side="left", fill="x", expand=True)
            self._setting_entries[key] = e
            if browsable:
                ctk.CTkButton(
                    row, text="Browse…", width=64, height=30,
                    fg_color=BTN_NEUTRAL, hover_color=BORDER,
                    text_color=TEXT_SECONDARY, font=F_SMALL,
                    command=self._browse_adb,
                ).pack(side="left", padx=(P_XS, 0))
            if i < len(fields) - 1:
                ctk.CTkFrame(card, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=P_SM)

        # ── Startup & Behavior card ──────────────────────────────────────────
        ctk.CTkLabel(outer, text="Startup & Behavior", font=F_HEADING, text_color=TEXT_SECONDARY).pack(anchor="w", pady=(P_SM, P_XS))
        behavior_card = ctk.CTkFrame(outer, fg_color=BG_CARD, corner_radius=RADIUS)
        behavior_card.pack(fill="x", pady=(0, P_SM))

        switch_defs = [
            ("launch_on_startup",   "Launch Guardian when Windows starts"),
            ("start_minimized",     "Start minimized to tray"),
            ("minimize_to_tray",    "Minimize to tray instead of closing"),
            ("auto_start_monitoring", "Auto-resume monitoring on launch"),
            ("check_for_updates",   "Check for updates automatically"),
        ]

        self._setting_switches = {}
        for i, (key, label) in enumerate(switch_defs):
            row = ctk.CTkFrame(behavior_card, fg_color="transparent")
            row.pack(fill="x", padx=P_SM, pady=6)
            var = ctk.BooleanVar(value=False)
            ctk.CTkSwitch(
                row, text=label, variable=var, font=F_SMALL,
                text_color=TEXT_SECONDARY, progress_color=GREEN,
                button_color="#e2e8f0", onvalue=True, offvalue=False,
            ).pack(side="left")
            self._setting_switches[key] = var
            if i < len(switch_defs) - 1:
                ctk.CTkFrame(behavior_card, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", padx=P_SM)

        self._settings_status = ctk.CTkLabel(outer, text="", font=F_SMALL, text_color=GREEN, wraplength=560, justify="left")
        self._settings_status.pack(pady=P_SM, anchor="w")

        btn_row = ctk.CTkFrame(outer, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row, text="Restore Defaults",
            fg_color=BTN_NEUTRAL, hover_color=BORDER,
            text_color=TEXT_MUTED, font=F_SMALL, height=34,
            command=self._restore_defaults
        ).pack(side="left")

        ctk.CTkButton(
            btn_row, text="Test Connection",
            fg_color=BTN_NEUTRAL, hover_color=BORDER,
            text_color=TEXT_SECONDARY, font=F_SMALL, height=34,
            command=self._test_connection
        ).pack(side="left", padx=(P_SM, 0))

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

        switch_values = {
            "launch_on_startup":     startup_manager.is_enabled(),
            "start_minimized":       self._cfg.start_minimized,
            "minimize_to_tray":      self._cfg.minimize_to_tray,
            "auto_start_monitoring": self._cfg.auto_start_monitoring,
            "check_for_updates":     self._cfg.check_for_updates,
        }
        for key, var in self._setting_switches.items():
            var.set(switch_values.get(key, False))

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

        default_switches = {
            "launch_on_startup": False, "start_minimized": False,
            "minimize_to_tray": True, "auto_start_monitoring": False,
            "check_for_updates": True,
        }
        for key, var in self._setting_switches.items():
            var.set(default_switches.get(key, False))

        self._settings_status.configure(
            text="Defaults restored — click Save, then plug USB to auto-detect IP.",
            text_color=AMBER
        )

    def _browse_adb(self):
        path = filedialog.askopenfilename(
            title="Locate adb.exe",
            filetypes=[("ADB executable", "adb.exe"), ("All files", "*.*")],
        )
        if path:
            self._setting_entries["adb_path"].delete(0, "end")
            self._setting_entries["adb_path"].insert(0, path)

    def _validate_settings_fields(self) -> tuple:
        """Returns (ok, error_message). Blocks Save on bad input instead of
        silently writing garbage into config.json."""
        adb_path = self._setting_entries["adb_path"].get().strip()
        phone_ip = self._setting_entries["phone_ip"].get().strip()

        if not adb_path:
            return False, "⚠ Invalid ADB Path — field cannot be empty."
        if not adb_path.lower().endswith(".exe"):
            return False, "⚠ Invalid ADB Path — expected a path ending in adb.exe."
        if not Path(adb_path).exists():
            return False, f"⚠ Invalid ADB Path — file not found:\n{adb_path}"

        if not phone_ip:
            return False, "⚠ Phone IP cannot be empty."

        for key, label in [
            ("adb_port", "Port"), ("check_interval", "Check Interval"),
            ("notification_timeout", "Notification Timeout"),
            ("reconnect_attempts", "Reconnect Attempts"),
        ]:
            raw = self._setting_entries[key].get().strip()
            try:
                value = int(raw)
                if value <= 0:
                    return False, f"⚠ {label} must be a positive whole number."
            except ValueError:
                return False, f"⚠ {label} must be a number. Got: '{raw}'"

        return True, ""

    def _save_settings(self):
        ok, error = self._validate_settings_fields()
        if not ok:
            self._settings_status.configure(text=error, text_color=RED)
            messagebox.showwarning("Invalid Settings", error)
            return

        # Invalidate any running verify thread first — _start_ip_detection()
        # below (if reached) will mint a fresh token; this just ensures a
        # stale thread from a previous Save never lingers.
        self._verify_running = False
        self._detect_token += 1

        config_path = Path("config/config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            data["adb"]["path"]                       = self._setting_entries["adb_path"].get().strip()
            data["adb"]["phone_ip"]                   = self._setting_entries["phone_ip"].get().strip()
            data["adb"]["port"]                       = int(self._setting_entries["adb_port"].get())
            data["adb"]["reconnect_attempts"]         = int(self._setting_entries["reconnect_attempts"].get())
            data["monitor"]["check_interval_seconds"] = int(self._setting_entries["check_interval"].get())
            data["notification"]["timeout_seconds"]   = int(self._setting_entries["notification_timeout"].get())

            data.setdefault("system", {})
            data["system"]["start_minimized"]       = bool(self._setting_switches["start_minimized"].get())
            data["system"]["minimize_to_tray"]       = bool(self._setting_switches["minimize_to_tray"].get())
            data["system"]["auto_start_monitoring"]  = bool(self._setting_switches["auto_start_monitoring"].get())
            data["system"]["check_for_updates"]      = bool(self._setting_switches["check_for_updates"].get())

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            # Apply launch-on-startup toggle to the Windows registry
            startup_manager.set_enabled(bool(self._setting_switches["launch_on_startup"].get()))

            # Reload config and ADB with new values
            self._cfg = ConfigManager()
            self._adb = ADBManager(self._cfg)

            messagebox.showinfo("Settings", "✔ Settings Saved")
            self._log("✓ Settings saved.", "green")

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
                self._set_status("connecting")
                self._start_ip_detection()
            else:
                self._settings_status.configure(
                    text=f"✓ Saved. IP: {self._cfg.phone_ip}", text_color=GREEN
                )
                self._log(f"✓ Settings saved. IP: {self._cfg.phone_ip}", "blue")

        except ValueError:
            error = "✗ Numbers only for Port, Interval, Attempts."
            self._settings_status.configure(text=error, text_color=RED)
            messagebox.showerror("Invalid Settings", error)
        except Exception as e:
            error = f"✗ Error: {e}"
            self._settings_status.configure(text=error, text_color=RED)
            messagebox.showerror("Settings Error", error)

    def _test_connection(self):
        ok, error = self._validate_settings_fields()
        if not ok:
            messagebox.showwarning("Invalid Settings", error)
            return

        self._settings_status.configure(text="Testing connection…", text_color=BLUE)

        class _Probe:
            pass

        probe = _Probe()
        probe.adb_path = self._setting_entries["adb_path"].get().strip()
        probe.phone_ip = self._setting_entries["phone_ip"].get().strip()
        probe.adb_port = int(self._setting_entries["adb_port"].get())
        probe.adb_target = f"{probe.phone_ip}:{probe.adb_port}"

        def _run_test():
            temp_adb = ADBManager(probe)
            connected = temp_adb.is_connected() or temp_adb.connect()

            def _report():
                if connected:
                    self._settings_status.configure(
                        text=f"✓ Connected to {probe.adb_target}", text_color=GREEN
                    )
                    self._log(f"✓ Test connection succeeded → {probe.adb_target}", "green")
                else:
                    msg = f"❌ Device Not Found at {probe.adb_target}"
                    self._settings_status.configure(text=msg, text_color=RED)
                    messagebox.showerror("Device Not Found", msg)
                    self._log(msg, "red")

            self.after(0, _report)

        threading.Thread(target=_run_test, daemon=True).start()

    def _start_ip_detection(self):
        """
        Starts a fresh USB IP-detection background thread and invalidates
        any previous one via a generation token, so Save being clicked
        repeatedly in quick succession can never leave two of these threads
        polling ADB and writing config.json at the same time.
        """
        self._detect_token += 1
        token = self._detect_token
        self._verify_running = True
        threading.Thread(target=self._detect_ip_via_usb, args=(token,), daemon=True).start()

    def _detect_ip_via_usb(self, token: int):
        """
        Background thread — only started when IP is the default placeholder.
        Polls for USB, fetches real IP, updates config.json and self._cfg.

        `token` pins this call to the generation it was started under —
        if a newer call to _start_ip_detection() has since bumped
        self._detect_token, this loop exits instead of racing the newer
        thread for the same ADB target and config.json file.

        All widget access is marshaled onto the main thread via self.after()
        — Tkinter widgets must never be touched directly from a background
        thread.
        """
        def _still_current():
            return self._verify_running and self._detect_token == token and not self._running

        while _still_current():
            serial = self._adb._get_usb_device()

            if serial:
                self.after(0, lambda s=serial: self._settings_status.configure(
                    text=f"✓ USB detected → {s}", text_color=PURPLE
                ))

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

                if not _still_current():
                    return  # superseded mid-flight — let the newer thread finish the job

                # Update config.json and in-memory ADB target
                self._adb._update_ip(ip)

                # Reload config so Settings fields show new IP
                self._cfg = ConfigManager()
                self._adb = ADBManager(self._cfg)

                # Update settings field to show new IP
                def _apply_ip(i=ip):
                    self._setting_entries["phone_ip"].delete(0, "end")
                    self._setting_entries["phone_ip"].insert(0, i)
                    self._settings_status.configure(
                        text=f"✓ IP auto-detected → {i}  Ready. Click Start Monitoring.",
                        text_color=GREEN
                    )
                self.after(0, _apply_ip)

                self._log(f"✓ IP auto-detected → {ip}", "green")
                self._set_status("idle")
                self._adb.disconnect()

                if self._detect_token == token:
                    self._verify_running = False
                break
            else:
                time.sleep(3)

    # ── Log helpers ───────────────────────────────────────────────────────────

    def _log(self, message: str, tag: str = "muted"):
        """Thread-safe. Always works — log box is never destroyed."""
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_entries.append((ts, message, tag))

        def _do():
            try:
                query = getattr(self, "_log_search", None)
                query_text = query.get().strip().lower() if query else ""
                if query_text and query_text not in message.lower():
                    return
                self._log_box.configure(state="normal")
                self._log_box._textbox.insert("end", f"{ts}  ", "muted")
                self._log_box._textbox.insert("end", f"{message}\n", tag)
                if self._autoscroll:
                    self._log_box._textbox.see("end")
                self._log_box.configure(state="disabled")
            except Exception:
                pass
        self.after(0, _do)

    def _render_log(self):
        """Re-renders the whole log box filtered by the current search text."""
        query = self._log_search.get().strip().lower()
        try:
            self._log_box.configure(state="normal")
            self._log_box.delete("1.0", "end")
            for ts, message, tag in self._log_entries:
                if query and query not in message.lower():
                    continue
                self._log_box._textbox.insert("end", f"{ts}  ", "muted")
                self._log_box._textbox.insert("end", f"{message}\n", tag)
            if self._autoscroll:
                self._log_box._textbox.see("end")
            self._log_box.configure(state="disabled")
        except Exception:
            pass

    def _clear_log(self):
        self._log_entries.clear()
        try:
            self._log_box.configure(state="normal")
            self._log_box.delete("1.0", "end")
            self._log_box.configure(state="disabled")
        except Exception:
            pass

    def _save_log(self):
        default_name = f"guardian_log_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
        path = filedialog.asksaveasfilename(
            title="Save Activity Log", defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                for ts, message, _tag in self._log_entries:
                    f.write(f"[{ts}] {message}\n")
            self._log(f"✓ Log saved → {path}", "green")
        except Exception as e:
            messagebox.showerror("Save Log", f"Could not save log:\n{e}")

    # ── Card + dot + status helpers ───────────────────────────────────────────

    def _update_card(self, key: str, value: str, color: str):
        def _do():
            try:
                self._cards[key].update_value(value, color)
            except Exception:
                pass
        self.after(0, _do)

    def _set_status(self, status: str):
        """
        Single source of truth for the header dot, tray icon, and progress
        bar — status is one of: idle | connecting | monitoring |
        disconnected | recovery.
        """
        text, color = STATUS_TEXT.get(status, STATUS_TEXT["idle"])

        def _do():
            try:
                self._status_dot.configure(text=text, text_color=color)
            except Exception:
                pass
        self.after(0, _do)

        try:
            self._tray.set_status(status)
        except Exception:
            pass

        self._set_progress(status in ("connecting", "recovery"))

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
        self._detect_token += 1
        self._stop_event.clear()

        self._running = True
        self._analytics.start_session()
        self._monitor = NetworkMonitor()  # fresh monitor — clears previous_status

        self._set_buttons(monitoring=True)
        self._set_status("connecting")
        self._log("Starting Guardian...", "blue")

        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def _stop(self):
        self._running = False
        self._stop_event.set()
        self._analytics.end_session()
        self._adb.disconnect()
        self._set_status("disconnected")
        self._update_card("device_card",  "—", TEXT_MUTED)
        self._update_card("network_card", "—", TEXT_MUTED)
        self._update_card("adb_card",     "—", TEXT_MUTED)
        self._set_buttons(monitoring=False)
        self._log("Monitoring stopped.", "muted")
        self._refresh_analytics()

    # ── Monitor loop ──────────────────────────────────────────────────────────

    def _monitor_loop(self):
        self._log(f"Connecting to {self._adb._target}...", "blue")
        self._update_card("device_card", "Connecting...", STATUS_COLORS["connecting"])

        connected = self._adb.is_connected() or self._adb.connect()

        if not connected:
            self._log("⚠ IP failed. Enter Recovery Mode — plug in USB...", "orange")
            self._set_status("recovery")
            self._update_card("device_card", "Recovery Mode", ORANGE)
            self._update_card("adb_card",    "Waiting USB...", ORANGE)
            connected = self._recovery_mode_gui()

        if not connected:
            self._log("✗ Could not connect. Stopping.", "red")
            self._set_status("disconnected")
            self._update_card("device_card", "Failed", RED)
            self._set_buttons(monitoring=False)
            self._running = False
            self._analytics.end_session()
            return

        self._log(f"✓ Connected to {self._adb._target}", "green")
        self._set_status("monitoring")
        self._update_card("device_card", "Connected", GREEN)
        self._update_card("adb_card",    "Wireless",  BLUE)

        while self._running:
            try:
                if not self._adb.is_connected():
                    self._log("⚠ Connection lost. Plug USB to recover...", "orange")
                    self._set_status("recovery")
                    self._update_card("device_card", "Recovery Mode", ORANGE)
                    self._update_card("adb_card",    "Waiting USB...", ORANGE)

                    recovered = self._recovery_mode_gui()
                    if not recovered:
                        self._log("✗ Recovery failed. Stopping.", "red")
                        self._running = False
                        break

                    self._log("✓ Connection restored.", "green")
                    self._set_status("monitoring")
                    self._update_card("device_card", "Connected", GREEN)
                    self._update_card("adb_card",    "Wireless",  BLUE)

                changed, network = self._monitor.has_changed()

                if changed:
                    self._analytics.record_network_change(network)
                    now = datetime.now().strftime("%H:%M:%S")
                    self._update_card("change_card", now, TEAL)

                    if network == NETWORK_5G:
                        self._update_card("network_card", "5G Unlimited", GREEN)
                        self._set_status("monitoring")
                        self._log("✓ Connected to 5G — Unlimited data active", "green")
                        self._logger.write("Connected to 5G")
                        self._notifier.show("🟢 5G Connected", "Unlimited Data Active 🚀")
                        SoundManager.play_5g()

                    elif network == NETWORK_4G:
                        self._update_card("network_card", "4G (Limited)", AMBER)
                        self._log("⚠ Switched to 4G — Data balance consuming!", "amber")
                        self._logger.write("Switched to 4G")
                        self._notifier.show("🔴 4G Detected", "Your Daily Data is now being used.")
                        SoundManager.play_4g()

                    else:
                        self._update_card("network_card", "Unknown", TEXT_MUTED)

                # Interruptible sleep — Stop/Exit no longer waits out check_interval
                self._stop_event.wait(self._cfg.check_interval)

            except Exception as e:
                self._log(f"✗ Error: {e}", "red")
                self._stop_event.wait(2)

        self._analytics.end_session()
        self._log("Monitoring ended.", "muted")
        self._set_buttons(monitoring=False)
        self._set_status("idle")

    # ── Recovery mode ─────────────────────────────────────────────────────────

    def _recovery_mode_gui(self) -> bool:
        self._log("══ Recovery Mode — Plug in USB cable ══", "orange")

        while self._running:
            serial = self._adb._get_usb_device()

            if serial:
                self._log(f"✓ USB detected → {serial}", "orange")
                self._update_card("adb_card", "USB Detected", ORANGE)

                if not self._adb._enable_tcpip(serial):
                    self._log("✗ TCP/IP failed. Replug USB.", "red")
                    self._stop_event.wait(3)
                    continue

                ip = self._adb._fetch_ip_via_usb(serial)
                if not ip:
                    self._log("✗ Could not read IP. Hotspot ON?", "red")
                    self._stop_event.wait(3)
                    continue

                self._adb._update_ip(ip)
                self._cfg = ConfigManager()
                self._log(f"✓ IP updated → {ip}", "orange")

                self._update_card("adb_card", "Reconnecting...", ORANGE)
                if self._adb.connect():
                    return True

                self._log("✗ Wireless connect failed. Retrying...", "red")
                self._stop_event.wait(3)
            else:
                self._stop_event.wait(3)

        return False

    # ── Smart Startup ─────────────────────────────────────────────────────────

    def _smart_startup(self):
        """
        Loads config, checks whether auto-resume is enabled, and if the
        phone IP is not still the default placeholder, kicks off monitoring
        without requiring a click — "Boot Windows → Guardian runs".
        """
        if not self._cfg.auto_start_monitoring:
            return
        if self._cfg.phone_ip == "192.168.43.1":
            self._log("Smart Startup skipped — no phone IP configured yet.", "muted")
            return
        self._log("Smart Startup — resuming previous session automatically.", "blue")
        self._start()

    # ── Update checker ────────────────────────────────────────────────────────

    def _check_updates_async(self):
        def _run():
            info = update_checker.check_for_update(self._cfg.app_version, self._cfg.update_repo)
            if info:
                self.after(0, lambda: self._show_update_dialog(info))
        threading.Thread(target=_run, daemon=True).start()

    def _show_update_dialog(self, info):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Update Available")
        dialog.geometry("380x180")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG_CONTENT)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=f"🚀 Airtel 5G Guardian v{info.version} Available",
            font=F_HEADING, text_color=TEXT_PRIMARY, wraplength=340,
        ).pack(pady=(P, P_SM), padx=P)

        ctk.CTkLabel(
            dialog, text="A newer version is ready to download from GitHub.",
            font=F_SMALL, text_color=TEXT_MUTED, wraplength=340,
        ).pack(padx=P)

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(side="bottom", fill="x", padx=P, pady=P)

        ctk.CTkButton(
            btn_row, text="Later", fg_color=BTN_NEUTRAL, hover_color=BORDER,
            text_color=TEXT_SECONDARY, font=F_SMALL, height=32,
            command=dialog.destroy,
        ).pack(side="left", expand=True, padx=(0, P_XS))

        ctk.CTkButton(
            btn_row, text="Download", fg_color=BLUE, hover_color="#2563eb",
            text_color="white", font=F_HEADING, height=32,
            command=lambda: (webbrowser.open(info.url), dialog.destroy()),
        ).pack(side="left", expand=True, padx=(P_XS, 0))

    # ── System tray callbacks (called from the tray's own thread) ─────────────

    def _tray_cb_start(self):
        self.after(0, self._start)

    def _tray_cb_stop(self):
        self.after(0, self._stop)

    def _tray_cb_open(self):
        self.after(0, self._restore_from_tray)

    def _tray_cb_settings(self):
        def _do():
            self._restore_from_tray()
            self._nav("settings")
        self.after(0, _do)

    def _tray_cb_exit(self):
        self.after(0, self._exit_app)

    # ── Minimize / restore / exit ─────────────────────────────────────────────

    def _minimize_to_tray(self):
        if not self._tray.available:
            self._log("Tray unavailable — use Exit from the window instead.", "amber")
            return
        self._closing_to_tray = True
        self.withdraw()
        self._log("Minimized to tray. Monitoring continues in the background.", "muted")

    def _restore_from_tray(self):
        self._closing_to_tray = False
        try:
            self.deiconify()
            self.lift()
            self.focus_force()
        except Exception:
            pass

    def _on_close(self):
        """Window-close (X) button — minimizes to tray unless tray is
        unavailable or the user has disabled that behavior."""
        if self._tray.available and self._cfg.minimize_to_tray:
            self._minimize_to_tray()
        else:
            self._exit_app()

    def _exit_app(self):
        """True shutdown — stops monitoring, tears down the tray icon, and
        closes the window. Only reachable via tray Exit or a disabled tray."""
        self._running        = False
        self._verify_running = False
        self._stop_event.set()
        self._analytics.end_session()
        try:
            self._adb.disconnect()
        except Exception:
            pass
        try:
            self._tray.stop()
        except Exception:
            pass
        self.destroy()

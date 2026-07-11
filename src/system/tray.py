"""
System Tray
-----------
v0.5.0 - Wraps pystray so Guardian can live in the Windows system tray
instead of holding a taskbar slot. Runs its own background thread;
every menu action is handed back to the caller through plain callback
functions so the tray never touches Tk widgets directly (Tk is not
thread-safe — the GUI layer marshals calls back with `.after(0, ...)`).
"""

from pathlib import Path
from typing import Callable, Optional

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except Exception:
    # pystray can fail at import time for reasons beyond a missing package —
    # e.g. no windowing backend available (Gtk/AppIndicator/Xorg on Linux,
    # or a headless environment). Any such failure should degrade to
    # "tray unavailable" rather than crash the whole app.
    TRAY_AVAILABLE = False
    Image = None
    ImageDraw = None


STATUS_COLORS = {
    "idle":        (71, 85, 105),    # muted gray
    "connecting":  (245, 158, 11),   # amber / yellow
    "monitoring":  (0, 210, 106),    # green
    "disconnected": (239, 68, 68),   # red
    "recovery":    (249, 115, 22),   # orange
}


def _rounded_bar(draw, x, y_top, y_bot, width, radius, fill):
    """
    Defensive wrapper around rounded_rectangle — PIL raises ValueError if
    y1 < y0 (or x1 < x0). A single flipped coordinate here previously
    crashed Guardian at startup on Windows (where pystray/PIL actually
    import) even though it silently "worked" in dev/CI environments where
    the tray degrades to unavailable and this code never runs. Normalizing
    the box means a geometry slip draws a slightly-off icon instead of
    taking the whole app down.
    """
    y0, y1 = min(y_top, y_bot), max(y_top, y_bot)
    draw.rounded_rectangle([x, y0, x + width, y1], radius=radius, fill=fill)


def _build_icon_image(status: str = "idle", size: int = 64) -> "Image.Image":
    """
    Draws a simple signal-bar glyph with a status-colored dot, so the
    tray works even without a bundled .ico asset.
    """
    color = STATUS_COLORS.get(status, STATUS_COLORS["idle"])
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Signal bars (dark slate) — four bars of increasing height sharing a
    # common baseline, like a signal-strength glyph. Each tuple is
    # (x, top_y, bottom_y) with top_y always < bottom_y.
    bar_color = (18, 21, 31, 255)
    bar_w = size // 8
    baseline = size * 0.90
    bars = [
        (size * 0.12, size * 0.62, baseline),
        (size * 0.32, size * 0.48, baseline),
        (size * 0.52, size * 0.32, baseline),
        (size * 0.72, size * 0.14, baseline),
    ]
    for x, y_top, y_bot in bars:
        _rounded_bar(draw, x, y_top, y_bot, bar_w, bar_w // 2, bar_color)

    # Status dot, bottom-right corner
    dot_r = size * 0.24
    cx, cy = size * 0.78, size * 0.78
    draw.ellipse(
        [cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
        fill=(*color, 255),
        outline=(13, 15, 24, 255),
        width=2,
    )
    return img


class GuardianTray:
    """
    Thin controller around a pystray.Icon.

    Usage:
        tray = GuardianTray(
            on_start=..., on_stop=..., on_open=..., on_settings=..., on_exit=...
        )
        tray.run_detached()          # starts its own thread
        tray.set_status("monitoring")
        tray.notify("5G Connected", "Unlimited data active")
        tray.stop()
    """

    def __init__(
        self,
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
        on_open: Callable[[], None],
        on_settings: Callable[[], None],
        on_exit: Callable[[], None],
        app_name: str = "Airtel 5G Guardian",
    ):
        self.available = TRAY_AVAILABLE
        self._app_name = app_name
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_open = on_open
        self._on_settings = on_settings
        self._on_exit = on_exit
        self._icon: Optional["pystray.Icon"] = None
        self._status = "idle"

        if self.available:
            try:
                self._icon = pystray.Icon(
                    name="airtel_5g_guardian",
                    icon=_build_icon_image("idle"),
                    title=self._title_for("idle"),
                    menu=self._build_menu(),
                )
            except Exception as e:
                # A tray-icon failure is not worth taking the whole app
                # down for — degrade to "tray unavailable" instead. This
                # is exactly the kind of thing that crashed app startup
                # entirely before this guard existed.
                print(f"[Tray] Could not initialize system tray icon: {e}")
                self.available = False
                self._icon = None

    def _title_for(self, status: str) -> str:
        labels = {
            "idle": "Idle",
            "connecting": "Connecting…",
            "monitoring": "Monitoring — Active",
            "disconnected": "Disconnected",
            "recovery": "Recovery Mode",
        }
        return f"{self._app_name}\n{labels.get(status, status.title())}"

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem(self._app_name, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("▶  Start Monitoring", lambda: self._on_start()),
            pystray.MenuItem("⏹  Stop Monitoring", lambda: self._on_stop()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🖥  Open Dashboard", lambda: self._on_open(), default=True),
            pystray.MenuItem("⚙  Settings", lambda: self._on_settings()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌  Exit", lambda: self._on_exit()),
        )

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def run_detached(self):
        """Starts the tray icon loop on its own background thread."""
        if not self.available or self._icon is None:
            return
        self._icon.run_detached()

    def stop(self):
        if self.available and self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass

    # ── Live updates ──────────────────────────────────────────────────────

    def set_status(self, status: str):
        """status: idle | connecting | monitoring | disconnected | recovery"""
        self._status = status
        if not self.available or self._icon is None:
            return
        try:
            self._icon.icon = _build_icon_image(status)
            self._icon.title = self._title_for(status)
        except Exception:
            pass

    def notify(self, title: str, message: str):
        """Balloon/toast notification via the tray icon itself (fallback path)."""
        if not self.available or self._icon is None:
            return
        try:
            self._icon.notify(message, title)
        except Exception:
            pass

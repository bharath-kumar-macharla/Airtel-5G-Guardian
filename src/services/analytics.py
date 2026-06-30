"""
Guardian Analytics
------------------
Stores monitoring sessions and network events, then builds daily summaries.
"""

import csv
import json
from datetime import datetime, date
from pathlib import Path

from src.config import NETWORK_4G, NETWORK_5G, NETWORK_UNKNOWN


class GuardianAnalytics:

    def __init__(self):
        self._data_dir = Path("data")
        self._exports_dir = Path("exports")
        self._sessions_file = self._data_dir / "sessions.json"
        self._events_file = self._data_dir / "events.json"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._exports_dir.mkdir(parents=True, exist_ok=True)
        self._active_session = None

    def start_session(self) -> str:
        session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        now = self._now()
        self._active_session = {
            "id": session_id,
            "start": now,
            "end": None,
            "duration_seconds": 0,
            "network_seconds": {
                NETWORK_5G: 0,
                NETWORK_4G: 0,
                NETWORK_UNKNOWN: 0,
            },
            "switch_count": 0,
            "last_network": None,
            "last_change": now,
        }
        self._append_event("monitoring_started", "Monitoring started", session_id=session_id)
        return session_id

    def end_session(self):
        if not self._active_session:
            return

        self._close_current_segment()
        self._active_session["end"] = self._now()
        self._active_session["duration_seconds"] = self._seconds_between(
            self._active_session["start"],
            self._active_session["end"],
        )

        sessions = self._read_json(self._sessions_file, [])
        sessions.append(self._active_session)
        self._write_json(self._sessions_file, sessions)
        self._append_event(
            "monitoring_stopped",
            "Monitoring stopped",
            session_id=self._active_session["id"],
        )
        self._active_session = None

    def record_network_change(self, network: str):
        if not self._active_session:
            self.start_session()

        self._close_current_segment()
        if self._active_session["last_network"] is not None:
            self._active_session["switch_count"] += 1

        self._active_session["last_network"] = network
        self._active_session["last_change"] = self._now()
        label = self._network_label(network)
        self._append_event(
            "network_change",
            f"Network changed to {label}",
            network=network,
            session_id=self._active_session["id"],
        )

    def today_summary(self) -> dict:
        today_key = date.today().isoformat()
        sessions = [
            s for s in self._read_json(self._sessions_file, [])
            if s.get("start", "").startswith(today_key)
        ]
        active = self._active_snapshot()
        if active and active.get("start", "").startswith(today_key):
            sessions.append(active)

        events = [
            e for e in self._read_json(self._events_file, [])
            if e.get("time", "").startswith(today_key)
        ]

        total = sum(s.get("duration_seconds", 0) for s in sessions)
        five_g = sum(s.get("network_seconds", {}).get(NETWORK_5G, 0) for s in sessions)
        four_g = sum(s.get("network_seconds", {}).get(NETWORK_4G, 0) for s in sessions)
        switches = sum(s.get("switch_count", 0) for s in sessions)
        last_4g = next(
            (
                e.get("time")
                for e in reversed(events)
                if e.get("type") == "network_change" and e.get("network") == NETWORK_4G
            ),
            None,
        )

        return {
            "date": today_key,
            "sessions": len(sessions),
            "monitoring_seconds": total,
            "five_g_seconds": five_g,
            "four_g_seconds": four_g,
            "unknown_seconds": sum(
                s.get("network_seconds", {}).get(NETWORK_UNKNOWN, 0) for s in sessions
            ),
            "switch_count": switches,
            "uptime_percent": round((five_g / total) * 100, 1) if total else 0,
            "last_4g_drop": last_4g,
            "events": events[-50:],
        }

    def export_today_report(self) -> tuple[Path, Path]:
        summary = self.today_summary()
        day = summary["date"]
        report_path = self._exports_dir / f"guardian_report_{day}.txt"
        csv_path = self._exports_dir / f"guardian_sessions_{day}.csv"

        lines = [
            "Airtel 5G Guardian Report",
            f"Date: {day}",
            "",
            f"Monitoring time: {self.format_duration(summary['monitoring_seconds'])}",
            f"5G active time: {self.format_duration(summary['five_g_seconds'])}",
            f"4G risk time: {self.format_duration(summary['four_g_seconds'])}",
            f"Network switches: {summary['switch_count']}",
            f"5G uptime: {summary['uptime_percent']}%",
            f"Last 4G drop: {self.format_time(summary['last_4g_drop'])}",
            "",
            "Timeline",
        ]
        for event in summary["events"]:
            lines.append(f"{self.format_time(event.get('time'))}  {event.get('message', '')}")
        report_path.write_text("\n".join(lines), encoding="utf-8")

        sessions = [
            s for s in self._read_json(self._sessions_file, [])
            if s.get("start", "").startswith(day)
        ]
        active = self._active_snapshot()
        if active and active.get("start", "").startswith(day):
            sessions.append(active)
        with open(csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "session_id", "start", "end", "duration", "5g_time",
                "4g_time", "unknown_time", "switches",
            ])
            for session in sessions:
                network_seconds = session.get("network_seconds", {})
                writer.writerow([
                    session.get("id", ""),
                    session.get("start", ""),
                    session.get("end", ""),
                    self.format_duration(session.get("duration_seconds", 0)),
                    self.format_duration(network_seconds.get(NETWORK_5G, 0)),
                    self.format_duration(network_seconds.get(NETWORK_4G, 0)),
                    self.format_duration(network_seconds.get(NETWORK_UNKNOWN, 0)),
                    session.get("switch_count", 0),
                ])

        return report_path, csv_path

    @staticmethod
    def format_duration(seconds: int | float) -> str:
        seconds = int(seconds or 0)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}h {minutes}m"
        if minutes:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    @staticmethod
    def format_time(value: str | None) -> str:
        if not value:
            return "Never"
        try:
            return datetime.fromisoformat(value).strftime("%I:%M %p")
        except ValueError:
            return value

    def _active_snapshot(self) -> dict | None:
        if not self._active_session:
            return None
        snapshot = json.loads(json.dumps(self._active_session))
        now = self._now()
        if snapshot["last_network"]:
            elapsed = self._seconds_between(snapshot["last_change"], now)
            snapshot["network_seconds"][snapshot["last_network"]] += elapsed
        snapshot["duration_seconds"] = self._seconds_between(snapshot["start"], now)
        return snapshot

    def _close_current_segment(self):
        if not self._active_session or not self._active_session["last_network"]:
            return
        now = self._now()
        elapsed = self._seconds_between(self._active_session["last_change"], now)
        network = self._active_session["last_network"]
        self._active_session["network_seconds"][network] += elapsed
        self._active_session["last_change"] = now

    def _append_event(self, event_type: str, message: str, network: str | None = None, session_id: str | None = None):
        events = self._read_json(self._events_file, [])
        event = {
            "time": self._now(),
            "type": event_type,
            "message": message,
        }
        if network:
            event["network"] = network
        if session_id:
            event["session_id"] = session_id
        events.append(event)
        self._write_json(self._events_file, events[-1000:])

    def _read_json(self, path: Path, default):
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default

    def _write_json(self, path: Path, data):
        path.write_text(json.dumps(data, indent=4), encoding="utf-8")

    def _seconds_between(self, start: str, end: str) -> int:
        return int((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds())

    def _now(self) -> str:
        return datetime.now().replace(microsecond=0).isoformat()

    def _network_label(self, network: str) -> str:
        if network == NETWORK_5G:
            return "5G"
        if network == NETWORK_4G:
            return "4G"
        return "Unknown"

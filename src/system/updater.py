"""
Update Checker
--------------
v0.5.0 - Checks the project's GitHub releases for a newer version than
the one currently running. Network calls are wrapped so a failure (no
internet, rate limit, repo not found) never crashes the app — it just
means "no update available right now".
"""

from dataclasses import dataclass
from typing import Optional

import urllib.request
import urllib.error
import json
import re


@dataclass
class UpdateInfo:
    version: str
    url: str
    notes: str = ""


def _parse_version(version: str) -> tuple:
    """'v0.5.0' / '0.5.0' -> (0, 5, 0). Non-numeric parts are dropped."""
    cleaned = version.strip().lstrip("vV")
    parts = re.findall(r"\d+", cleaned)
    return tuple(int(p) for p in parts) if parts else (0,)


def is_newer(remote: str, local: str) -> bool:
    return _parse_version(remote) > _parse_version(local)


def check_for_update(current_version: str, repo: str = "", timeout: int = 6) -> Optional[UpdateInfo]:
    """
    Queries GitHub's "latest release" API for `repo` (format 'owner/name').
    Returns an UpdateInfo if a newer version is published, else None.
    Never raises — all failures resolve to None so callers can call this
    from a background thread without extra error handling.
    """
    if not repo:
        return None

    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    request = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Airtel-5G-Guardian-Updater",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return None

    remote_version = str(data.get("tag_name") or data.get("name") or "").strip()
    if not remote_version:
        return None

    if is_newer(remote_version, current_version):
        return UpdateInfo(
            version=remote_version.lstrip("vV"),
            url=data.get("html_url", f"https://github.com/{repo}/releases/latest"),
            notes=(data.get("body") or "")[:400],
        )

    return None

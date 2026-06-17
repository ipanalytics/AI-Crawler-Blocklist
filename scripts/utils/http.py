"""HTTP retrieval helpers with safe defaults."""

from __future__ import annotations

from dataclasses import dataclass

import requests


DEFAULT_TIMEOUT = 20
USER_AGENT = "AI-Crawler-Blocklist/0.1 (+https://github.com/ipanalytics/AI-Crawler-Blocklist)"


@dataclass(frozen=True)
class FetchResult:
    url: str
    ok: bool
    text: str
    status_code: int | None = None
    error: str | None = None


def fetch_text(url: str, timeout: int = DEFAULT_TIMEOUT) -> FetchResult:
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        return FetchResult(url=url, ok=False, text="", error=str(exc))
    return FetchResult(url=url, ok=True, text=response.text, status_code=response.status_code)


"""Rendering helpers for generated artifacts."""

from __future__ import annotations

from datetime import UTC, datetime

PROJECT = "AI-Crawler-Blocklist"
POLICY = "official/operator-published sources only"
SOURCE = "https://github.com/ipanalytics/AI-Crawler-Blocklist"
WARNING = "Review before hard drop. Search crawlers may affect visibility."


def generated_at() -> str:
    import os

    return os.environ.get("CRAWLERSCOPE_GENERATED_AT") or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def header(timestamp: str, comment: str = "#") -> str:
    return "\n".join(
        [
            f"{comment} {PROJECT}",
            f"{comment} Generated: {timestamp}",
            f"{comment} Source: {SOURCE}",
            f"{comment} Policy: {POLICY}",
            f"{comment} WARNING: {WARNING}",
            "",
        ]
    )


from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_outputs import DIST, expected_outputs, validate


def test_expected_outputs_list_is_complete() -> None:
    expected = set(expected_outputs())
    assert "ai-ips-verified-v4.txt" in expected
    assert "robots-ai-all-block.txt" in expected
    assert "metadata.json" in expected
    assert "sources-report.md" in expected


def test_generated_files_validate_after_build() -> None:
    missing = [name for name in expected_outputs() if not (DIST / name).exists()]
    assert missing == []
    assert validate() == []


def test_metadata_has_required_counts_and_health() -> None:
    metadata = json.loads((DIST / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["project"] == "AI-Crawler-Blocklist"
    assert "verified_ipv4_prefixes" in metadata["counts"]
    assert "failed_sources" in metadata
    assert isinstance(metadata["sources"], list)


def test_robots_only_tokens_do_not_leak_into_ip_drop_outputs() -> None:
    combined = ""
    for name in ["ai-ips-verified-all.txt", "iptables-ai.sh", "nftables-ai.nft", "pf-ai-table.conf"]:
        combined += (Path("dist") / name).read_text(encoding="utf-8")
    assert "Google-Extended" not in combined
    assert "Applebot-Extended" not in combined
    assert "Bytespider" not in combined


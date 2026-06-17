from __future__ import annotations

import copy

import pytest

from scripts.normalize_sources import SOURCES_PATH, host_is_aggregator, load_json, load_policy, normalize_sources


def source_by_id(sources: list[dict], source_id: str) -> dict:
    return next(source for source in sources if source["id"] == source_id)


def test_sources_schema_and_normalization() -> None:
    normalized = normalize_sources()
    ids = {source["id"] for source in normalized}
    assert "openai-gptbot" in ids
    assert "anthropic-claude-bots" in ids
    assert "applebot-extended" in ids


def test_robots_only_tokens_never_enter_ip_drop() -> None:
    normalized = normalize_sources()
    for source_id in ("google-extended", "applebot-extended"):
        source = source_by_id(normalized, source_id)
        assert source["robotsOnly"] is True
        assert source["enforcement"] == "robots-only"
        assert source["ipPolicy"] == "robots-only"


def test_documented_user_agent_only_not_verified_drop() -> None:
    normalized = normalize_sources()
    source = source_by_id(normalized, "openai-adsbot")
    assert source["sourceType"] == "documented_user_agent"
    assert source["ipPolicy"] == "ua-only"
    assert source["enforcement"] == "block"


def test_weak_cn_and_static_watch_not_verified_drop() -> None:
    normalized = normalize_sources()
    for source_id in ("bytespider", "baiduspider-ai-watch", "petalbot-ai-watch", "meta-ai-crawlers"):
        source = source_by_id(normalized, source_id)
        assert source["ipPolicy"] in {"ua-only", "static-watch"}
        assert source["enforcement"] in {"block", "log-only"}
        assert source["ipPolicy"] != "verified-drop"


def test_aggregator_hosts_are_rejected() -> None:
    policy = load_policy()
    assert host_is_aggregator("https://raw.githubusercontent.com/example/list/main/bots.txt", policy)
    data = load_json(SOURCES_PATH)
    bad = copy.deepcopy(data)
    bad["sources"][0]["sourceUrl"] = "https://raw.githubusercontent.com/example/list/main/bots.txt"
    with pytest.raises(ValueError, match="aggregator"):
        normalize_sources(bad, policy)


def test_non_ai_categories_excluded_unless_explicit_ai_use() -> None:
    policy = load_policy()
    data = load_json(SOURCES_PATH)
    sample = copy.deepcopy(data["sources"][0])
    sample.update(
        {
            "id": "generic-search-sample",
            "category": "search",
            "sourceUrl": "https://example.com/searchbot.json",
            "sourceType": "official_json",
            "authoritative": True,
        }
    )
    modified = {"schemaVersion": 1, "sources": [sample]}
    normalized = normalize_sources(modified, policy)
    assert normalized[0]["includeInAiOutputs"] is False
    assert normalized[0]["ipPolicy"] == "no-ip"
    assert normalized[0]["enforcement"] == "exclude"

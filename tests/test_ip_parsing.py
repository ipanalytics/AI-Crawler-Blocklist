from __future__ import annotations

from scripts.fetch_sources import fetch_source, parse_embedded_json_prefixes, parse_json_prefixes, parse_text_prefixes
from scripts.utils.http import FetchResult
from scripts.utils.ip import split_networks, stringify_networks


def test_valid_invalid_split_dedupe_and_sort() -> None:
    parsed = split_networks(
        [
            "203.0.113.2",
            "203.0.113.0/24",
            "2001:db8::/32",
            "2001:db8::1/128",
            "bad-cidr",
            "198.51.100.0/24"
        ]
    )
    assert stringify_networks(parsed.ipv4) == ["198.51.100.0/24", "203.0.113.0/24"]
    assert stringify_networks(parsed.ipv6) == ["2001:db8::/32"]
    assert parsed.invalid == ["bad-cidr"]


def test_json_text_and_embedded_json_parsers() -> None:
    assert parse_json_prefixes('{"prefixes":[{"ipv4Prefix":"192.0.2.0/24"},{"ipv6Prefix":"2001:db8::/32"}]}') == [
        "192.0.2.0/24",
        "2001:db8::/32",
    ]
    assert parse_text_prefixes("192.0.2.1\n# comment\n2001:db8::/48\n") == ["192.0.2.1", "2001:db8::/48"]
    html = '<html><code>{"prefixes":[{"ipv4Prefix":"198.51.100.0/24"}]}</code></html>'
    assert parse_embedded_json_prefixes(html) == ["198.51.100.0/24"]


def test_source_failure_is_recorded_without_abort() -> None:
    source = {
        "id": "example-ai",
        "sourceType": "official_json",
        "sourceUrl": "https://example.com/feed.json",
        "ipPolicy": "verified-drop",
        "robotsOnly": False,
    }

    def failing_fetcher(url: str) -> FetchResult:
        return FetchResult(url=url, ok=False, text="", error="temporary failure")

    result = fetch_source(source, fetcher=failing_fetcher)
    assert result.status == "failed"
    assert result.error and "temporary failure" in result.error
    assert result.prefixes_v4 == []
    assert result.prefixes_v6 == []


def test_static_watch_source_does_not_fetch_and_normalizes_static_prefixes() -> None:
    source = {
        "id": "static-watch",
        "sourceType": "known_static",
        "sourceUrl": "https://example.com/docs",
        "ipPolicy": "static-watch",
        "robotsOnly": False,
        "staticPrefixes": ["203.0.113.1", "203.0.113.0/24", "invalid"],
    }

    def unexpected_fetcher(url: str) -> FetchResult:
        raise AssertionError("static-watch source should not fetch")

    result = fetch_source(source, fetcher=unexpected_fetcher)
    assert result.status == "ok"
    assert result.prefixes_v4 == ["203.0.113.0/24"]
    assert result.invalid == ["invalid"]


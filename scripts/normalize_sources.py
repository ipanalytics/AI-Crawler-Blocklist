"""Normalize AI crawler source policy."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SOURCES_PATH = ROOT / "config" / "sources.json"
POLICY_PATH = ROOT / "config" / "policy.yml"
SCHEMA_PATH = ROOT / "config" / "sources.schema.json"


@dataclass(frozen=True)
class NormalizedSource:
    raw: dict
    confidence: int
    enforcement: str
    ip_policy: str
    include_in_ai_outputs: bool


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_policy(path: Path = POLICY_PATH) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_schema(data: dict) -> None:
    schema = load_json(SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda error: error.path)
    if errors:
        message = "; ".join(f"{list(error.path)}: {error.message}" for error in errors)
        raise ValueError(message)


def host_is_aggregator(url: str, policy: dict) -> bool:
    host = urlparse(url).netloc.lower()
    source_host = host.removeprefix("www.")
    for blocked in policy["aggregator_hosts"]:
        if source_host == blocked or source_host.endswith(f".{blocked}"):
            return True
    return False


def confidence_for(source: dict, policy: dict) -> int:
    if source.get("robotsOnly") is True:
        return 100
    base = int(policy["source_type_confidence"].get(source["sourceType"], 10))
    if not source.get("authoritative", False):
        base = min(base, 50)
    if source.get("operatorCountry") in policy.get("cn_watch_countries", []):
        base = min(base, 50)
    if source["operator"] in policy.get("watch_operators", []) and not source.get("authoritative"):
        base = min(base, 40)
    return base


def classify_source(source: dict, policy: dict) -> NormalizedSource:
    category = source["category"]
    confidence = confidence_for(source, policy)
    ai_category = category in policy["allowed_ai_categories"]
    robots_only = source.get("robotsOnly", False)
    has_ip_feed = source["sourceType"] in {"official_json", "official_text", "official_embedded_json", "official_html"}

    if robots_only:
        enforcement = "robots-only"
        ip_policy = "robots-only"
    elif not ai_category:
        enforcement = "exclude"
        ip_policy = "no-ip"
    elif confidence >= policy["confidence_mapping"]["verified_drop_min"] and has_ip_feed:
        enforcement = "drop"
        ip_policy = "verified-drop"
    elif confidence >= policy["confidence_mapping"]["high_confidence_min"]:
        enforcement = "challenge"
        ip_policy = "high-confidence"
    elif confidence >= policy["confidence_mapping"]["ua_block_min"]:
        enforcement = "block"
        ip_policy = "ua-only"
    else:
        enforcement = "log-only"
        ip_policy = "static-watch"

    normalized = dict(source)
    normalized.update(
        {
            "confidence": confidence,
            "enforcement": enforcement,
            "ipPolicy": ip_policy,
            "includeInAiOutputs": ai_category,
        }
    )
    return NormalizedSource(normalized, confidence, enforcement, ip_policy, ai_category)


def normalize_sources(data: dict | None = None, policy: dict | None = None) -> list[dict]:
    data = data or load_json(SOURCES_PATH)
    policy = policy or load_policy()
    validate_schema(data)
    seen_ids: set[str] = set()
    normalized: list[dict] = []
    for source in data["sources"]:
        if source["id"] in seen_ids:
            raise ValueError(f"duplicate source id: {source['id']}")
        seen_ids.add(source["id"])
        if host_is_aggregator(source["sourceUrl"], policy):
            raise ValueError(f"aggregator source URL rejected: {source['id']} {source['sourceUrl']}")
        for url in source.get("sourceUrls", []):
            if host_is_aggregator(url, policy):
                raise ValueError(f"aggregator source URL rejected: {source['id']} {url}")
        normalized.append(classify_source(source, policy).raw)
    return sorted(normalized, key=lambda item: item["id"])


def summarize(normalized: list[dict]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {"enforcement": {}, "ipPolicy": {}}
    for source in normalized:
        summary["enforcement"][source["enforcement"]] = summary["enforcement"].get(source["enforcement"], 0) + 1
        summary["ipPolicy"][source["ipPolicy"]] = summary["ipPolicy"].get(source["ipPolicy"], 0) + 1
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize and validate AI crawler sources.")
    parser.add_argument("--check", action="store_true", help="validate and summarize sources")
    parser.add_argument("--json", action="store_true", help="emit normalized JSON")
    args = parser.parse_args(argv)
    normalized = normalize_sources()
    if args.json:
        sys.stdout.write(json.dumps({"sources": normalized}, indent=2, sort_keys=True) + "\n")
    else:
        summary = summarize(normalized)
        sys.stdout.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


"""Fetch and parse official AI crawler source feeds."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.normalize_sources import normalize_sources
from scripts.utils.http import FetchResult, fetch_text
from scripts.utils.ip import ParsedNetworks, split_networks, stringify_networks

PREFIX_KEYS = {"ipv4Prefix", "ipv6Prefix", "ipPrefix", "prefix", "cidr", "network"}
CIDR_RE = re.compile(r"(?<![\w.:/-])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:/\d{1,2})?|(?:[0-9a-fA-F]{0,4}:){2,}[0-9a-fA-F:/]+")


@dataclass
class SourceFetch:
    source: dict
    status: str
    prefixes_v4: list[str] = field(default_factory=list)
    prefixes_v6: list[str] = field(default_factory=list)
    invalid: list[str] = field(default_factory=list)
    error: str | None = None


def _walk_json(value: object) -> Iterable[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in PREFIX_KEYS and isinstance(item, str):
                yield item
            else:
                yield from _walk_json(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_json(item)


def parse_json_prefixes(text: str) -> list[str]:
    data = json.loads(text)
    return list(_walk_json(data))


def parse_text_prefixes(text: str) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        cleaned = line.split("#", 1)[0].strip().strip(",")
        if not cleaned:
            continue
        values.extend(match.group(0) for match in CIDR_RE.finditer(cleaned))
    return values


def parse_embedded_json_prefixes(text: str) -> list[str]:
    for start in [match.start() for match in re.finditer(r"\{", text)]:
        depth = 0
        for index in range(start, len(text)):
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start : index + 1]
                    if "prefixes" not in candidate:
                        break
                    try:
                        return parse_json_prefixes(candidate)
                    except json.JSONDecodeError:
                        break
    return parse_text_prefixes(text)


def parse_prefixes(source: dict, text: str) -> list[str]:
    source_type = source["sourceType"]
    if source_type == "official_json":
        return parse_json_prefixes(text)
    if source_type == "official_text":
        return parse_text_prefixes(text)
    if source_type == "official_embedded_json":
        return parse_embedded_json_prefixes(text)
    if source_type in {"known_static", "manual_static"}:
        return list(source.get("staticPrefixes", []))
    return []


def normalize_prefixes(prefixes: list[str]) -> ParsedNetworks:
    return split_networks(prefixes)


def fetch_source(source: dict, fetcher: Callable[[str], FetchResult] = fetch_text) -> SourceFetch:
    if source.get("robotsOnly") or source["ipPolicy"] in {"robots-only", "ua-only", "static-watch", "no-ip"}:
        parsed = normalize_prefixes(list(source.get("staticPrefixes", [])))
        return SourceFetch(
            source=source,
            status="ok",
            prefixes_v4=stringify_networks(parsed.ipv4),
            prefixes_v6=stringify_networks(parsed.ipv6),
            invalid=parsed.invalid,
        )

    all_prefixes: list[str] = list(source.get("staticPrefixes", []))
    urls = source.get("sourceUrls") or [source["sourceUrl"]]
    errors: list[str] = []
    for url in urls:
        result = fetcher(url)
        if not result.ok:
            errors.append(f"{url}: {result.error}")
            continue
        try:
            all_prefixes.extend(parse_prefixes(source, result.text))
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{url}: {exc}")

    parsed = normalize_prefixes(all_prefixes)
    status = "ok" if not errors else "failed" if not all_prefixes else "partial"
    return SourceFetch(
        source=source,
        status=status,
        prefixes_v4=stringify_networks(parsed.ipv4),
        prefixes_v6=stringify_networks(parsed.ipv6),
        invalid=parsed.invalid,
        error="; ".join(errors) if errors else None,
    )


def fetch_all_sources(fetcher: Callable[[str], FetchResult] = fetch_text) -> list[SourceFetch]:
    return [fetch_source(source, fetcher=fetcher) for source in normalize_sources()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch official AI crawler sources.")
    parser.add_argument("--metadata", type=Path, help="write fetch metadata JSON")
    args = parser.parse_args(argv)
    results = fetch_all_sources()
    payload = {
        "sources": [
            {
                "id": result.source["id"],
                "status": result.status,
                "prefixes_v4": len(result.prefixes_v4),
                "prefixes_v6": len(result.prefixes_v6),
                "invalid": result.invalid,
                "error": result.error,
            }
            for result in results
        ]
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.metadata:
        args.metadata.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Build all generated AI crawler blocklist artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.fetch_sources import SourceFetch, fetch_all_sources
from scripts.normalize_sources import normalize_sources
from scripts.render_firewall_configs import render_all_configs
from scripts.utils.render import header, generated_at
from scripts.utils.ua import cloudflare_contains_expression, regex_for_agent, unique_user_agents

DIST = ROOT / "dist"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _lines(timestamp: str, values: list[str], comment: str = "#") -> str:
    return header(timestamp, comment) + "\n".join(values) + ("\n" if values else "")


def _source_map(results: list[SourceFetch]) -> dict[str, SourceFetch]:
    return {result.source["id"]: result for result in results}


def _verified_networks(results: list[SourceFetch], family: str, policy: str = "verified-drop") -> list[str]:
    values: set[str] = set()
    for result in results:
        if result.source.get("ipPolicy") != policy:
            continue
        values.update(result.prefixes_v4 if family == "v4" else result.prefixes_v6)
    return sorted(values)


def _watch_agents(sources: list[dict], *, country: str | None = None) -> list[str]:
    values: set[str] = set()
    for source in sources:
        if source["ipPolicy"] not in {"static-watch", "ua-only"}:
            continue
        if country and source.get("operatorCountry") != country:
            continue
        values.update(source.get("userAgentPatterns", []))
    return sorted(values, key=str.lower)


def _robots(tokens: list[str], timestamp: str) -> str:
    blocks = [f"User-agent: {token}\nDisallow: /" for token in tokens]
    return header(timestamp, "#") + "\n\n".join(blocks) + "\n"


def _metadata(timestamp: str, sources: list[dict], results: list[SourceFetch], agents: list[str], robots_tokens: list[str]) -> dict:
    verified_v4 = _verified_networks(results, "v4")
    verified_v6 = _verified_networks(results, "v6")
    source_rows = []
    for result in results:
        source = result.source
        source_rows.append(
            {
                "id": source["id"],
                "operator": source["operator"],
                "service": source["service"],
                "status": result.status,
                "prefixes_v4": len(result.prefixes_v4),
                "prefixes_v6": len(result.prefixes_v6),
                "confidence": source["confidence"],
                "enforcement": source["enforcement"],
                "ipPolicy": source["ipPolicy"],
                "error": result.error,
            }
        )
    return {
        "generated_at": timestamp,
        "project": "AI-Crawler-Blocklist",
        "policy": "official/operator-published sources only",
        "counts": {
            "verified_ipv4_prefixes": len(verified_v4),
            "verified_ipv6_prefixes": len(verified_v6),
            "user_agent_patterns": len(agents),
            "robots_tokens": len(robots_tokens),
        },
        "sources": source_rows,
        "failed_sources": [row for row in source_rows if row["status"] in {"failed", "partial"}],
    }


def _report(timestamp: str, results: list[SourceFetch]) -> str:
    rows = [
        "| Source | Operator | Enforcement | IP policy | Status | IPv4 | IPv6 |",
        "| --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for result in results:
        source = result.source
        rows.append(
            f"| `{source['id']}` | {source['operator']} | {source['enforcement']} | {source['ipPolicy']} | {result.status} | {len(result.prefixes_v4)} | {len(result.prefixes_v6)} |"
        )
    return header(timestamp, "<!--").replace("<!-- ", "<!-- ").replace("\n", " -->\n", 5) + "# Sources Report\n\n" + "\n".join(rows) + "\n"


def build() -> dict:
    timestamp = generated_at()
    sources = normalize_sources()
    results = fetch_all_sources()
    agents = unique_user_agents(sources)
    robots_tokens = unique_user_agents(sources, include_robots_only=True)
    regexes = [regex_for_agent(agent) for agent in agents]
    verified_v4 = _verified_networks(results, "v4")
    verified_v6 = _verified_networks(results, "v6")
    high_v4 = _verified_networks(results, "v4", policy="high-confidence")
    high_v6 = _verified_networks(results, "v6", policy="high-confidence")
    cn_watch = _watch_agents(sources, country="CN")

    DIST.mkdir(parents=True, exist_ok=True)
    _write(DIST / "ai-ips-verified-v4.txt", _lines(timestamp, verified_v4))
    _write(DIST / "ai-ips-verified-v6.txt", _lines(timestamp, verified_v6))
    _write(DIST / "ai-ips-verified-all.txt", _lines(timestamp, verified_v4 + verified_v6))
    _write(DIST / "ai-ips-high-confidence-v4.txt", _lines(timestamp, high_v4))
    _write(DIST / "ai-ips-high-confidence-v6.txt", _lines(timestamp, high_v6))
    _write(DIST / "ai-user-agents.txt", _lines(timestamp, agents))
    _write(DIST / "ai-user-agents-regex.txt", _lines(timestamp, regexes))
    _write(DIST / "ai-user-agents-nginx-map.conf", render_all_configs(timestamp, verified_v4, verified_v6, agents, regexes)["nginx-ai-map.conf"])
    _write(DIST / "ai-user-agents-apache-setenvif.conf", render_all_configs(timestamp, verified_v4, verified_v6, agents, regexes)["apache-ai-setenvif.conf"])
    _write(DIST / "ai-user-agents-cloudflare-expression.txt", header(timestamp) + cloudflare_contains_expression(agents) + "\n")
    _write(DIST / "ai-cn-user-agents-watch.txt", _lines(timestamp, cn_watch))
    _write(DIST / "ai-cn-user-agents-block.txt", _lines(timestamp, cn_watch))
    _write(DIST / "ai-watch-asn.txt", _lines(timestamp, ["AS_CN_AI_WATCH", "AS_CLOUD_AI_WATCH"]))
    _write(DIST / "ai-cloud-hosting-watch.txt", _lines(timestamp, ["aws", "gcp", "azure", "oracle-cloud", "cloudflare-workers"]))
    training_tokens = [source["userAgentPatterns"][0] for source in sources if "training" in source.get("aiUse", []) or source.get("robotsOnly")]
    _write(DIST / "robots-ai-training-block.txt", _robots(sorted(set(training_tokens), key=str.lower), timestamp))
    _write(DIST / "robots-ai-all-block.txt", _robots(robots_tokens, timestamp))
    _write(DIST / "robots-ai-chinese-bots-block.txt", _robots(cn_watch, timestamp))
    safe_tokens = sorted({"GPTBot", "ClaudeBot", "PerplexityBot", "CCBot", "Google-Extended", "Applebot-Extended"})
    _write(DIST / "robots-search-safe-ai-optout.txt", _robots(safe_tokens, timestamp))

    configs = render_all_configs(timestamp, verified_v4, verified_v6, agents, regexes)
    for name, text in configs.items():
        _write(DIST / name, text)

    metadata = _metadata(timestamp, sources, results, agents, robots_tokens)
    _write(DIST / "metadata.json", json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    _write(DIST / "sources-report.md", _report(timestamp, results))
    return metadata


def main() -> int:
    metadata = build()
    counts = metadata["counts"]
    sys.stdout.write(
        "Built AI crawler blocklists: "
        f"v4={counts['verified_ipv4_prefixes']} "
        f"v6={counts['verified_ipv6_prefixes']} "
        f"ua={counts['user_agent_patterns']} "
        f"failed={len(metadata['failed_sources'])}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

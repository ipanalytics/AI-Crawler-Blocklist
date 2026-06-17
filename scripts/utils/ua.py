"""User-agent rendering helpers."""

from __future__ import annotations

import re


def unique_user_agents(sources: list[dict], *, include_robots_only: bool = False) -> list[str]:
    values: set[str] = set()
    for source in sources:
        if source.get("enforcement") == "exclude":
            continue
        if source.get("robotsOnly") and not include_robots_only:
            continue
        values.update(source.get("userAgentPatterns", []))
    return sorted(values, key=str.lower)


def regex_for_agent(agent: str) -> str:
    return re.escape(agent)


def cloudflare_contains_expression(agents: list[str]) -> str:
    parts = [f'(http.user_agent contains "{agent}")' for agent in agents]
    return " or\n".join(parts)


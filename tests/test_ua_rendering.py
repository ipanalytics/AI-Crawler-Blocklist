from __future__ import annotations

from scripts.utils.ua import cloudflare_contains_expression, regex_for_agent, unique_user_agents


def test_user_agents_are_unique_sorted_and_exclude_robots_only_by_default() -> None:
    sources = [
        {"enforcement": "drop", "userAgentPatterns": ["GPTBot", "ClaudeBot"]},
        {"enforcement": "robots-only", "robotsOnly": True, "userAgentPatterns": ["Google-Extended"]},
        {"enforcement": "drop", "userAgentPatterns": ["GPTBot"]},
    ]
    assert unique_user_agents(sources) == ["ClaudeBot", "GPTBot"]
    assert unique_user_agents(sources, include_robots_only=True) == ["ClaudeBot", "Google-Extended", "GPTBot"]


def test_regex_and_cloudflare_expression_escape_agents() -> None:
    assert regex_for_agent("ChatGPT-User") == "ChatGPT\\-User"
    expression = cloudflare_contains_expression(["GPTBot", "ClaudeBot"])
    assert '(http.user_agent contains "GPTBot")' in expression
    assert " or\n" in expression


from __future__ import annotations

from pathlib import Path

import yaml


WORKFLOW_DIR = Path(".github/workflows")


def load_workflow(name: str) -> dict:
    return yaml.safe_load((WORKFLOW_DIR / name).read_text(encoding="utf-8"))


def workflow_on(workflow: dict) -> dict:
    return workflow.get("on") or workflow[True]


def test_update_workflow_schedule_and_summary() -> None:
    workflow = load_workflow("update.yml")
    assert workflow_on(workflow)["schedule"][0]["cron"] == "17 */6 * * *"
    text = (WORKFLOW_DIR / "update.yml").read_text(encoding="utf-8")
    assert "verified_ipv4_prefixes" in text
    assert "verified_ipv6_prefixes" in text
    assert "user_agent_patterns" in text
    assert "failed_sources" in text
    assert "git status --porcelain dist" in text


def test_validate_pr_checks_generated_dist_consistency() -> None:
    workflow = load_workflow("validate-pr.yml")
    assert "pull_request" in workflow_on(workflow)
    text = (WORKFLOW_DIR / "validate-pr.yml").read_text(encoding="utf-8")
    assert "python scripts/normalize_sources.py --check" in text
    assert "python scripts/build.py" in text
    assert "git status --porcelain dist" in text
    assert "exit 1" in text


def test_release_workflow_daily_release() -> None:
    workflow = load_workflow("release.yml")
    assert workflow_on(workflow)["schedule"][0]["cron"] == "43 2 * * *"
    text = (WORKFLOW_DIR / "release.yml").read_text(encoding="utf-8")
    assert "daily-$(date -u +%Y-%m-%d)" in text
    assert "gh release create" in text
    assert "gh release upload" in text
    assert "ai-crawler-blocklist-dist.tar.gz" in text

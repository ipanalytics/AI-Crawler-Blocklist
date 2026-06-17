"""Check that required repository files are present in CI checkouts."""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_PATHS = [
    "config/generators.yml",
    "config/policy.yml",
    "config/sources.json",
    "config/sources.schema.json",
    "dist/metadata.json",
    "dist/sources-report.md",
    "dist/ai-ips-verified-v4.txt",
    "dist/ai-ips-verified-v6.txt",
    "dist/ai-user-agents.txt",
    "dist/robots-ai-all-block.txt",
    "tests/conftest.py",
    "tests/test_ip_parsing.py",
    "tests/test_outputs.py",
    "tests/test_sources_schema.py",
    "tests/test_ua_rendering.py",
    "tests/test_workflows.py",
]


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not Path(path).exists()]
    if missing:
        sys.stderr.write("Repository checkout is incomplete. Missing required files:\n")
        for path in missing:
            sys.stderr.write(f"  - {path}\n")
        sys.stderr.write("\nUpload the full project tree, including config/, dist/, tests/, scripts/, and workflows.\n")
        return 1
    sys.stdout.write(f"Repository integrity check passed: {len(REQUIRED_PATHS)} required files present.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


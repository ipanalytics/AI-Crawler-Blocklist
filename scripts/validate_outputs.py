"""Validate generated dist artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DIST = ROOT / "dist"


def expected_outputs() -> list[str]:
    data = yaml.safe_load((ROOT / "config" / "generators.yml").read_text(encoding="utf-8"))
    return [item.removeprefix("dist/") for item in data["outputs"]]


def validate() -> list[str]:
    errors: list[str] = []
    for name in expected_outputs():
        path = DIST / name
        if not path.exists():
            errors.append(f"missing {name}")
            continue
        text = path.read_text(encoding="utf-8")
        if name == "metadata.json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append(f"metadata invalid JSON: {exc}")
            continue
        if not any("AI-Crawler-Blocklist" in line for line in text.splitlines()[:5]):
            errors.append(f"missing header in {name}")

    metadata_path = DIST / "metadata.json"
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if "failed_sources" not in metadata or "counts" not in metadata:
            errors.append("metadata missing failed_sources or counts")

    combined_drop = ""
    for name in ["ai-ips-verified-all.txt", "iptables-ai.sh", "nftables-ai.nft", "pf-ai-table.conf"]:
        path = DIST / name
        if path.exists():
            combined_drop += path.read_text(encoding="utf-8")
    for token in ("Google-Extended", "Applebot-Extended", "Bytespider", "Baiduspider", "PetalBot"):
        if token in combined_drop:
            errors.append(f"{token} leaked into verified IP/firewall drop output")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        sys.stderr.write("\n".join(errors) + "\n")
        return 1
    sys.stdout.write(f"validated {len(expected_outputs())} dist outputs\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

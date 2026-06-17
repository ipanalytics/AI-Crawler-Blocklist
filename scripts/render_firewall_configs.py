"""Render firewall and web-server config snippets."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scripts.utils.render import header

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates"


def env() -> Environment:
    return Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False, trim_blocks=True, lstrip_blocks=True)


def render_template(name: str, **context: object) -> str:
    return env().get_template(name).render(**context)


def render_all_configs(timestamp: str, v4: list[str], v6: list[str], agents: list[str], regexes: list[str]) -> dict[str, str]:
    context = {
        "header": header(timestamp),
        "hash_header": header(timestamp, "#"),
        "slash_header": header(timestamp, "//"),
        "v4": v4,
        "v6": v6,
        "agents": agents,
        "regexes": regexes,
    }
    return {
        "nginx-ai-map.conf": render_template("nginx-ai-map.conf.j2", **context),
        "nginx-ai-deny.conf": render_template("nginx-ai-deny.conf.j2", **context),
        "apache-ai-setenvif.conf": render_template("apache-ai-setenvif.conf.j2", **context),
        "cloudflare-ai-expression.txt": render_template("cloudflare-ai-expression.txt.j2", **context),
        "iptables-ai.sh": render_template("iptables-ai.sh.j2", **context),
        "nftables-ai.nft": render_template("nftables-ai.nft.j2", **context),
        "pf-ai-table.conf": render_template("pf-ai-table.conf.j2", **context),
        "caddy-ai-block.caddy": render_template("caddy-ai-block.caddy.j2", **context),
        "haproxy-ai-acl.cfg": render_template("haproxy-ai-acl.cfg.j2", **context),
        "traefik-ai-middleware.yml": render_template("traefik-ai-middleware.yml.j2", **context),
    }


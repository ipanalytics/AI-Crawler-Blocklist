# AI-Crawler-Blocklist

AI-Crawler-Blocklist publishes AI crawler blocklists and deployment-ready firewall snippets from official operator-published sources. It separates verified IP ranges, user-agent rules, robots.txt controls, and watch lists so site operators can choose the right enforcement level without mixing signal quality.



<p align="center">
  <a href="https://github.com/ipanalytics/AI-Crawler-Blocklist/actions/workflows/update.yml"><img alt="Update" src="https://img.shields.io/github/actions/workflow/status/ipanalytics/AI-Crawler-Blocklist/update.yml?branch=main&label=update"></a>
  <a href="https://github.com/ipanalytics/AI-Crawler-Blocklist/actions/workflows/validate-pr.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/ipanalytics/AI-Crawler-Blocklist/validate-pr.yml?branch=main&label=ci"></a>
  <a href="https://github.com/ipanalytics/AI-Crawler-Blocklist/releases"><img alt="Release" src="https://img.shields.io/github/v/release/ipanalytics/AI-Crawler-Blocklist?display_name=tag&sort=date"></a>
  <img alt="Dataset" src="https://img.shields.io/badge/dataset-generated%20dist-2f6fed">
  <img alt="Python" src="https://img.shields.io/badge/python-3.12-3776ab">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
</p>

---

## Links

| Resource | URL |
| --- | --- |
| Generated artifacts | [`dist/`](./dist) |
| Source policy | [`docs/source-policy.md`](./docs/source-policy.md) |
| Firewall deployment notes | [`docs/firewalls.md`](./docs/firewalls.md) |
| Operating modes | [`docs/modes.md`](./docs/modes.md) |
| Source health report | [`dist/sources-report.md`](./dist/sources-report.md) |
| Machine-readable metadata | [`dist/metadata.json`](./dist/metadata.json) |

## Overview

AI-Crawler-Blocklist is built for publishers, application operators, infrastructure teams, and security engineers who need repeatable controls for AI training crawlers, AI search bots, assistant fetchers, and related indexing systems.

The repository consumes curated source definitions from `config/sources.json`, validates the source policy, fetches official IP feeds where available, normalizes CIDRs, and renders platform-specific outputs under `dist/`. Source failures are recorded in metadata instead of failing the entire build, which keeps scheduled updates operational while preserving source health visibility.

## System Behavior

```text
config/sources.json
        |
        v
scripts/normalize_sources.py  -> confidence, enforcement, source policy
        |
        v
scripts/fetch_sources.py      -> official JSON/text/embedded JSON/static prefixes
        |
        v
scripts/build.py              -> deterministic dist artifacts
        |
        v
dist/metadata.json + firewall snippets + robots.txt + plain lists
```

Enforcement is derived from source quality:

| Class | Source quality | Output behavior |
| --- | --- | --- |
| `verified-drop` | Official crawler-specific IP/CIDR feed | Eligible for IP hard drop |
| `ua-only` | Documented user-agent without verified IP feed | User-agent block rules only |
| `robots-only` | Robots token such as `Google-Extended` | robots.txt outputs only |
| `static-watch` | Broad static ranges, CN/watch, platform ranges, weak signals | Observe, challenge, or rate-limit |

## Features

- Verified IPv4/IPv6 lists for official AI crawler IP feeds.
- User-agent lists, regex lists, nginx maps, Apache SetEnvIf rules, and Cloudflare expressions.
- robots.txt snippets for training opt-out, all AI bots, CN/watch bots, and search-safe AI opt-out.
- iptables/ipset, nftables, pf/pfSense, Caddy, HAProxy, and Traefik outputs.
- Deterministic builds with fixed timestamp support via `CRAWLERSCOPE_GENERATED_AT`.
- Machine-readable metadata with counts, source health, confidence, enforcement, and failed sources.
- Scheduled GitHub Actions update workflow and daily release workflow.

## Quick Start

```bash
git clone https://github.com/ipanalytics/AI-Crawler-Blocklist.git
cd AI-Crawler-Blocklist
make install-dev
make build
make validate
make test
```

For sandboxed environments where `uv` must keep all state inside the worktree:

```bash
UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python \
  uv run --python 3.12 python scripts/build.py
```

## Installation

The generated files are intended to be consumed directly from GitHub raw URLs or vendored into your own configuration management.

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/metadata.json
```

Pinning to a release tag is recommended for controlled production rollout:

```bash
curl -fsSL https://github.com/ipanalytics/AI-Crawler-Blocklist/releases/latest/download/ai-crawler-blocklist-dist.tar.gz \
  -o ai-crawler-blocklist-dist.tar.gz
```

## Usage Examples

### robots.txt

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/robots-ai-all-block.txt \
  -o /var/www/html/robots.txt
```

### nginx

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/nginx-ai-map.conf \
  -o /etc/nginx/snippets/nginx-ai-map.conf
```

```nginx
include /etc/nginx/snippets/nginx-ai-map.conf;

server {
    if ($ai_crawler) {
        return 403;
    }
}
```

```bash
nginx -t && systemctl reload nginx
```

### Apache

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/apache-ai-setenvif.conf \
  -o /etc/apache2/conf-available/ai-crawlers.conf

a2enconf ai-crawlers
apachectl configtest && systemctl reload apache2
```

### Cloudflare WAF

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/cloudflare-ai-expression.txt
```

Use the expression in a WAF Custom Rule. The output is UA-based and designed for review before deployment.

### iptables

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/iptables-ai.sh \
  -o /usr/local/sbin/update-ai-iptables.sh

chmod +x /usr/local/sbin/update-ai-iptables.sh
/usr/local/sbin/update-ai-iptables.sh
```

The generated script uses `ipset` for set-based matching.

### nftables

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/nftables-ai.nft \
  -o /etc/nftables.d/ai-crawlers.nft

nft -f /etc/nftables.d/ai-crawlers.nft
```

### Caddy

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/caddy-ai-block.caddy \
  -o /etc/caddy/snippets/ai-crawlers.caddy

caddy validate --config /etc/caddy/Caddyfile && systemctl reload caddy
```

### HAProxy

```bash
curl -fsSL https://raw.githubusercontent.com/ipanalytics/AI-Crawler-Blocklist/main/dist/haproxy-ai-acl.cfg \
  -o /etc/haproxy/ai-crawlers.cfg

haproxy -c -f /etc/haproxy/haproxy.cfg && systemctl reload haproxy
```

## Outputs

| Artifact | Purpose |
| --- | --- |
| `dist/ai-ips-verified-v4.txt` | Verified official IPv4 CIDRs |
| `dist/ai-ips-verified-v6.txt` | Verified official IPv6 CIDRs |
| `dist/ai-ips-verified-all.txt` | Combined verified CIDRs |
| `dist/ai-ips-high-confidence-v4.txt` | IPv4 challenge/rate-limit candidates |
| `dist/ai-ips-high-confidence-v6.txt` | IPv6 challenge/rate-limit candidates |
| `dist/ai-user-agents.txt` | Plain AI crawler UA tokens |
| `dist/ai-user-agents-regex.txt` | Escaped UA regex tokens |
| `dist/ai-cn-user-agents-watch.txt` | CN/watch UA list |
| `dist/robots-ai-all-block.txt` | robots.txt rules for AI bots and robots-only tokens |
| `dist/cloudflare-ai-expression.txt` | Cloudflare WAF expression |
| `dist/metadata.json` | Source health and counts |
| `dist/sources-report.md` | Human-readable source report |

<details>
<summary>Platform-specific files</summary>

| Artifact | Platform |
| --- | --- |
| `dist/nginx-ai-map.conf` | nginx |
| `dist/nginx-ai-deny.conf` | nginx |
| `dist/apache-ai-setenvif.conf` | Apache |
| `dist/iptables-ai.sh` | iptables/ipset |
| `dist/nftables-ai.nft` | nftables |
| `dist/pf-ai-table.conf` | pf / pfSense |
| `dist/caddy-ai-block.caddy` | Caddy |
| `dist/haproxy-ai-acl.cfg` | HAProxy |
| `dist/traefik-ai-middleware.yml` | Traefik |

</details>

## Data Format

All generated text files include a header with project name, generation timestamp, source repository, policy, and review note.

`dist/metadata.json` is the operational source of truth for current build state:

```json
{
  "generated_at": "2026-06-17T00:00:00Z",
  "project": "AI-Crawler-Blocklist",
  "policy": "official/operator-published sources only",
  "counts": {
    "verified_ipv4_prefixes": 2261,
    "verified_ipv6_prefixes": 1,
    "user_agent_patterns": 24,
    "robots_tokens": 26
  },
  "failed_sources": []
}
```

Source definitions live in `config/sources.json`. The normalizer adds `confidence`, `enforcement`, `ipPolicy`, and `includeInAiOutputs` at build time.

## Operational Notes

- Use `verified-drop` artifacts for hard IP enforcement.
- Use UA files for application-layer controls where IP ranges are unavailable.
- Use watch lists for logging, challenge, bot-score adjustment, or rate limiting.
- Treat `Google-Extended` and `Applebot-Extended` as robots.txt controls.
- Review `dist/metadata.json` and `dist/sources-report.md` before rolling changes into production.

## Project Scope

The project covers AI crawlers, AI search bots, assistant fetchers, training/indexing bots, and AI-adjacent archive sources such as CCBot. Generic search crawlers, SEO tools, uptime probes, ad verification crawlers, social preview bots, and security scanners are outside the generated AI output set unless explicitly classified by policy.

## Use Cases

- Publisher AI crawling controls.
- WAF rule generation for known AI user agents.
- Verified IP hard-drop lists for official crawler feeds.
- Bot analytics enrichment from access logs.
- Change-controlled distribution of crawler policy into infrastructure automation.

## Limitations

- User-agent strings can be spoofed.
- robots.txt depends on crawler compliance.
- Some assistant fetchers are user-triggered and may affect product visibility.
- Broad cloud or platform ranges belong in observe/challenge workflows, not default hard drop.

## Directory Structure

```text
.
├── config/                 # source definitions, policy, output manifest, schema
├── dist/                   # generated blocklists and platform artifacts
├── docs/                   # operator documentation
├── scripts/                # build, fetch, normalize, validate, render
├── templates/              # Jinja templates for generated configs
├── tests/                  # source policy, parsing, output, workflow tests
└── .github/workflows/      # update, PR validation, daily release
```

## Deployment

The update workflow rebuilds `dist/` every six hours and commits changes when generated artifacts differ. The release workflow publishes a daily release containing the current `dist/` archive plus metadata and source report.

Production deployments should pin to a release tag or mirror `dist/` through internal configuration management. Direct raw URL consumption is suitable for simple hosts and lab environments.

## License

MIT. See [`LICENSE`](./LICENSE).

## Disclaimer

This project provides defensive network and application-layer control data. Operators are responsible for testing enforcement impact in their own environment before blocking traffic.


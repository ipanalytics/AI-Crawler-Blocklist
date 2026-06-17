# Firewalls

Generated firewall files are snippets. Review them before applying to production.

## nginx

Use `dist/nginx-ai-map.conf` for UA blocking and `dist/nginx-ai-deny.conf` for combined map/IP snippets.

## Apache

Use `dist/apache-ai-setenvif.conf` with `SetEnvIfNoCase` to deny AI crawler UAs.

## Cloudflare

Use `dist/cloudflare-ai-expression.txt` in WAF Custom Rules. Cloudflare expressions are UA-based here; IP lists should be reviewed and converted into Cloudflare IP lists where appropriate.

## iptables

Use `dist/iptables-ai.sh`. The script uses `ipset` sets for IPv4 and IPv6 instead of thousands of raw rules.

## nftables

Use `dist/nftables-ai.nft`. The generated file uses interval sets.

## pf / pfSense

Use `dist/pf-ai-table.conf` as a table include and adapt interface policy locally.

## Caddy

Use `dist/caddy-ai-block.caddy` as a reusable snippet.

## HAProxy

Use `dist/haproxy-ai-acl.cfg` with your frontend/backend rules.

## Traefik

Use `dist/traefik-ai-middleware.yml` as a starting point for middleware integration.


# Source Policy

AI-Crawler-Blocklist uses only official/operator-published source URLs. Aggregator repositories and third-party blocklist mirrors are rejected as source of truth.

## Enforcement Classes

- `verified-drop`: official crawler-specific machine-readable IP/CIDR feeds.
- `high-confidence`: official or verified signals suitable for challenge or rate-limit.
- `ua-only`: documented user-agent without verified IP ranges.
- `robots-only`: tokens such as `Google-Extended` and `Applebot-Extended`.
- `static-watch`: weak, broad, CN, platform, ASN, or cloud-hosting signals for observe/challenge only.

## Confidence

- `100`: official JSON/text/embedded JSON CIDR feed.
- `90`: official static CIDR from operator documentation.
- `70`: verified reverse DNS plus documented UA.
- `50`: documented UA only.
- `40`: observed/static watch signal without crawler-specific IP feed.
- `<40`: log-only.

## AI-Only Scope

Generic search, SEO, monitoring, social preview, analytics, ad-verification, and security-scanner sources are excluded unless explicitly classified as AI-use.


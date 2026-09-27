# Verifying a crawler beyond its IP address

An IP range answers "which network is this", not "who is this". Every layer below is separately forgeable, so this page records what each signal is worth and in which order to check them.

## 1. What an IP range proves

An operator-published CIDR feed (the `verified-drop` class in this repository) proves that a request came from address space the operator announces for its crawlers. It does not prove which product sent it: several feeds are shared address space, and `config/sources.json` marks those cases in `note`.

Shared-space examples recorded in this repository:

- `common-crawlers.json` covers Googlebot, Googlebot-Image/News/Video, GoogleOther, Storebot-Google **and** Google-CloudVertexBot. Blocking it removes Google Search too — which is why Google-CloudVertexBot has no entry in `config/sources.json`: an operator-published feed exists, but no *crawler-specific* one, and the verified-drop class in this repository is defined as crawler-specific feeds. The caveat is recorded on the `google-extended` entry, which is the correct control for that crawler.
- Three Google files together hold the user-triggered fetcher space: `user-triggered-fetchers.json`, `user-triggered-fetchers-google.json`, `user-triggered-agents.json`.
- The Applebot-Extended and Google-Extended tokens are robots.txt controls, not address ranges: no IP list exists for them.

## 2. Reverse DNS, then ASN

Operator documentation gives the reverse-DNS masks as well as the ranges. For Google's user-triggered fetchers they are:

- `***-***-***-***.gae.googleusercontent.com` for Google-owned fetchers,
- `google-proxy-***-***-***-***.google.com` for user-owned proxies.

Forward-confirmed reverse DNS is the minimum check before treating a request as an operator crawler. An ASN-only rule is not verification: Claude-related traffic has long been attributed to large cloud footprints, so an ASN block produces collateral damage before it produces a block.

## 3. Spoofing is the normal case, not the exception

GreyNoise documented threat actors announcing themselves as OpenAI, Anthropic and DeepSeek crawlers while hunting credentials; the same report lists `216.73.216.0/22` (Perplexity) as a range that should not raise alerts on its own.

Two consequences for enforcement:

- A User-Agent claim that fails verification gets a challenge or a `403`, never the benefit of the doubt.
- Log the path, not just the agent string. The spoofing campaigns target credential and configuration paths, which is also how a false positive is distinguished from an attack.

## 4. Cryptographic identity: Web Bot Auth

- `draft-ietf-webbotauth-httpsig-protocol-00` was published on 1 September 2026 on the standards track, built on RFC 9421 (HTTP Message Signatures) with Ed25519 keys.
- A signing agent publishes its public keys at `/.well-known/http-message-signatures-directory` and signs the request itself; verification rebuilds the signed material from the received request, so the identity is the key directory, not the User-Agent header.
- Signing agents already include Claude, ChatGPT, Perplexity and Common Crawl; verification is offered by Cloudflare, AWS WAF, Vercel, Shopify and Akamai.
- Scheduling is honest to report: the drafts have slipped and the BCP is still stuck inside the working group. Treat signature verification as an edge feature you enable, not something to implement yourself today.

## 5. Declaration layer: Content Signals

`Content-Signal` inside robots.txt (`contentsignals.org`, aligned with the IETF AI Preferences work) states what may be done with a page *after* it was fetched: `search=`, `ai-input=`, `ai-train=`, and Cloudflare's `use=`. It is not access control, and Google has stated it does not act on it for its own crawlers — it is a statement of terms, useful for the legal record and for the crons and validators that read it.

Cloudflare's controls live separately from it: since 15 September 2026 crawling is split into three independent switches (search, AI training, AI agents), "Managed robots.txt" is replaced by "Bot Preference Sync", and operators are classified as Accountable against published criteria.

## 6. When the answer is a price, not a block

RSL (Really Simple Licensing) and HTTP 402 pay-per-crawl sit above the declaration layer: they assume the fetch happens and attach terms to it. They do not replace a block when the block is what the operator wants.

## 7. Order of checks before an enforcement action

1. Is the source in this repository's `verified-drop` class, and is the range marked as shared address space in its `note`?
2. Does forward-confirmed reverse DNS match the operator's published mask?
3. Is the request signed, and does it verify against the key directory (if the edge supports it)?
4. Is the path one the crawler has any business requesting — or a configuration/credential path that belongs to a spoofing campaign?
5. Only then choose the action: allow, challenge, rate-limit, `403`/`402`, or block.

Anything that fails steps 1–3 and lands on step 4 is a spoof: answer it with a challenge or a `403` and keep it out of the "verified operator crawler" statistics that this repository's feeds are built to describe.

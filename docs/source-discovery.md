# Source Discovery

This project accepts only official/operator-published sources. Third-party aggregator blocklist repositories are rejected as source of truth.

## Accepted official AI sources

| Operator | Accepted sources | Notes |
| --- | --- | --- |
| OpenAI | `https://openai.com/gptbot.json`, `https://openai.com/searchbot.json`, `https://openai.com/chatgpt-user.json`, OpenAI crawler docs | GPTBot, OAI-SearchBot, ChatGPT-User have published IP feeds. OAI-AdsBot is documented UA-only. |
| Anthropic | `https://claude.com/crawling/bots.json`, Anthropic ClaudeBot help article | Official JSON feed covers Claude crawlers. |
| Perplexity | `https://www.perplexity.ai/perplexitybot.json`, `https://www.perplexity.ai/perplexity-user.json` | Official JSON feeds for bot and user-triggered fetcher. |
| Mistral AI | `https://mistral.ai/mistralai-user-ips.json` | Official user-triggered fetcher feed from upstream source list. |
| Amazon | `https://developer.amazon.com/amazonbot/ip-addresses`, `https://developer.amazon.com/amazonbot/searchbot-ip-addresses`, `https://developer.amazon.com/amazonbot/live-ip-addresses` | Amazon publishes embedded JSON pages for Amazonbot, Amzn-SearchBot, and Amzn-User. |
| Common Crawl | `https://index.commoncrawl.org/ccbot.json` | Official CCBot JSON feed; AI-adjacent archive/training dataset source. |
| DuckDuckGo | `https://duckduckgo.com/duckassistbot.json` | DuckAssistBot official feed. |
| Google | Google crawler docs | `Google-Extended` is robots-only and is not an IP/firewall drop source. |
| Apple | Applebot support docs | `Applebot-Extended` is robots-only and does not crawl pages. Applebot CIDRs are not default AI hard-drop. |
| Meta | Meta crawler docs | UA/watch only; static platform ranges are not verified crawler-specific AI hard-drop. |
| ByteDance | Toutiao webmaster docs | Bytespider is documented UA/watch; no verified official crawler-specific IP feed is used. |
| Baidu/Petal | Baidu and Petal webmaster docs | CN watch/challenge only unless official crawler-specific AI ranges are later published. |

## Rejected or excluded source classes

- Generic search crawlers such as Googlebot/Bingbot are excluded from AI outputs.
- SEO, monitoring, social preview, analytics, ad-verification, and security-scanner sources are excluded unless explicitly classified as AI-use.
- Aggregator hosts such as `github.com`, `raw.githubusercontent.com`, `gitlab.com`, `firebog.net`, and other blocklist mirrors are rejected as source URLs.


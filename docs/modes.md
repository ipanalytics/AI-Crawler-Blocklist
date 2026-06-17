# Modes

## Strict

Use strict mode when maximum AI blocking matters more than assistant/search visibility.

- verified IP drop
- UA block
- robots all block
- challenge watchlists

## Balanced

Use balanced mode for normal publishers.

- robots all block
- UA block for known AI crawlers
- verified IP block only for high-confidence training/indexing bots
- no Googlebot/Bingbot hard block

## Observe

Use observe mode before enforcement.

- log AI user agents
- log verified IP hits
- inspect false positives
- do not block yet


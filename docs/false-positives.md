# False Positives

Hard blocking can affect visibility, previews, assistant answers, user-requested fetches, or partner workflows.

## Common Cases

- Assistant fetchers can be initiated by a real user.
- AI search bots can affect whether a site appears in generated search answers.
- UA strings can be spoofed.
- Platform IP ranges can be broader than one crawler.
- CN/search watch entries are not verified AI drop signals.

## Response

1. Start in observe mode.
2. Compare hits against `dist/metadata.json`.
3. Prefer challenge/rate-limit for watch lists.
4. Use verified IP hard drop only for `verified-drop` sources.
5. Report source mistakes with official operator documentation.


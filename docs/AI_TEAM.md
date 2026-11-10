# Zero-billing AI team integration

ChatGPT remains the user-facing coordinator in the ChatGPT conversation; GitHub Actions does not call the ChatGPT product or Claude's consumer chat UI.

## Supported free-only routes
- OpenRouter: `OPENROUTER_API_KEY`, `OPENROUTER_FREE_MODEL`. Only IDs ending in `:free` or `openrouter/free` are accepted.
- Optional self-hosted FreeLLMAPI: `FREELLMAPI_BASE_URL`, `FREELLMAPI_API_KEY`, `FREELLMAPI_FREE_MODEL`. Model IDs must be explicitly free. FreeLLMAPI is a router, not hosted inference or a free quota; it requires a reachable HTTPS endpoint and a separately configured free provider.

## Claude Code support
A root `CLAUDE.md` and native skills under `.claude/skills/*/SKILL.md` make project guidance discoverable in Claude Code. This is repository-level workflow support, not a Claude API connection. A Claude API key/route is not configured here; a consumer chat plan is not an API credential.

## Zero-billing safeguards
- No paid fallback, paid catalog, subscription, or billing route.
- Provider quotas may be exhausted; skip unavailable free models rather than switching to paid.
- Secrets stay in GitHub Actions Secrets, never source, commits, logs, or chat.
- Gemini is not called unless a verified free route and authorized credential are configured; no Gemini key or route is assumed.

## Team behaviour
Configured free providers may return independent reviews for comparison. Agreement is not evidence; verify factual claims against primary sources. If no free provider is configured or quotas are exhausted, video generation continues without paid fallback and reports the skipped review accurately.

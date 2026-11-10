# Zero-billing AI team integration

The project can ask multiple model providers for independent drafts and reviews.
ChatGPT remains the user-facing coordinator in the ChatGPT conversation; the
GitHub workflow does not claim to call the ChatGPT product or Claude's consumer
chat UI.

## Supported free-only routes

- OpenRouter: `OPENROUTER_API_KEY`, `OPENROUTER_FREE_MODEL`. Only model IDs
  ending in `:free` or the explicit `openrouter/free` router are accepted.
- Optional self-hosted FreeLLMAPI: `FREELLMAPI_BASE_URL`,
  `FREELLMAPI_API_KEY`, and `FREELLMAPI_FREE_MODEL`. The model ID must end
  in `:free` or be `openrouter/free`. The endpoint accepts the OpenAI-compatible
  `/v1/chat/completions` route.

FreeLLMAPI is a router, not a hosted inference allowance. It must already be
running at a reachable HTTPS endpoint and have at least one provider configured
with its own free quota/key. This repository does not launch a persistent
FreeLLMAPI server, does not create provider accounts or keys, and does not
assume that a local phone endpoint is reachable from GitHub Actions. A blank
endpoint/key/model means the integration is simply skipped.

## Zero-billing safeguards

- Groq is deliberately excluded from this workflow until a specific model and
  route can be verified as free. A provider's free account tier does not make
  every model free.
- OpenRouter and FreeLLMAPI model IDs are rejected before sending if they are
  not explicitly marked free.
- There is no paid fallback, paid catalog, subscription, or billing route.
- Provider quotas are controlled by each provider and may change. Free limits
  can be exhausted; in that case the affected model is skipped and no paid
  route is attempted.
- Secrets belong only in GitHub Actions Secrets, never in source files,
  commits, logs, or chat.

## Team behaviour

The `consult_team(system, prompt)` function asks every configured free provider
concurrently and returns separate answers for comparison. The synthesis helper
then asks a responding free provider to reconcile the drafts; if that fails it
returns a clearly identifiable raw draft rather than inventing consensus.
Model agreement is not evidence: factual claims still require primary-source
verification.

The current video script uses the team for an optional peer-review report.
If no free provider is configured or all quotas are exhausted, video generation
continues without paid fallback. Claude's consumer chat plan is not a free API
credential; Claude can only be added if an authorized, explicitly no-cost API
route is available.

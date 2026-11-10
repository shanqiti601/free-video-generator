# Zero-cost AI team integration

The repository can consult multiple model providers for research, script drafts,
and independent reviews. ChatGPT remains the human-facing coordinator in the
ChatGPT conversation; this module does not pretend to call the ChatGPT product
or Claude's consumer chat UI.

## Free providers supported

- Google Gemini API free tier (key: `GEMINI_API_KEY`; model: `gemini-3.8-flash`)
- Groq free API tier (key: `GROQ_API_KEY`)
- OpenRouter free models (key: `OPENROUTER_API_KEY`)

Only the configured providers are called. The current integration intentionally excludes Groq GPT-OSS 120B because Groq's published developer pricing lists it as paid; do not treat a model as free merely because the API has a free developer allowance. OpenRouter is hard-restricted to
`:free` model IDs; a non-free model is rejected before any request. There is
no paid fallback and no billing key is needed. Free quotas are provider
controlled and may change.

## Important limitation

Anthropic's Claude chat Free plan does not provide a general free API quota.
Claude can only be added to automated orchestration if the account has an
authorized API allowance; this project deliberately does not send requests to
Anthropic or risk paid usage.

## Activation

Set the free provider keys as environment variables (or repository Actions
secrets for a workflow). Do not commit keys into source files. If no key is
configured, the existing video workflow continues unchanged. Never paste
secrets into public issues or commit history.

The module is `core/model_team.py`. Its `consult_team(system, prompt)`
function asks all configured providers concurrently and returns their separate
answers for the coordinator to compare. The current video script uses it only for an optional peer-review report. If no provider keys are configured or a free quota is exhausted, video generation continues without paid fallback.

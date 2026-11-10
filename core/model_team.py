"""Zero-billing multi-provider LLM helpers.

Only explicitly configured providers are called. OpenRouter and FreeLLMAPI
are restricted to explicitly free model IDs. No automatic paid fallback exists.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    api_key_env: str
    model_env: str
    default_model: str = ""
    free_only_suffix: str | None = None
    free_model_ids: tuple[str, ...] = ()
    base_url_env: str | None = None

    def config(self):
        key = os.getenv(self.api_key_env, "").strip()
        model = os.getenv(self.model_env, "").strip() or self.default_model
        if not key or not model:
            return None
        if self.free_model_ids and model not in self.free_model_ids:
            raise ValueError(f"{self.name} model {model!r} is not on the configured free-only allowlist.")
        if self.free_only_suffix and not (
            model.endswith(self.free_only_suffix) or model == "openrouter/free"
        ):
            raise ValueError(
                f"{self.name} is restricted to explicitly free model IDs "
                f"ending in {self.free_only_suffix!r}; refusing possible paid usage."
            )
        endpoint = self.base_url
        if self.base_url_env:
            base = os.getenv(self.base_url_env, "").strip().rstrip("/")
            if not base:
                return None
            if base.endswith("/v1/chat/completions"):
                endpoint = base
            elif base.endswith("/v1"):
                endpoint = base + "/chat/completions"
            else:
                endpoint = base + "/v1/chat/completions"
        return key, model, endpoint


PROVIDERS = (
    # Keep this exact model ID on the free-tier allowlist; change only after
    # checking Google's current model availability and pricing.
    Provider("Gemini", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
             "GEMINI_API_KEY", "GEMINI_FREE_MODEL", "gemini-3.8-flash",
             free_model_ids=("gemini-3.8-flash",)),
    # OpenRouter's dynamic free router is the only accepted default here.
    Provider("OpenRouter", "https://openrouter.ai/api/v1/chat/completions",
             "OPENROUTER_API_KEY", "OPENROUTER_FREE_MODEL", "openrouter/free",
             free_only_suffix=":free"),
    # Optional self-hosted FreeLLMAPI gateway. The model must be explicitly
    # marked free; the router itself does not provide free inference or keys.
    Provider("FreeLLMAPI", "", "FREELLMAPI_API_KEY", "FREELLMAPI_FREE_MODEL",
             free_only_suffix=":free", base_url_env="FREELLMAPI_BASE_URL"),
)


class ModelTeamError(RuntimeError):
    pass


def _call(provider: Provider, system: str, prompt: str, timeout: int = 45):
    configured = provider.config()
    if not configured:
        raise ModelTeamError(f"{provider.name}: endpoint or API key/model not configured")
    key, model, endpoint = configured
    payload = {
        "model": model,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        answer = data["choices"][0]["message"]["content"]
        if isinstance(answer, list):
            answer = "\n".join(
                part.get("text", "") for part in answer if isinstance(part, dict)
            )
        answer = str(answer).strip()
        if not answer:
            raise ModelTeamError(f"{provider.name}: empty response")
        return {"provider": provider.name, "model": model, "text": answer}
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError) as exc:
        raise ModelTeamError(f"{provider.name}: {exc}") from exc


def available_providers():
    """Return configured provider names without exposing credentials."""
    available = []
    for provider in PROVIDERS:
        try:
            if provider.config():
                available.append(provider.name)
        except ValueError:
            # Invalid non-free model selections are not reported as available.
            continue
    return available


def consult_team(system: str, prompt: str, max_workers: int = 3):
    """Ask every configured free provider concurrently; return successful replies."""
    configured = []
    for provider in PROVIDERS:
        try:
            if provider.config():
                configured.append(provider)
        except ValueError:
            # A non-free model is rejected, never called.
            continue
    if not configured:
        raise ModelTeamError(
            "No free model providers configured. Add Gemini/OpenRouter free keys, "
            "or a FreeLLMAPI endpoint, key, and explicitly free model."
        )
    results, errors = [], []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(configured))) as pool:
        futures = {pool.submit(_call, p, system, prompt): p for p in configured}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append(str(exc))
    if not results:
        raise ModelTeamError("All configured free providers failed: " + "; ".join(errors))
    return sorted(results, key=lambda item: item["provider"])


def synthesize_replies(system: str, replies: list[dict]):
    """Have one responding free provider reconcile already-collected peer drafts."""
    if not replies:
        raise ModelTeamError("No peer drafts were supplied for synthesis.")
    if len(replies) == 1:
        return replies[0]["text"]
    synthesis_prompt = (
        "Compare the independent model drafts below. Resolve disagreements using "
        "only evidence present in the drafts; do not invent facts or sources. "
        "Clearly label unresolved uncertainty. Produce one concise synthesis.\\n\\n"
        + "\\n\\n".join(
            f"### {item['provider']} ({item['model']})\\n{item['text']}"
            for item in replies
        )
    )
    provider_by_name = {p.name: p for p in PROVIDERS}
    for reply in replies:
        try:
            return _call(provider_by_name[reply["provider"]], system, synthesis_prompt)["text"]
        except Exception:
            continue
    return replies[0]["text"]


def synthesize_with_team(system: str, prompt: str):
    """Ask the free-model team, then synthesize their independent drafts."""
    return synthesize_replies(system, consult_team(system, prompt))

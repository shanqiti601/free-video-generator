"""Zero-billing multi-provider LLM helpers.

Only explicitly configured providers are called. OpenRouter is restricted to
model IDs ending in :free. No automatic paid fallback is possible.
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
    default_model: str
    free_only_suffix: str | None = None

    def config(self):
        key = os.getenv(self.api_key_env, "").strip()
        model = os.getenv(self.model_env, self.default_model).strip()
        if not key or not model:
            return None
        if self.free_only_suffix and not (model.endswith(self.free_only_suffix) or model == "openrouter/free"):
            raise ValueError(
                f"{self.name} is restricted to model IDs ending in "
                f"{self.free_only_suffix!r}; refusing possible paid usage."
            )
        return key, model


PROVIDERS = (
    Provider("Gemini", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
             "GEMINI_API_KEY", "GEMINI_FREE_MODEL", "gemini-3.8-flash"),
    Provider("Groq", "https://api.groq.com/openai/v1/chat/completions",
             "GROQ_API_KEY", "GROQ_FREE_MODEL", "openai/gpt-oss-120b"),
    Provider("OpenRouter", "https://openrouter.ai/api/v1/chat/completions",
             "OPENROUTER_API_KEY", "OPENROUTER_FREE_MODEL", "openrouter/free",
             free_only_suffix=":free"),
)


class ModelTeamError(RuntimeError):
    pass


def _call(provider: Provider, system: str, prompt: str, timeout: int = 45):
    configured = provider.config()
    if not configured:
        raise ModelTeamError(f"{provider.name}: no API key configured")
    key, model = configured
    payload = {
        "model": model,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    request = urllib.request.Request(
        provider.base_url,
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
        if provider.config():
            available.append(provider.name)
    return available


def consult_team(system: str, prompt: str, max_workers: int = 3):
    """Ask every configured free provider concurrently; return successful replies."""
    configured = []
    for provider in PROVIDERS:
        try:
            if provider.config():
                configured.append(provider)
        except ValueError:
            # A non-free OpenRouter model is rejected, never called.
            continue
    if not configured:
        raise ModelTeamError(
            "No free model providers configured. Add Gemini, Groq, or "
            "OpenRouter free-model keys as environment secrets."
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


def synthesize_with_team(system: str, prompt: str):
    """Use the first successful free provider as a synthesis fallback."""
    replies = consult_team(system, prompt)
    return replies[0]["text"]

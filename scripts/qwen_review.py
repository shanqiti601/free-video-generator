#!/usr/bin/env python3
"""Optional Qwen quality gate for FACT BITES UNBOXED.

Uses Groq's OpenAI-compatible API to call Qwen 3.8 27B.
No key is stored in the repository. Set GROQ_API_KEY in the environment.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "qwen/qwen3.8-27b"

def image_data(path: Path) -> str:
    mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, help="Narration/script text file")
    parser.add_argument("--frames", nargs="*", default=[], help="Rendered QA frame images")
    parser.add_argument("--output", default="qwen-review.json")
    args = parser.parse_args()

    key = os.environ.get("GROQ_API_KEY")
    if not key:
        print("QWEN_NOT_CONFIGURED: set GROQ_API_KEY as a protected GitHub Actions secret.", file=sys.stderr)
        return 2

    script = Path(args.script).read_text(encoding="utf-8")
    content = [{
        "type": "text",
        "text": (
            "You are the independent quality reviewer for FACT BITES UNBOXED. "
            "Review this short-video episode before release. Check factual clarity, "
            "hook strength, narration-to-visual match, visual quality, portrait framing, "
            "subtitle safe area, legibility, and branding. Be strict. Do not invent "
            "details not visible. Return JSON only with keys: approved (boolean), "
            "score (0-100), factual_issues (array), visual_issues (array), "
            "subtitle_issues (array), fixes (array), summary (string). "
            "Set approved false for any major factual, framing, subtitle, or visual mismatch.\n\n"
            "NARRATION SCRIPT:\n" + script
        )
    }]
    for frame in args.frames[:6]:
        p = Path(frame)
        if p.exists():
            content.append({"type": "text", "text": f"Rendered frame: {p.name}"})
            content.append({"type": "image_url", "image_url": {"url": image_data(p)}})

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.1,
        "max_tokens": 1800,
        "response_format": {"type": "json_object"}
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        review_text = data["choices"][0]["message"]["content"]
        review = json.loads(review_text)
        Path(args.output).write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(review, ensure_ascii=False, indent=2))
        return 0 if review.get("approved") is True else 1
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"QWEN_API_ERROR {exc.code}: {detail}", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"QWEN_REVIEW_ERROR: {exc}", file=sys.stderr)
        return 4

if __name__ == "__main__":
    raise SystemExit(main())

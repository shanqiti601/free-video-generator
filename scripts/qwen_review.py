#!/usr/bin/env python3
"""Optional Qwen 3.8 visual and script review for FACT BITES UNBOXED.

Required environment:
  DASHSCOPE_API_KEY: Alibaba Cloud Model Studio API key
  QWEN_BASE_URL: workspace-specific OpenAI-compatible base URL, ending /compatible-mode/v1
No credentials are stored in this repository.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

MODEL = os.environ.get("QWEN_MODEL", "qwen3.8-max")
BASE_URL = os.environ.get("QWEN_BASE_URL", "").rstrip("/")
API_URL = BASE_URL + "/chat/completions"

def image_data(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True)
    parser.add_argument("--frames", nargs="*", default=[])
    parser.add_argument("--output", default="qwen-review.json")
    args = parser.parse_args()

    key = os.environ.get("DASHSCOPE_API_KEY")
    if not key or not BASE_URL:
        print("QWEN_NOT_CONFIGURED: add DASHSCOPE_API_KEY and QWEN_BASE_URL as GitHub Actions secrets.", file=sys.stderr)
        return 2

    script = Path(args.script).read_text(encoding="utf-8")
    content = [{
        "type": "text",
        "text": (
            "You are the independent release-quality reviewer for FACT BITES UNBOXED. "
            "Review this short-video episode strictly. Check factual accuracy and clarity, "
            "hook strength, narration-to-visual match, genuine 3D visual quality, portrait "
            "framing, subtitle safe area and legibility, and branding. Do not infer unseen "
            "details. Return JSON only with keys: approved (boolean), score (0-100), "
            "factual_issues (array), visual_issues (array), subtitle_issues (array), "
            "fixes (array), summary (string). Set approved=false for any major issue.\n\n"
            "NARRATION SCRIPT:\n" + script
        )
    }]
    for frame in args.frames[:6]:
        p = Path(frame)
        if p.is_file():
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
        with urllib.request.urlopen(req, timeout=150) as response:
            data = json.loads(response.read().decode("utf-8"))
        review = json.loads(data["choices"][0]["message"]["content"])
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

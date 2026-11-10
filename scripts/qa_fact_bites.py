#!/usr/bin/env python3
"""Deterministic technical QA for the Fact Bites final MP4."""
import json
import subprocess
from pathlib import Path

VIDEO = Path("output/Fact-Bites-Short.mp4")
REPORT = Path("output/Video-QA.txt")
CAPTIONS = Path("output/captions.ass")


def run(command):
    return subprocess.run(command, check=True, capture_output=True, text=True)


def main():
    if not VIDEO.is_file() or VIDEO.stat().st_size < 500_000:
        raise SystemExit("FAIL: final MP4 missing or unexpectedly small")
    data = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(VIDEO)]).stdout)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video or not audio:
        raise SystemExit("FAIL: MP4 must contain both video and audio")
    duration = float(data["format"]["duration"])
    fps = video.get("avg_frame_rate", "0/1")
    checks = [
        f"FILE_BYTES={VIDEO.stat().st_size}",
        f"DURATION_SECONDS={duration:.2f}",
        f"RESOLUTION={video.get('width')}x{video.get('height')}",
        f"FPS={fps}",
        f"VIDEO_CODEC={video.get('codec_name')}",
        f"AUDIO_CODEC={audio.get('codec_name')}",
    ]
    if (video.get("width"), video.get("height")) != (1080, 1920):
        raise SystemExit("FAIL: expected full-screen 1080x1920 portrait")
    if video.get("codec_name") != "h264" or audio.get("codec_name") != "aac":
        raise SystemExit("FAIL: expected H.264 video and AAC audio")
    if duration < 30 or fps not in {"30/1", "30000/1001"}:
        raise SystemExit("FAIL: unexpected duration or frame rate")
    if CAPTIONS.exists():
        dialogue = [line.split(",,", 1)[-1].strip() for line in CAPTIONS.read_text(encoding="utf-8").splitlines() if line.startswith("Dialogue:")]
        if any(not text.startswith(("FACT BITES", "FACT BITE")) for text in dialogue):
            raise SystemExit("FAIL: unexpected on-screen copy outside Fact Bites identity/cards")
        checks.append(f"ON_SCREEN_COPY_LINES={len(dialogue)}")
    run(["ffmpeg", "-v", "error", "-i", str(VIDEO), "-f", "null", "-"])
    checks.extend(["FULL_DECODE=PASS", "TECHNICAL_QA=PASS"])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\\n".join(checks) + "\\n", encoding="utf-8")
    print("\\n".join(checks))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create a cinematic Fact Bites documentary short using NOAA public-domain footage."""
import argparse
import asyncio
import importlib.util
import math
import os
import sys
import subprocess
import urllib.request
from pathlib import Path

import edge_tts

# Load this standalone helper by file path. Importing "core.model_team"
# would execute core/__init__.py first, which pulls in the full video app and
# optional dependencies that are not needed by this short-video workflow.
AI_REVIEW_IMPORT_ERROR = ""
try:
    model_team_path = Path(__file__).resolve().parents[1] / "core" / "model_team.py"
    spec = importlib.util.spec_from_file_location("fact_bites_model_team", model_team_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load model team module from {model_team_path}")
    model_team = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model_team
    spec.loader.exec_module(model_team)
    consult_team = model_team.consult_team
    synthesize_replies = model_team.synthesize_replies
    ModelTeamError = model_team.ModelTeamError
except Exception as exc:
    consult_team = None
    synthesize_replies = None
    ModelTeamError = RuntimeError
    AI_REVIEW_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"

W, H, FPS = 1080, 1920, 30
OUT = Path("output")
NOAA_URL = "https://oceanexplorer.noaa.gov/wp-content/uploads/2018/06/greenland-mp4.mp4"
VOICE_CANDIDATES = ["en-GB-RyanNeural", "en-US-ChristopherNeural", "en-GB-ThomasNeural"]

HOOK = "Imagine being born before the first photograph... and still being alive today."
FACT = "Deep beneath the Arctic waves, the Greenland shark moves through darkness. Scientists estimate that some may live for nearly four centuries."
SCIENCE = "In a study published in the journal Science, researchers used radiocarbon dating in the eye lenses of 28 female sharks. The largest was estimated to be about 392 years old — with a wide margin of uncertainty."
TWIST = "And here is the astonishing part: females may not reach sexual maturity until around 156 years of age. A shark could spend more than a century simply growing up."
END = "A living witness to centuries of history... hidden in the coldest depths of the ocean. Follow Fact Bites for discoveries most people never hear about."

def run(cmd):
    subprocess.run(cmd, check=True)

def probe(path, entry="format=duration"):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", entry,
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True, check=True)
    return r.stdout.strip()

def ass_time(seconds):
    cs = max(0, int(round(seconds * 100)))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, c = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{c:02}"

def write_ass(text, seconds, path):
    words = text.split()
    # Short captions in a centered mobile-safe area; explicit wrapping avoids edge overflow.
    chunks = [" ".join(words[i:i+4]) for i in range(0, len(words), 4)]
    rows = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,DejaVu Sans,46,&H00FFFFFF,&H0000C8FF,&H00101A29,&H90000000,1,0,0,0,100,100,0,0,1,3,2,2,110,110,260,1",
        "Style: Brand,DejaVu Sans,58,&H0000D7FF,&H0000D7FF,&H00101A29,&H90000000,1,0,0,0,100,100,1,0,1,3,1,8,90,90,100,1",
        "Style: Intro,DejaVu Sans,62,&H00FFFFFF,&H0000D7FF,&H00101A29,&H90000000,1,0,0,0,100,100,0,0,1,4,2,8,100,100,245,1",
        "Style: EndCard,DejaVu Sans,76,&H00FFFFFF,&H0000D7FF,&H00101A29,&H90000000,1,0,0,0,100,100,1,0,1,4,2,5,90,90,0,1",
        "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 1,0:00:00.00,{ass_time(seconds + 3.0)},Brand,,0,0,0,,FACT BITES",
        f"Dialogue: 2,0:00:00.00,0:00:04.00,Intro,,0,0,0,,THE SHARK THAT CAN LIVE FOR CENTURIES",
        f"Dialogue: 3,{ass_time(seconds + 0.2)},{ass_time(seconds + 3.2)},EndCard,,0,0,0,,FACT BITES\\NREAL STORIES. EXTRAORDINARY FACTS."
    ]
    total = max(1, len(words)); cursor = 0
    for chunk in chunks:
        n = len(chunk.split())
        start = seconds * cursor / total
        cursor += n
        end = seconds * cursor / total
        parts = chunk.split()
        line1, line2 = [], []
        for word in parts:
            candidate = " ".join(line1 + [word])
            if len(candidate) <= 22 and not line2:
                line1.append(word)
            else:
                line2.append(word)
        caption = " ".join(line1 + ([r"\N"] if line2 else []) + line2)
        rows.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{caption}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")

async def make_voice(text, path):
    last = None
    for voice in VOICE_CANDIDATES:
        try:
            await edge_tts.Communicate(text, voice=voice, rate="-14%", pitch="-10Hz", volume="+0%").save(str(path))
            if path.exists() and path.stat().st_size > 4096:
                print(f"NARRATOR_VOICE={voice}")
                return
        except Exception as exc:
            last = exc
            print(f"Voice {voice} unavailable: {exc}")
    raise RuntimeError(f"No documentary narration voice was generated: {last}")

def download_footage(path):
    req = urllib.request.Request(NOAA_URL, headers={"User-Agent": "FactBites/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response, path.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    if path.stat().st_size < 500_000:
        raise RuntimeError("NOAA footage download was unexpectedly small.")
    print(f"NOAA_FOOTAGE_BYTES={path.stat().st_size}")

def optional_ai_review(narration):
    """Ask configured free models for an independent pre-production review."""
    if os.getenv("FACT_BITES_AI_REVIEW", "1").strip().lower() not in {"1", "true", "yes"}:
        print("AI_REVIEW=disabled")
        return
    if consult_team is None:
        report = OUT / "AI-Peer-Review.txt"
        report.write_text(
            f"AI review module could not be loaded: {AI_REVIEW_IMPORT_ERROR}\n",
            encoding="utf-8",
        )
        print(f"AI_REVIEW=unavailable ({AI_REVIEW_IMPORT_ERROR})")
        print(f"AI_REVIEW_REPORT={report}")
        return
    system = (
        "You are a strict documentary fact-check and short-form video editor. "
        "Review the supplied narration only. Do not invent sources or facts. "
        "Flag unsupported or uncertain claims, misleading certainty, pacing "
        "problems, and subtitle overflow risk. Return concise bullet points. "
        "Do not rewrite or silently approve factual claims."
    )
    try:
        reviews = consult_team(system, narration)
        report = OUT / "AI-Peer-Review.txt"
        report.write_text(
            "\n\n".join(
                f"--- {item['provider']} ({item['model']}) ---\n{item['text']}"
                for item in reviews
            ) + "\n",
            encoding="utf-8",
        )
        print(f"AI_REVIEW=completed ({len(reviews)} free model responses)")
        print(f"AI_REVIEW_REPORT={report}")
        if synthesize_replies is not None and len(reviews) > 1:
            synthesis = synthesize_replies(system, reviews)
            synthesis_path = OUT / "AI-Team-Synthesis.txt"
            synthesis_path.write_text(synthesis + "\n", encoding="utf-8")
            print(f"AI_TEAM_SYNTHESIS={synthesis_path}")
    except Exception as exc:
        # The video remains buildable when no free provider key is configured
        # or a provider is rate-limited; no paid fallback is attempted.
        report = OUT / "AI-Peer-Review.txt"
        report.write_text(
            f"AI peer review was skipped safely: {exc}\n"
            "No paid fallback was attempted.\n",
            encoding="utf-8",
        )
        print(f"AI_REVIEW=skipped ({exc})")
        print(f"AI_REVIEW_REPORT={report}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hook", default=HOOK)
    p.add_argument("--fact", default=FACT)
    p.add_argument("--science", default=SCIENCE)
    p.add_argument("--twist", default=TWIST)
    p.add_argument("--end", default=END)
    a = p.parse_args()
    OUT.mkdir(exist_ok=True)
    narration = " ".join([a.hook, a.fact, a.science, a.twist, a.end])
    optional_ai_review(narration)
    audio = OUT / "narration.mp3"
    asyncio.run(make_voice(narration, audio))
    voice_len = float(probe(audio))
    # Reserve a clean 3.5-second branded end card after narration.
    target = max(48.0, voice_len + 3.5)

    footage = OUT / "noaa_greenland_shark.mp4"
    download_footage(footage)
    source_len = float(probe(footage))
    print(f"SOURCE_FOOTAGE_SECONDS={source_len:.2f}")

    # Build a cinematic vertical sequence from the real NOAA ROV encounter.
    # Alternating crop positions and a gentle push-in keep the frame alive without fake illustrations.
    segment = target / 4
    clips = []
    for i in range(4):
        clip = OUT / f"shot_{i+1}.mp4"
        # Use a slightly different crop center for each shot, with a slow push-in.
        xexpr = ["iw/2-(iw/zoom/2)", "iw*0.46-(iw/zoom/2)", "iw*0.54-(iw/zoom/2)", "iw/2-(iw/zoom/2)"][i]
        # Preserve the complete 16:9 source frame in the 9:16 canvas.
        # A softly blurred, brighter fill replaces black bars; the sharp foreground is never cropped.
        vf = (
            "[0:v]split[bg][fg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
            "crop=1080:1920,boxblur=30:12,eq=brightness=0.10:saturation=1.18[bg];"
            "[fg]scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
            "hqdn3d=1.2:1.2:4:4,eq=contrast=1.05:saturation=1.16:brightness=0.08:gamma=1.08,"
            "unsharp=7:7:0.55:5:5:0.0,setsar=1,format=yuv420p[out]"
        )
        # Skip NOAA's original black title slate so the story opens on actual underwater footage.
        usable = max(1.0, source_len - segment * 0.85 - 12.0)
        start = 12.0 + (i * usable) / 3
        run(["ffmpeg","-y","-loglevel","error","-ss",f"{start:.2f}","-stream_loop","-1","-i",str(footage),
             "-t",f"{segment:.2f}","-filter_complex",vf,"-map","[out]","-an","-c:v","libx264","-preset","medium",
             "-crf","18","-pix_fmt","yuv420p",str(clip)])
        clips.append(clip)

    concat = OUT / "shots.txt"
    concat.write_text("".join(f"file '{x.resolve()}'\n" for x in clips), encoding="utf-8")
    silent = OUT / "documentary_silent.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),
         "-c","copy","-t",f"{target:.2f}",str(silent)])

    captions = OUT / "captions.ass"
    write_ass(narration, voice_len, captions)
    # Original low-level cinematic drone: synthesized locally, no copyrighted music.
    final = OUT / "Fact-Bites-Short.mp4"
    run([
        "ffmpeg","-y","-loglevel","error","-i",str(silent),"-i",str(audio),
        "-f","lavfi","-i",f"anoisesrc=color=pink:sample_rate=48000:duration={target:.2f}",
        "-filter_complex",
        "[2:a]lowpass=f=180,highpass=f=35,volume=0.035,afade=t=in:st=0:d=3,afade=t=out:st="
        f"{max(0,target-4):.2f}:d=4[amb];"
        "[1:a]highpass=f=75,lowpass=f=9000,acompressor=threshold=0.12:ratio=3:attack=20:release=250,"
        "volume=1.25[voice];[voice][amb]amix=inputs=2:duration=longest:weights=1 0.28[a]",
        "-vf",f"subtitles={captions},format=yuv420p",
        "-map","0:v:0","-map","[a]","-t",f"{target:.2f}",
        "-c:v","libx264","-preset","medium","-crf","17","-c:a","aac","-b:a","192k",
        "-movflags","+faststart",str(final)
    ])
    actual = float(probe(final))
    print(f"VIDEO_READY={final}")
    print(f"DURATION_SECONDS={actual:.1f}")
    print(f"RESOLUTION={probe(final, 'stream=width,height').replace(chr(10),'x')}")
    print("FOOTAGE_CREDIT=NOAA Ocean Exploration, Northeast U.S. Canyons Expedition 2013")
    if actual < 30:
        raise RuntimeError("Generated video is shorter than 30 seconds.")

if __name__ == "__main__":
    main()

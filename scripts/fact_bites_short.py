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

HOOK = "This shark may live for centuries — and scientists found its age in its eyes."
FACT = "Radiocarbon dating of eye-lens nuclei from 28 female Greenland sharks suggested a lifespan of at least 272 years."
SCIENCE = "In a study published in Science, researchers examined the eye lenses of 28 Greenland sharks. The largest specimen was estimated to be about 392 years old, with an uncertainty of roughly 120 years — a wide range, not an exact birthday."
TWIST = "The study also estimated that females reach sexual maturity at about 156 years old, with an uncertainty of roughly 22 years. For this shark, growing up can take more than a century."
END = "For the Greenland shark, a century is barely a beginning."

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

def write_ass(seconds, path):
    """Render only the Fact Bites brand and concise fact cards, never full subtitles."""
    rows = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Brand,DejaVu Sans,54,&H0000D7FF,&H0000D7FF,&H00101A29,&H90000000,1,0,0,0,100,100,1,0,1,3,1,8,90,90,105,1",
        "Style: Fact,DejaVu Sans,40,&H0000F2FF,&H0000F2FF,&H00101A29,&HCC071321,1,0,0,0,100,100,1,0,1,3,1,8,92,92,430,1",
        "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 1,0:00:00.00,{ass_time(min(seconds, 3.0))},Brand,,0,0,0,,FACT BITES",
        f"Dialogue: 2,{ass_time(seconds * 0.12)},{ass_time(seconds * 0.25)},Fact,,0,0,0,,FACT BITE 01  •  AT LEAST 272 YEARS",
        f"Dialogue: 2,{ass_time(seconds * 0.39)},{ass_time(seconds * 0.55)},Fact,,0,0,0,,FACT BITE 02  •  392 ± 120 YEARS (EST.)",
        f"Dialogue: 2,{ass_time(seconds * 0.68)},{ass_time(seconds * 0.83)},Fact,,0,0,0,,FACT BITE 03  •  MATURITY: AT LEAST 156 ± 22 YEARS",
    ]
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
        review_prompt = (
            "NARRATION TO REVIEW:\n" + narration +
            "\n\nPRIMARY SOURCE CONTEXT:\n"
            "Nielsen et al. (2016), Science 353(6300), 702–704, DOI 10.1126/science.aaf1703. "
            "The study used radiocarbon dating of eye-lens nuclei from 28 female Greenland sharks. "
            "It reported a lifespan of at least 272 years; the largest specimen (502 cm) was estimated "
            "at 392 ± 120 years; estimated age at sexual maturity was at least 156 ± 22 years "
            "(95.4% probability range). Review whether the narration preserves these details and uncertainty."
        )
        reviews = consult_team(system, review_prompt)
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

    # Three fast, relevant footage cuts make the first five seconds visually immediate.
    intro_durations = [1.6, 1.7, 1.7]
    main_duration = target - sum(intro_durations)
    segment = main_duration / 4
    usable = max(1.0, source_len - segment * 0.85 - 12.0)
    clips = []

    def make_shot(filename, start, duration):
        clip = OUT / filename
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
            "crop=1080:1920:iw-ow:0,hqdn3d=1.0:1.0:3:3,"
            "eq=contrast=1.05:saturation=1.10:brightness=0.14:gamma=1.16:gamma_weight=0.85,"
            "unsharp=5:5:0.45:5:5:0.0,"
            "zoompan=z='min(zoom+0.0007,1.055)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,"
            "setsar=1,format=yuv420p"
        )
        run(["ffmpeg","-y","-loglevel","error","-ss",f"{start:.2f}","-stream_loop","-1","-i",str(footage),
             "-t",f"{duration:.2f}","-vf",vf,"-an","-c:v","libx264","-preset","medium",
             "-crf","18","-pix_fmt","yuv420p",str(clip)])
        clips.append(clip)

    # The NOAA clip's strongest shark encounters occur after the opening slate.
    # Favor the two encounter windows instead of wasting the hook on empty blue water.
    shark_window_a = 12.0 + usable / 3
    shark_window_b = 12.0 + usable
    def safe_start(preferred, duration):
        latest = max(12.0, source_len - duration - 0.2)
        return max(12.0, min(preferred, latest))

    hook_positions = [
        safe_start(shark_window_a, intro_durations[0]),
        safe_start(shark_window_a + 4.0, intro_durations[1]),
        safe_start(shark_window_b - 2.0, intro_durations[2]),
    ]
    for i, duration in enumerate(intro_durations):
        make_shot(f"hook_{i+1}.mp4", hook_positions[i], duration)
    story_positions = [
        safe_start(shark_window_a + 8.0, segment),
        safe_start(shark_window_b - 10.0, segment),
        safe_start(shark_window_a + 13.0, segment),
        safe_start(shark_window_b - 4.0, segment),
    ]
    for i, start in enumerate(story_positions):
        make_shot(f"story_{i+1}.mp4", start, segment)

    concat = OUT / "shots.txt"
    concat.write_text("".join(f"file '{x.resolve()}'\n" for x in clips), encoding="utf-8")
    silent = OUT / "documentary_silent.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),
         "-c","copy","-t",f"{target:.2f}",str(silent)])

    # Keep primary research and footage credits with the export for transparent publishing.
    sources = OUT / "Research-Sources.txt"
    sources.write_text(
        "SCIENTIFIC SOURCE\n"
        "Nielsen, J. et al. (2016). Eye lens radiocarbon reveals centuries of longevity in the Greenland shark (Somniosus microcephalus).\n"
        "Science, 353(6300), 702–704. DOI: 10.1126/science.aaf1703\n"
        "https://doi.org/10.1126/science.aaf1703\n\n"
        "FOOTAGE SOURCE AND CREDIT\n"
        "NOAA Ocean Exploration, Greenland Shark — Northeast U.S. Canyons Expedition 2013.\n"
        "https://oceanexplorer.noaa.gov/multimedia/video-playlist-ex1304-greenlandshark/\n"
        "Credit: NOAA Ocean Exploration, Northeast U.S. Canyons Expedition 2013.\n",
        encoding="utf-8",
    )

    # On-screen copy is intentionally limited to FACT BITES branding and fact cards.
    captions = OUT / "captions.ass"
    write_ass(target, captions)
    final = OUT / "Fact-Bites-Short.mp4"
    # Original low-level cinematic drone: synthesized locally, no copyrighted music.
    final = OUT / "Fact-Bites-Short.mp4"
    run([
        "ffmpeg","-y","-loglevel","error","-i",str(silent),"-i",str(audio),
        "-f","lavfi","-i",f"anoisesrc=color=pink:sample_rate=48000:duration={target:.2f}",
        "-filter_complex",
        "[2:a]lowpass=f=180,highpass=f=35,volume=0.035,afade=t=in:st=0:d=3,afade=t=out:st="
        f"{max(0,target-4):.2f}:d=4[amb];"
        "[1:a]highpass=f=75,lowpass=f=9000,acompressor=threshold=0.12:ratio=3:attack=20:release=250,"
        "volume=1.25[voice];[voice][amb]amix=inputs=2:duration=longest:weights=1 0.28,"
        f"afade=t=out:st={max(0,target-1.5):.2f}:d=1.5[a]",
        "-vf",f"subtitles={captions},fade=t=out:st={max(0,target-1.4):.2f}:d=1.4,format=yuv420p",
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

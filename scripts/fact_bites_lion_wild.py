#!/usr/bin/env python3
"""FACT BITES — wild African lion documentary. Commons footage, Edge TTS, Whisper captions, FFmpeg."""
import asyncio, hashlib, json, pathlib, subprocess, urllib.parse, urllib.request
import edge_tts

ROOT = pathlib.Path("output/lion")
ASSETS = ROOT / "assets"
SEGMENTS = ROOT / "segments"
SOCIAL = pathlib.Path("output/social")
for p in (ROOT, ASSETS, SEGMENTS, SOCIAL):
    p.mkdir(parents=True, exist_ok=True)

HORIZONTAL = pathlib.Path("output/FACT-BITES-LION-Wild-Savanna-Documentary.mp4")
VERTICAL = SOCIAL / "FACT-BITES-LION-Instagram-Reel.mp4"
SCRIPT = """At first light on Africa’s open savanna, a lion’s presence can change the rhythm of the entire landscape. But the most remarkable thing about a lion is not its roar. It is the society behind it.

Lions are the only big cats that live in stable social groups, called prides. A pride is usually built around related females and their young. These lionesses often remain in the same family group for life.

When they hunt, lionesses may spread out, using cover and timing to approach from different directions. Cooperation can improve their chances, although a hunt is never guaranteed. Males often form coalitions and help defend the pride’s territory against rivals.

But the balance is always changing. Young males leave, new coalitions challenge, and cubs depend on the group for protection. Across the savanna, survival is not simply strength against strength. It is family, teamwork, and a constant struggle to hold a place in the wild.

This is FACT BITES."""

SOURCES = [
    {
        "title": "File:Lions (Panthera leo) pride ....webm",
        "page": "https://commons.wikimedia.org/wiki/File:Lions_(Panthera_leo)_pride_....webm",
        "credit": "Bernard DUPONT — CC BY-SA 2.0",
        "location": "S25 Road West of Crocodile Bridge, Kruger National Park, South Africa",
        "duration": 40
    },
    {
        "title": "File:Lions (Panthera leo) on the move ....webm",
        "page": "https://commons.wikimedia.org/wiki/File:Lions_(Panthera_leo)_on_the_move_....webm",
        "credit": "Bernard DUPONT — CC BY-SA 2.0",
        "location": "H4-1 Road West of Lower Sabie, Kruger National Park, South Africa",
        "duration": 31
    },
    {
        "title": "File:Lions (Panthera leo).webm",
        "page": "https://commons.wikimedia.org/wiki/File:Lions_(Panthera_leo).webm",
        "credit": "Bernard DUPONT — CC BY-SA 2.0",
        "location": "H1-4 Road North of Satara, Kruger National Park, South Africa",
        "duration": 17
    }
]

def run(args):
    subprocess.run([str(x) for x in args], check=True)

def probe(path):
    return json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        text=True
    ))

def download_commons(item, index):
    params = urllib.parse.urlencode({
        "action": "query", "titles": item["title"], "prop": "imageinfo",
        "iiprop": "url|size|mime", "format": "json"
    })
    req = urllib.request.Request(
        "https://commons.wikimedia.org/w/api.php?" + params,
        headers={"User-Agent": "FactBitesDocumentary/1.0 (wildlife educational video)"}
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        data = json.load(response)
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    if "imageinfo" not in page:
        raise RuntimeError("Wikimedia source unavailable: " + item["title"])
    info = page["imageinfo"][0]
    if not info.get("mime", "").startswith("video/"):
        raise RuntimeError("Source is not a video: " + item["title"])
    target = ASSETS / f"wild_lion_{index:02d}.webm"
    req = urllib.request.Request(
        info["url"], headers={"User-Agent": "Mozilla/5.0 FactBitesDocumentary/1.0"}
    )
    with urllib.request.urlopen(req, timeout=180) as response, target.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
    if target.stat().st_size < 1_000_000:
        raise RuntimeError("Downloaded source is unexpectedly small: " + item["title"])
    meta = probe(target)
    if not any(s.get("codec_type") == "video" for s in meta["streams"]):
        raise RuntimeError("Invalid video source: " + item["title"])
    item["downloaded_bytes"] = target.stat().st_size
    item["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    return target

async def make_voice():
    mp3 = ROOT / "narration.mp3"
    communicate = edge_tts.Communicate(SCRIPT, voice="en-US-ChristopherNeural", rate="-6%", volume="+0%")
    with mp3.open("wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
    if mp3.stat().st_size < 100_000:
        raise RuntimeError("Narration audio was not generated")
    return mp3

def make_endcard(path, width, height, duration):
    run([
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"color=c=0x071426:s={width}x{height}:r=25:d={duration}",
        "-vf",
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "text='FACT BITES':fontcolor=0x00D9FF:fontsize="
        + ("96" if width > height else "76")
        + ":x=(w-text_w)/2:y=(h-text_h)/2",
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", str(path)
    ])

def main():
    clips = []
    hashes = set()
    for i, item in enumerate(SOURCES, 1):
        path = download_commons(item, i)
        if item["sha256"] in hashes:
            raise RuntimeError("Duplicate source footage detected")
        hashes.add(item["sha256"])
        clips.append(path)

    credits = {
        "episode": "FACT BITES — The Lion: Power of the Pride",
        "footage_provenance": "All three video sources are documented at Kruger National Park, South Africa; no captive footage is used.",
        "license": "Creative Commons Attribution-ShareAlike 2.0 Generic (CC BY-SA 2.0)",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "changes": "Clips cropped, colour/size normalised, edited into a documentary, narrated and captioned.",
        "sources": SOURCES
    }
    (ROOT / "video-credits.json").write_text(json.dumps(credits, indent=2), encoding="utf-8")

    voice = asyncio.run(make_voice())
    duration = float(probe(voice)["format"]["duration"])
    available = sum(float(probe(p)["format"]["duration"]) for p in clips)
    if duration > available - 3:
        raise RuntimeError(f"Voiceover ({duration:.1f}s) exceeds unique wild footage ({available:.1f}s)")

    parts = []
    for i, clip in enumerate(clips):
        out = SEGMENTS / f"wild_{i:02d}.mp4"
        run([
            "ffmpeg", "-y", "-i", str(clip), "-an",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=25,format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", str(out)
        ])
        parts.append(out)

    concat = ROOT / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
    picture = ROOT / "unique_wild_footage.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(picture)])

    # Whisper produces real speech-aligned captions; no guessed timings.
    run(["whisper", str(voice), "--model", "tiny.en", "--output_format", "srt",
         "--output_dir", str(ROOT), "--fp16", "False"])
    srt = ROOT / "narration.srt"
    if not srt.exists() or srt.stat().st_size < 100:
        raise RuntimeError("Speech-aligned subtitle file was not generated")
    # Keep the requested conventional filename as well.
    (ROOT / "captions.srt").write_text(srt.read_text(encoding="utf-8"), encoding="utf-8")

    horizontal_main = ROOT / "horizontal_main.mp4"
    h_sub = "subtitles=" + str(srt.resolve()) + ":force_style='FontName=DejaVu Sans,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00071426,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=58'"
    run([
        "ffmpeg", "-y", "-i", str(picture), "-i", str(voice),
        "-vf", h_sub, "-t", str(duration), "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-movflags", "+faststart", str(horizontal_main)
    ])
    h_end = ROOT / "horizontal_endcard.mp4"
    make_endcard(h_end, 1920, 1080, 4)
    h_list = ROOT / "horizontal_concat.txt"
    h_list.write_text(f"file '{horizontal_main.resolve()}'\nfile '{h_end.resolve()}'\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(h_list), "-c", "copy", str(HORIZONTAL)])

    vertical_main = ROOT / "vertical_main.mp4"
    v_sub = "subtitles=" + str(srt.resolve()) + ":force_style='FontName=DejaVu Sans,FontSize=38,PrimaryColour=&H00FFFFFF,OutlineColour=&H00071426,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=300'"
    v_filter = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:14[blur];"
        "[fg]scale=1080:608:force_original_aspect_ratio=decrease[main];"
        "[blur][main]overlay=(W-w)/2:(H-h)/2,subtitles="
        + str(srt.resolve())
        + ":force_style='FontName=DejaVu Sans,FontSize=38,PrimaryColour=&H00FFFFFF,OutlineColour=&H00071426,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=300'[v]"
    )
    run([
        "ffmpeg", "-y", "-i", str(picture), "-i", str(voice),
        "-filter_complex", v_filter, "-t", str(duration),
        "-map", "[v]", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-movflags", "+faststart", str(vertical_main)
    ])
    v_end = ROOT / "vertical_endcard.mp4"
    make_endcard(v_end, 1080, 1920, 4)
    v_list = ROOT / "vertical_concat.txt"
    v_list.write_text(f"file '{vertical_main.resolve()}'\nfile '{v_end.resolve()}'\n", encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(v_list), "-c", "copy", str(VERTICAL)])

    for path, expected in ((HORIZONTAL, (1920, 1080)), (VERTICAL, (1080, 1920))):
        meta = probe(path)
        video = next(s for s in meta["streams"] if s.get("codec_type") == "video")
        assert (video["width"], video["height"]) == expected, (path, video)
        assert any(s.get("codec_type") == "audio" for s in meta["streams"])
        assert 60 < float(meta["format"]["duration"]) < 180
        run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"])
    (ROOT / "FINAL-QA-FFPROBE.json").write_text(json.dumps({
        "horizontal": probe(HORIZONTAL), "vertical": probe(VERTICAL),
        "unique_source_count": len(clips), "source_sha256_unique": len(hashes) == len(clips),
        "caption_file_bytes": srt.stat().st_size
    }, indent=2), encoding="utf-8")
    (ROOT / "Research-Sources.txt").write_text(
        "Lion social structure and ecology:\n"
        "https://www.nationalgeographic.com/animals/mammals/facts/african-lion\n"
        "https://www.smithsonianmag.com/science-nature/lions-are-only-social-cats-180977650/\n\n"
        "All wildlife video credits and license details are in video-credits.json.\n",
        encoding="utf-8"
    )
    print("QA=PASS")
    print("HORIZONTAL=" + str(HORIZONTAL))
    print("VERTICAL=" + str(VERTICAL))
    print("VOICE_SECONDS=" + str(round(duration, 1)))
    print("UNIQUE_WILD_SOURCES=" + str(len(clips)))

if __name__ == "__main__":
    main()

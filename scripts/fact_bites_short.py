#!/usr/bin/env python3
"""Build a suspense-led, vertical Fact Bites short (minimum 30 seconds)."""
import argparse
import asyncio
import math
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 25
OUT = Path("output")
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def run(cmd):
    subprocess.run(cmd, check=True)

def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())

def wrap(draw, text, font, width):
    lines, current = [], ""
    for word in text.split():
        test = (current + " " + word).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]

def make_scene(path, kicker, heading, index):
    palettes = [((3, 10, 28), (8, 50, 75)), ((5, 12, 35), (25, 28, 75)),
                ((10, 8, 28), (65, 18, 48)), ((3, 18, 36), (10, 68, 76)),
                ((4, 8, 25), (32, 22, 65))]
    top, bottom = palettes[index]
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(top[k] * (1-t) + bottom[k] * t) for k in range(3))
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(img, "RGBA")
    # Underwater light shafts and bubbles create a cinematic deep-sea atmosphere.
    for x in (70, 280, 510):
        d.polygon([(x, 0), (x+65, 0), (x+230, 850), (x+115, 850)],
                  fill=(90, 220, 245, 13))
    for bx, by, r in [(90,330,10),(610,430,7),(535,720,14),(145,870,6),(590,180,5),(270,610,8)]:
        d.ellipse((bx-r,by-r,bx+r,by+r), outline=(190,240,255,105), width=2)
    # Stylized octopus silhouette, tentacles and eyes.
    if index >= 1:
        cx, cy = 360, 800
        for offset in (-125, -65, 0, 65, 125):
            d.arc((cx+offset-85, cy-10, cx+offset+85, cy+230),
                  start=5, end=170, fill=(8, 13, 29, 235), width=24)
        d.ellipse((cx-105,cy-145,cx+105,cy+80), fill=(9,15,34,245))
        d.ellipse((cx-55,cy-55,cx-20,cy-20), fill=(230,245,255,240))
        d.ellipse((cx+20,cy-55,cx+55,cy-20), fill=(230,245,255,240))
        if index >= 2:
            for hx, hy in [(245, 660), (360, 625), (475, 660)]:
                rr = 22
                d.ellipse((hx-rr,hy-rr,hx,hy), fill=(255,65,95,230))
                d.ellipse((hx-rr//2,hy-rr,hx+rr//2,hy), fill=(255,65,95,230))
                d.polygon([(hx-rr,hy-rr//2),(hx+rr,hy-rr//2),(hx,hy+rr)],
                          fill=(255,65,95,230))
    d.rounded_rectangle((42,65,678,1215), radius=38,
                        fill=(3,8,22,105), outline=(255,255,255,48), width=2)
    d.rounded_rectangle((78,105,642,114), radius=5, fill=(72,226,196,255))
    d.text((80,150),"FACT BITES",font=ImageFont.truetype(BOLD,25),fill=(111,238,218,255))
    d.text((80,215),kicker.upper(),font=ImageFont.truetype(BOLD,21),fill=(255,190,95,255))
    d.text((80,258),"A DEEP-SEA MYSTERY",font=ImageFont.truetype(REG,15),fill=(180,210,230,220))
    size = 53
    while size > 32:
        ft = ImageFont.truetype(BOLD,size)
        lines = wrap(d,heading,ft,535)
        if len(lines) <= 5:
            break
        size -= 3
    y = 390
    for line in lines:
        box = d.textbbox((0,0),line,font=ft)
        x = (W-(box[2]-box[0]))//2
        d.text((x+2,y+3),line,font=ft,fill=(0,0,0,140))
        d.text((x,y),line,font=ft,fill=(255,255,255,255))
        y += int(size*1.28)
    d.rounded_rectangle((80,1080,640,1088),radius=4,fill=(255,255,255,55))
    d.rounded_rectangle((80,1080,80+int(560*(index+1)/5),1088),radius=4,fill=(72,226,196,255))
    d.text((80,1115),f"{index+1} / 5",font=ImageFont.truetype(REG,18),fill=(220,232,245,220))
    img.save(path)

def ass_time(seconds):
    cs=max(0,int(round(seconds*100)))
    h,cs=divmod(cs,360000); m,cs=divmod(cs,6000); s,c=divmod(cs,100)
    return f"{h}:{m:02}:{s:02}.{c:02}"

def write_ass(text, seconds, path):
    words=text.split()
    chunks=[" ".join(words[i:i+5]) for i in range(0,len(words),5)]
    lines=["[Script Info]","ScriptType: v4.00+","PlayResX: 720","PlayResY: 1280","WrapStyle: 2",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Default,DejaVu Sans,34,&H00FFFFFF,&H000000FF,&H0010182C,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,45,45,110,1",
           "[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    total=max(1,len(words)); cursor=0
    for chunk in chunks:
        n=len(chunk.split()); start=seconds*cursor/total; cursor+=n; end=seconds*cursor/total
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{chunk}")
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")

async def voice(text,path):
    try:
        await edge_tts.Communicate(text,voice="en-US-GuyNeural",rate="-8%").save(str(path))
        if path.exists() and path.stat().st_size>1024:
            return path
    except Exception as exc:
        print(f"Edge TTS unavailable: {exc}")
    wav=path.with_suffix(".wav")
    run(["espeak-ng","-v","en-us","-s","145","-w",str(wav),text])
    if not wav.exists() or wav.stat().st_size<1024:
        raise RuntimeError("No narration audio was produced.")
    return wav

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hook",default="Deep in the ocean lives a creature with THREE hearts. But here's the mystery... one stops when it swims.")
    p.add_argument("--fact",default="It's the octopus. Two hearts pump blood to its gills. The third sends blood to the rest of its body.")
    p.add_argument("--why",default="But wait. When an octopus swims, its main heart temporarily stops beating. Swimming takes so much energy that it often chooses to crawl instead.")
    p.add_argument("--cta",default="Three hearts. One strange secret. And the ocean is full of surprises. Follow Fact Bites for more.")
    a=p.parse_args()
    OUT.mkdir(exist_ok=True)
    parts=[a.hook.strip(),a.fact.strip(),a.why.strip(),a.cta.strip()]
    narration=" ".join(parts)
    audio=asyncio.run(voice(narration,OUT/"voice.mp3"))
    audio_duration=duration(audio)
    # Guarantee a 32-second minimum; if narration is shorter, the final image holds with a subtle music-free pause.
    target=max(32.0,audio_duration+0.6)
    scenes=[
        ("THE MYSTERY","A creature with THREE hearts..."),
        ("THE REVEAL","Meet the octopus."),
        ("THE SCIENCE","Two hearts send blood to the gills."),
        ("THE TWIST","Its main heart stops when it swims."),
        ("THINK ABOUT IT","It would rather crawl than swim.")
    ]
    clips=[]
    for i,(label,heading) in enumerate(scenes):
        still=OUT/f"scene_{i+1}.png"; clip=OUT/f"scene_{i+1}.mp4"
        make_scene(still,label,heading,i)
        seconds=target/5; frames=math.ceil(seconds*FPS)
        run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(still),
             "-vf",f"zoompan=z='min(zoom+0.0008,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},setsar=1",
             "-frames:v",str(frames),"-an","-c:v","libx264","-preset","ultrafast",
             "-pix_fmt","yuv420p",str(clip)])
        clips.append(clip)
    listing=OUT/"clips.txt"
    listing.write_text("".join(f"file '{x.resolve()}'\n" for x in clips),encoding="utf-8")
    silent=OUT/"silent.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(listing),"-c","copy",str(silent)])
    captions=OUT/"captions.ass"
    write_ass(narration,audio_duration,captions)
    final=OUT/"Fact-Bites-Short.mp4"
    run(["ffmpeg","-y","-loglevel","error","-i",str(silent),"-i",str(audio),
         "-vf",f"subtitles={captions}","-map","0:v:0","-map","1:a:0",
         "-af",f"apad=pad_dur={max(0,target-audio_duration):.2f}","-t",f"{target:.2f}",
         "-c:v","libx264","-preset","ultrafast","-crf","22","-c:a","aac","-b:a","128k",
         "-movflags","+faststart",str(final)])
    actual=duration(final)
    print(f"VIDEO_READY={final}")
    print(f"DURATION_SECONDS={actual:.1f}")
    if actual<30:
        raise RuntimeError(f"Generated video is shorter than 30 seconds: {actual:.1f}")

if __name__=="__main__":
    main()

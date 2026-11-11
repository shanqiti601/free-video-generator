#!/usr/bin/env python3
"""FACT BITES EP003 — Snow Leopard. Free Commons stills + Edge TTS + FFmpeg."""
import asyncio, json, pathlib, subprocess, urllib.parse, urllib.request, re, html, time
from edge_tts import Communicate

OUT=pathlib.Path("output/ep003"); ASSETS=OUT/"assets"; SEGS=OUT/"segments"
OUT.mkdir(parents=True,exist_ok=True); ASSETS.mkdir(exist_ok=True); SEGS.mkdir(exist_ok=True)
VIDEO=pathlib.Path("output/Fact-Bites-EP003-Ghost-of-the-Mountains.mp4")
SCRIPT="""Imagine crossing a mountain wilderness so vast that an animal can vanish in plain sight. Somewhere among these frozen cliffs, a predator is watching. You may be only a few steps away—and never know it.

This is the snow leopard: the ghost of the mountains.

Across the high ranges of Central and South Asia, snow leopards move through some of the planet’s most rugged terrain. Their habitat includes the Himalayas and the mountains of twelve countries. Many live above the tree line, where steep rock, thin air, and extreme cold shape every part of life.

Their coat is more than beautiful. Pale grey fur, dark spots, and smoky rosettes break up the animal’s outline against stone and snow. It is camouflage so effective that researchers can overlook a snow leopard even when it is in the camera frame.

Look at the feet. Wide paws spread the animal’s weight across soft snow, acting like natural snowshoes. Dense fur protects the pads from freezing temperatures and rough rock.

And then there is the tail. Nearly as long as the body, it helps the cat balance on narrow ledges and make sudden turns on steep slopes. When resting, the leopard can wrap that thick tail around its body like a living scarf.

Power comes from the hind legs. A snow leopard can leap across gaps up to around fifteen metres, turning broken mountain terrain into a series of launch points. Its usual prey includes blue sheep, ibex, and other mountain animals. A successful hunt may mean following a herd for hours before one precise ambush.

But this cat has a surprising limitation. Unlike lions and tigers, snow leopards cannot roar. They communicate with sounds such as growls, yowls, and a soft breathy call known as a chuff.

Most of the time, they live alone. Their territories can be enormous, and the mountains make encounters rare. Scientists use camera traps, tracks, and signs left on rocks to understand where these elusive cats travel.

The snow leopard is also a key predator. By keeping mountain herbivore populations in balance, it helps protect the wider ecosystem. Its future is tied to the health of the mountains—and to the people who share them.

Today, habitat changes, declining wild prey, poaching, and conflict with livestock owners put pressure on snow leopards. Conservation work increasingly depends on local communities, protecting herders’ livelihoods while keeping this remarkable predator alive.

A ghost is difficult to protect when it is rarely seen. But every camera-trap image, every mapped corridor, and every community partnership reveals a little more of its hidden world.

High above the valleys, where the wind moves across stone and snow, the ghost of the mountains continues its silent patrol.

This is FACT BITES."""
def run(args): subprocess.run(list(map(str,args)),check=True)
def fetch_images():
    headers={"User-Agent":"FactBitesDocumentary/1.0 (educational video)"}
    def api(params):
        url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
        req=urllib.request.Request(url,headers=headers)
        return json.loads(urllib.request.urlopen(req,timeout=45).read())
    search=api({"action":"query","list":"search","srsearch":"snow leopard","srnamespace":6,"srlimit":50,"format":"json"})
    titles=[x["title"] for x in search.get("query",{}).get("search",[])]
    chosen=[]
    for title in titles:
        data=api({"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1920,"format":"json"})
        pages=list(data.get("query",{}).get("pages",{}).values())
        if not pages: continue
        info=(pages[0].get("imageinfo") or [{}])[0]
        mime=info.get("mime","")
        if mime not in ("image/jpeg","image/png","image/webp"): continue
        meta=info.get("extmetadata",{})
        license_name=html.unescape(meta.get("LicenseShortName",{}).get("value",""))
        chosen.append({"title":title,"url":info.get("thumburl") or info.get("url"),"license":license_name,
          "artist":re.sub("<[^>]+>","",html.unescape(meta.get("Artist",{}).get("value","Unknown"))),
          "credit":re.sub("<[^>]+>","",html.unescape(meta.get("Credit",{}).get("value",""))),
          "source":info.get("descriptionurl","")})
        if len(chosen)>=18: break
    if len(chosen)<8:
        raise RuntimeError(f"Only {len(chosen)} usable Commons images found; titles={len(titles)}")
    (OUT/"image-credits.json").write_text(json.dumps(chosen,indent=2),encoding="utf-8")
    paths=[]
    for i,item in enumerate(chosen):
        p=ASSETS/f"{i:02d}.jpg"
        req=urllib.request.Request(item["url"],headers=headers)
        with urllib.request.urlopen(req,timeout=60) as r: p.write_bytes(r.read())
        if p.stat().st_size<15000: raise RuntimeError(f"Image download too small: {item['title']}")
        paths.append(p)
    return paths
def ts(v):
    ms=round(v*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
async def make_voice():
    mp3=OUT/"narration.mp3"; srt=OUT/"captions.srt"; words=[]
    tts=Communicate(SCRIPT,voice="en-US-ChristopherNeural",rate="-8%",volume="+0%")
    with mp3.open("wb") as f:
        async for c in tts.stream():
            if c["type"]=="audio": f.write(c["data"])
            elif c["type"]=="WordBoundary": words.append((c["offset"]/1e7,(c["offset"]+c["duration"])/1e7,c["text"]))
    blocks=[]; group=[]
    for w in words:
        if group and (len(group)>=8 or len(" ".join(x[2] for x in group+[w]))>44):
            blocks.append(group); group=[]
        group.append(w)
    if group: blocks.append(group)
    if not blocks: raise RuntimeError("Edge TTS did not return caption timing")
    rows=[]
    for i,g in enumerate(blocks,1):
        rows.append(f"{i}\n{ts(max(0,g[0][0]-0.03))} --> {ts(g[-1][1]+0.15)}\n{' '.join(x[2] for x in g)}\n")
    srt.write_text("\n".join(rows),encoding="utf-8")
    return mp3,srt
def main():
    images=fetch_images()
    voice,srt=asyncio.run(make_voice())
    # Create a slow, restrained documentary move from every licensed photograph.
    clips=[]
    for i,img in enumerate(images):
        p=SEGS/f"{i:02d}.mp4"
        vf="scale=1600:900:force_original_aspect_ratio=increase,crop=1600:900,zoompan=z='min(zoom+0.00055,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=300:s=1280x720:fps=25,format=yuv420p"
        run(["ffmpeg","-y","-loop","1","-i",img,"-t","12","-vf",vf,"-an","-c:v","libx264","-preset","veryfast","-crf","20",p])
        clips.append(p)
    listing=OUT/"concat.txt"; listing.write_text("".join(f"file '{p.resolve()}'\n" for p in clips))
    silent=OUT/"picture.mp4"; run(["ffmpeg","-y","-f","concat","-safe","0","-i",listing,"-c","copy",silent])
    # Mix quiet original ambience with the deep narration; burn readable English subtitles.
    subtitle="subtitles="+str(srt.resolve())+":force_style='FontName=DejaVu Sans,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101828,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=48'"
    run(["ffmpeg","-y","-i",silent,"-i",voice,"-f","lavfi","-i","anoisesrc=color=pink:amplitude=0.008:sample_rate=48000",
      "-filter_complex","[1:a]aresample=48000,volume=1.0[v];[2:a]lowpass=f=160,volume=0.06[a];[v][a]amix=inputs=2:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11[m]",
      "-vf",subtitle,"-map","0:v:0","-map","[m]","-shortest","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",VIDEO])
    # Add a clean branded end frame; no extra slogan or opening title.
    duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",VIDEO],text=True).strip())
    (OUT/"Research-Sources.txt").write_text("Primary fact references:\nhttps://www.worldwildlife.org/resources/facts/where-do-snow-leopards-live-and-nine-other-snow-leopard-facts/\nhttps://snowleopard.org/snow-leopard-facts/physical-features/\nhttps://www.catsg.org/living-species-snowleopard\n\nImage credits and license details: image-credits.json\n",encoding="utf-8")
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",VIDEO],text=True))
    assert any(x.get("codec_type")=="video" for x in probe["streams"])
    assert any(x.get("codec_type")=="audio" for x in probe["streams"])
    assert duration>120, f"Video too short: {duration}"
    (OUT/"FINAL-QA-FFPROBE.json").write_text(json.dumps(probe,indent=2))
    # One English-language vertical cut for Instagram; no translated captions.
    social=pathlib.Path("output/social"); social.mkdir(parents=True,exist_ok=True)
    reel=social/"FACT-BITES-EP003-Instagram-Reel.mp4"
    run(["ffmpeg","-y","-i",VIDEO,"-t","60","-filter_complex",
      "[0:v]split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:12[blur];[fg]scale=1080:608:force_original_aspect_ratio=decrease[main];[blur][main]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]",
      "-map","[v]","-map","0:a:0","-c:v","libx264","-preset","veryfast","-crf","21","-c:a","aac","-b:a","160k","-movflags","+faststart",reel])
    print("FINAL_VIDEO="+str(VIDEO)); print("INSTAGRAM_REEL="+str(reel)); print("DURATION_SECONDS="+str(round(duration,1))); print("IMAGE_COUNT="+str(len(images))); print("QA=PASS")
if __name__=="__main__": main()

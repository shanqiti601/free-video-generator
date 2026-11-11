#!/usr/bin/env python3
"""Build FACT BITES EP002 from NOAA source footage and free Edge TTS."""
import asyncio, os, subprocess, pathlib, json, textwrap
from edge_tts import Communicate

ROOT=pathlib.Path("output/ep002"); ASSETS=ROOT/"assets"; SEG=ROOT/"segments"
ROOT.mkdir(parents=True,exist_ok=True); ASSETS.mkdir(exist_ok=True); SEG.mkdir(exist_ok=True)
SOURCES={
"C01":"https://oceanexplorer.noaa.gov/wp-content/uploads/2025/09/dive05-coral-polyp.mp4",
"C02":"https://oceanexplorer.noaa.gov/wp-content/uploads/2018/05/sedci-1920x1080-1.mp4",
"C03":"https://archive.oceanexplorer.noaa.gov/okeanos/explorations/ex1711/dailyupdates/media/video/architects/architects-1280x720.mp4",
"C04":"https://oceanexplorer.noaa.gov/wp-content/uploads/2019/11/coral-garden-1280x720-1.mp4",
"C05":"https://archive.oceanexplorer.noaa.gov/okeanos/explorations/ex1711/dailyupdates/media/video/architects/architects-1280x720.mp4",
"C06":"https://oceanexplorer.noaa.gov/wp-content/uploads/2018/05/sedci-1920x1080-1.mp4",
"C07":"https://oceanexplorer.noaa.gov/wp-content/uploads/2019/11/coral-garden-1280x720-1.mp4"
}
def run(args):
    print("+"," ".join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),check=True)
def download():
    import urllib.request, time
    for k,url in SOURCES.items():
        p=ASSETS/(k+".mp4")
        if p.exists() and p.stat().st_size>=100000:
            print(f"Using cached {k}: {p.stat().st_size} bytes",flush=True)
            continue
        print(f"Downloading {k} from {url}",flush=True)
        last_error=None
        for attempt in range(1,4):
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 FACT-BITES documentary research"})
                with urllib.request.urlopen(req,timeout=90) as response, p.open("wb") as out:
                    if response.status != 200:
                        raise RuntimeError(f"HTTP {response.status} for {k}")
                    while True:
                        chunk=response.read(1024*1024)
                        if not chunk: break
                        out.write(chunk)
                if p.stat().st_size<100000:
                    raise RuntimeError(f"{k} download too small: {p.stat().st_size} bytes")
                print(f"Downloaded {k}: {p.stat().st_size} bytes",flush=True)
                last_error=None
                break
            except Exception as exc:
                last_error=exc
                if p.exists(): p.unlink()
                print(f"Attempt {attempt}/3 failed for {k}: {exc}",flush=True)
                if attempt<3: time.sleep(attempt*3)
        if last_error:
            raise RuntimeError(f"NOAA source {k} failed after 3 attempts: {url}") from last_error
def probe_duration(path):
    x=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(path)])
    return float(json.loads(x)["format"]["duration"])
SCRIPT = """Far below the waves, where sunlight never reaches, forests are growing. They are not made of trees. They are built by tiny animals whose stony skeletons rise slowly from the seafloor, creating shelter for an astonishing range of life.

These are deep-sea coral gardens. Unlike the familiar reefs of warm, shallow water, many of these communities thrive in cold darkness. More than half of all known coral species live in deep waters, where temperatures can hover between four and twelve degrees Celsius. Their world is quiet, cold, and often hundreds or thousands of meters beneath the surface.

A coral begins with a small animal called a polyp. It extends delicate tentacles into the current, capturing passing food. Many polyps live together in colonies, building a shared skeleton that can persist long after individual animals are gone. Over generations, these structures can grow into complex habitats.

Some deep-sea corals stand like branches of an ancient tree. Others form delicate fans, whips, or rounded colonies. Their shapes are not decoration. They create surfaces and hiding places in a landscape that might otherwise offer little shelter. Small crustaceans, brittle stars, fish, and other animals gather among the branches.

A coral garden can become an island of life. As the structure grows, it changes the seafloor around it. Currents move differently. Organic particles settle. Animals find places to feed, rest, and reproduce. One organism becomes the foundation for an entire community.

Some corals grow extraordinarily slowly. A colony that looks like a small tree may have been alive for centuries. Certain deep-sea corals are among the longest-lived animals known to science. Their slow growth means that damage can take a very long time to repair. A broken branch may represent decades or even centuries of growth.

Scientists explore these habitats using remotely operated vehicles. From a ship far above, pilots guide cameras and lights across the dark seafloor. Each dive reveals new shapes and unexpected neighbors. A coral that first appears alone may turn out to support a crowded community.

The search can reveal entire reefs where maps once showed only open ocean. In some regions, scientists have discovered long chains of coral mounds and ridges, built over immense periods of time. These formations can stretch across the seafloor, creating a hidden landscape that is easy to miss without careful mapping and exploration.

Not all deep-sea corals look alike. Black corals can form elegant branching structures. Bamboo corals have segmented skeletons that resemble joints along a stem. Stony corals can build substantial mounds. Each form reflects a different way of living in cold water, strong currents, and limited food.

Unlike shallow tropical corals, deep-sea corals do not depend on sunlight-powered algae living in their tissues. Many capture food particles from the water around them. The current becomes their source of nourishment, delivering the tiny organisms and organic material that sustain the colony.

Their world is connected to the ocean above. Food produced near the surface can drift downward, while currents carry nutrients across the seafloor. The animals living in coral branches are part of a wider network of life, linking distant habitats through the movement of water and energy.

Yet these gardens are fragile. Bottom-contact fishing gear, seabed disturbance, and other human activities can break structures that took centuries to grow. Because recovery is slow, protecting the habitat is not simply about saving individual corals. It is about preserving the living architecture that supports an entire community.

Every expedition adds another piece to the story. Scientists map the shape of reefs, identify species, and study the animals that depend on them. New observations help reveal where these habitats exist and why they matter.

In the darkness of the deep ocean, a coral branch can be more than a place to attach. It can become shelter, feeding ground, nursery, and the beginning of a living forest.

These are the ancient forests of the deep. Hidden from the surface, built one small animal at a time, and still waiting to be fully explored.

Every branch holds a record of time: a refuge shaped by currents, darkness, and the lives that gather there. The deep ocean is still full of places we have never seen. And in these hidden forests, discovery is only just beginning. The story of the deep is far from over.

This is FACT BITES."""
def srt_timestamp(seconds):
    ms=round(seconds*1000)
    h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

async def narration():
    p=ROOT/"narration.mp3"
    srt=ROOT/"captions.srt"
    communicate=Communicate(SCRIPT,voice="en-US-ChristopherNeural",rate="-10%",volume="+0%")
    words=[]
    with p.open("wb") as audio:
        async for chunk in communicate.stream():
            if chunk["type"]=="audio":
                audio.write(chunk["data"])
            elif chunk["type"]=="WordBoundary":
                start=chunk["offset"]/10_000_000
                end=(chunk["offset"]+chunk["duration"])/10_000_000
                words.append((start,end,chunk["text"]))
    captions=[]; group=[]
    for word in words:
        candidate=" ".join(x[2] for x in group+[word])
        if group and (len(group)>=8 or len(candidate)> 42):
            captions.append(group); group=[]
        group.append(word)
    if group: captions.append(group)
    blocks=[]
    for i,g in enumerate(captions,1):
        start=max(0,g[0][0]-0.03); end=max(start+0.5,g[-1][1]+0.12)
        line=" ".join(x[2] for x in g)
        blocks.append(f"{i}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{line}\n")
    # Always produce a valid subtitle file, even if the TTS provider omits WordBoundary events.
    if not blocks:
        duration=probe_duration(p)
        tokens=SCRIPT.split()
        groups=[]; current=[]
        for token in tokens:
            candidate=" ".join(current+[token])
            if current and (len(current)>=8 or len(candidate)>42):
                groups.append(current); current=[]
            current.append(token)
        if current: groups.append(current)
        total=sum(len(g) for g in groups) or 1
        elapsed=0.0
        for i,g in enumerate(groups,1):
            start=duration*elapsed/total
            elapsed+=len(g)
            end=duration*elapsed/total
            blocks.append(f"{i}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{' '.join(g)}\n")
    srt.write_text("\n".join(blocks),encoding="utf-8")
    if not srt.is_file() or srt.stat().st_size==0:
        raise RuntimeError("Subtitle file was not created")
    print("SUBTITLE_FILE="+str(srt.resolve())+" SIZE="+str(srt.stat().st_size),flush=True)
    return p,srt
def make_segment(src,start,dur,out,label):
    # Clean cinematic frame: no chapter bars or labels over source footage.
    vf=("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,setsar=1,fps=30,format=yuv420p")
    if label == "FACT BITES":
        vf += ",drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='FACT BITES':fontcolor=white:fontsize=42:x=80:y=70:shadowcolor=black@0.45:shadowx=2:shadowy=2"
    run(["ffmpeg","-y","-ss",str(start),"-i",str(src),"-t",str(dur),"-an","-vf",vf,
         "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",str(out)])
def main():
    download()
    # Source ranges are intentionally conservative; avoid opening title cards on A04/A05.
    plan=[
      ("C02",12,34,"A FOREST WITHOUT TREES"),
      ("C01",8,34,"A WORLD BUILT BY POLYPS"),
      ("C03",10,34,"ARCHITECTS OF THE DEEP"),
      ("C04",12,34,"ANCIENT CORAL GARDENS"),
      ("C05",8,34,"REEFS ACROSS THE SEAFLOOR"),
      ("C07",10,32,"LIFE AMONG THE BRANCHES"),
      ("C03",45,34,"A SLOW-GROWING WORLD"),
      ("C06",12,34,"DISCOVERING HIDDEN REEFS"),
      ("C02",70,34,"FRAGILE LIVING STRUCTURES"),
      ("C02",160,26,"FACT BITES")
    ]
    concat=[]
    for i,(key,start,dur,label) in enumerate(plan):
        src=ASSETS/(key+".mp4")
        if start+dur>probe_duration(src): raise RuntimeError(f"Invalid range {key} {start}+{dur}")
        out=SEG/f"{i:02d}.mp4"; make_segment(src,start,dur,out,label); concat.append(out)
    listing=ROOT/"concat.txt"
    listing.write_text("".join("file '"+str(p.resolve())+"'\n" for p in concat))
    silent=ROOT/"picture.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",listing,"-c","copy",silent])
    voice,captions=asyncio.run(narration())
    # Burn accurately timed English captions into the picture for universal playback.
    final=pathlib.Path("output/Fact-Bites-EP002-The-Ancient-Forests-of-the-Deep.mp4")
    final.parent.mkdir(exist_ok=True)
    dur=probe_duration(silent)
    subtitle_filter="subtitles="+str(captions.resolve())+":force_style='FontName=DejaVu Sans,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=8,MarginV=62'"
    run(["ffmpeg","-y","-i",silent,"-i",voice,"-f","lavfi","-i",
         "anoisesrc=color=pink:amplitude=0.018:sample_rate=48000",
         "-filter_complex",
         "[1:a]aresample=48000,volume=1.0[voice];[2:a]lowpass=f=180,volume=0.10[amb];"
         "[voice][amb]amix=inputs=2:duration=longest:dropout_transition=2, loudnorm=I=-16:TP=-1.5:LRA=11[a]",
         "-vf",subtitle_filter,"-map","0:v:0","-map","[a]","-t",str(dur),
         "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",final])
    report=subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(final)],text=True)
    (ROOT/"FINAL-QA-FFPROBE.json").write_text(report)
    print("FINAL_VIDEO="+str(final),flush=True)
    print("DURATION_SECONDS="+str(round(probe_duration(final),2)),flush=True)
if __name__=="__main__": main()

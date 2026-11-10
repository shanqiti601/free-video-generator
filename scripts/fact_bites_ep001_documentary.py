#!/usr/bin/env python3
"""Build FACT BITES EP001 from NOAA source footage and free Edge TTS."""
import asyncio, os, subprocess, pathlib, json, textwrap
from edge_tts import Communicate

ROOT=pathlib.Path("output/ep001"); ASSETS=ROOT/"assets"; SEG=ROOT/"segments"
ROOT.mkdir(parents=True,exist_ok=True); ASSETS.mkdir(exist_ok=True); SEG.mkdir(exist_ok=True)
SOURCES={
"A01":"https://oceanexplorer.noaa.gov/wp-content/uploads/2013/10/marine-snow-1920x1080-1.mp4",
"A02":"https://oceanexplorer.noaa.gov/wp-content/uploads/2023/07/dive08-fish-1280x720-1.mp4",
"A03":"https://oceanexplorer.noaa.gov/wp-content/uploads/2019/06/0501-hydrothermal-vents-1920x1080-1.mp4",
"A04":"https://oceanexplorer.noaa.gov/wp-content/uploads/2026/10/largest-sponge-ever-found.mp4",
"A05":"https://oceanexplorer.noaa.gov/wp-content/uploads/2023/10/dive08-changingColors-1280x720-1.mp4",
"A07":"https://oceanexplorer.noaa.gov/wp-content/uploads/2018/09/d2-1280x720-2.mp4"}
def run(args):
    print("+"," ".join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),check=True)
def download():
    import urllib.request
    for k,url in SOURCES.items():
        p=ASSETS/(k+".mp4")
        if not p.exists() or p.stat().st_size<100000:
            print("Downloading",k,flush=True)
            urllib.request.urlretrieve(url,p)
def probe_duration(path):
    x=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(path)])
    return float(json.loads(x)["format"]["duration"])
SCRIPT = """Beneath the ocean surface lies a world that sunlight can barely reach. It is a place of immense pressure, cold water, and animals adapted to conditions that would be impossible for us to survive.

As we descend, the blue light fades. In the deep ocean, the familiar colours of the surface disappear, and the seafloor becomes a landscape revealed only when an exploration vehicle sends out its lights.

This is not an empty wilderness. A giant grenadier moves through the darkness, searching for food. Its large eyes are suited to a world where every trace of light matters. Nearby, an octopus changes its appearance against the seafloor. In the deep, camouflage is not decoration. It is survival.

Some of the most remarkable structures are not animals at all. A deep-sea sponge can grow into an enormous habitat, rising from the seabed and providing shelter for other organisms. These communities develop slowly, in a world where food can be scarce and disturbance may last for generations.

Far above, the ocean's surface continues to send material downward. Tiny fragments of organic matter drift through the water like snow. Scientists call it marine snow. It is one of the ways energy reaches animals living far below the sunlit layer.

Yet not all deep-sea ecosystems depend on food falling from above. At hydrothermal vents, seawater circulates through hot rocks beneath the seafloor and returns carrying dissolved chemicals. Microorganisms use chemical energy to build organic matter. This process, called chemosynthesis, supports communities in places where sunlight never arrives.

An exploration vehicle can reveal only a small part of this immense environment. Its cameras move slowly across the seabed, uncovering animals, geological formations, and habitats that may never have been seen before.

Every dive adds another observation. Every image helps scientists ask better questions about how life survives, how these ecosystems connect, and what may put them at risk.

The deep ocean is not a lifeless void. It is a living world, hidden beneath the waves — and we are only beginning to understand it.

This is FACT BITES."""
async def narration():
    p=ROOT/"narration.mp3"
    await Communicate(SCRIPT,voice="en-US-GuyNeural",rate="-8%",volume="+0%").save(str(p))
    return p
def make_segment(src,start,dur,out,label):
    # Fit the source to a cinematic 1080p frame without stretching; restrained label.
    vf=("scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,setsar=1,fps=30,format=yuv420p,"
        "drawbox=x=0:y=0:w=iw:h=150:color=black@0.28:t=fill,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='{label}':"
        "fontcolor=white:fontsize=44:x=90:y=55")
    run(["ffmpeg","-y","-ss",str(start),"-i",str(src),"-t",str(dur),"-an","-vf",vf,
         "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",str(out)])
def main():
    download()
    # Source ranges are intentionally conservative; avoid opening title cards on A04/A05.
    plan=[
      ("A07",35,28,"THE WORLD BELOW SUNLIGHT"),
      ("A02",8,35,"LIFE IN THE DARK"),
      ("A05",8,34,"ADAPTATION AND CAMOUFLAGE"),
      ("A04",18,42,"ANCIENT SEAFLOOR HABITATS"),
      ("A01",0,9,"MARINE SNOW"),
      ("A07",115,34,"EXPLORING THE DEEP"),
      ("A03",8,48,"LIFE AT HYDROTHERMAL VENTS"),
      ("A07",175,32,"A WORLD STILL BEING DISCOVERED"),
      ("A04",70,38,"THE HIDDEN SEAFLOOR"),
      ("A07",220,30,"FACT BITES")
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
    voice=asyncio.run(narration())
    # Generate an original, subtle synthetic low-frequency ambience; no third-party music.
    final=pathlib.Path("output/Fact-Bites-EP001-The-Hidden-World-of-the-Deep-Ocean.mp4")
    final.parent.mkdir(exist_ok=True)
    dur=probe_duration(silent)
    run(["ffmpeg","-y","-i",silent,"-i",voice,"-f","lavfi","-i",
         "anoisesrc=color=pink:amplitude=0.018:sample_rate=48000",
         "-filter_complex",
         "[1:a]aresample=48000,volume=1.0[voice];[2:a]lowpass=f=180,volume=0.10[amb];"
         "[voice][amb]amix=inputs=2:duration=longest:dropout_transition=2, loudnorm=I=-16:TP=-1.5:LRA=11[a]",
         "-map","0:v:0","-map","[a]","-t",str(dur),"-c:v","copy","-c:a","aac","-b:a","192k",
         "-movflags","+faststart",final])
    report=subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(final)],text=True)
    (ROOT/"FINAL-QA-FFPROBE.json").write_text(report)
    print("FINAL_VIDEO="+str(final),flush=True)
    print("DURATION_SECONDS="+str(round(probe_duration(final),2)),flush=True)
if __name__=="__main__": main()

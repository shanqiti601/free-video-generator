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
SCRIPT = """Beneath the ocean surface lies a world that sunlight can barely reach. Here, pressure rises, temperatures can fall close to freezing, and darkness becomes the defining feature of the landscape. Yet this is no empty wilderness. The deep ocean contains habitats, hunters, scavengers, and communities shaped by conditions unlike those on land.

As we descend, sunlight fades from blue to black. Colours disappear, and the seafloor becomes visible only when an exploration vehicle sends out its lights. Every beam reveals a small circle of an enormous environment. Beyond it lies a world still waiting to be observed.

A giant grenadier moves slowly above the seabed. Its body is adapted to life where food may be widely scattered and every meal matters. Large eyes help it detect faint traces of light, while its movements are measured and economical. In the deep sea, survival often depends not on speed, but on patience and the ability to make use of rare opportunities.

Nearby, an octopus changes its appearance against the seafloor. Its skin can shift in colour and texture, helping it blend into a complex background. Camouflage can make the difference between being noticed and remaining hidden. For an animal living among rocks, sediment, and shadow, changing appearance is a remarkable form of protection.

Some of the most striking structures on the deep seabed are built by animals that seem almost motionless. Sponges filter tiny particles from the water, drawing food through channels in their bodies. Some deep-sea sponges grow to extraordinary sizes and may provide shelter for other organisms. A large sponge is more than an individual animal. It can become part of the architecture of a habitat, adding structure to an otherwise open seafloor.

These habitats can be slow to develop. In the deep ocean, many organisms grow slowly, and disturbances may take a long time to recover from. A footprint, a piece of lost equipment, or a change in the environment can affect a place that has remained undisturbed for generations. Exploring these areas carefully helps scientists understand what lives here before it is altered.

Far above, the ocean's surface continues to send material downward. Tiny fragments of dead plankton, mucus, waste, and other organic matter drift through the water column. Scientists call this marine snow. It falls slowly through the darkness, carrying energy from surface ecosystems to animals living far below the sunlit layer. What looks like a gentle snowfall is, in fact, an important food supply for much of the deep ocean.

But not every deep-sea community depends on food falling from above. At hydrothermal vents, seawater seeps into cracks in the ocean crust, is heated by hot rock, and returns carrying dissolved chemicals. When this fluid meets cold seawater, minerals can form dramatic chimney-like structures. The surrounding water may shimmer with heat, while the seafloor hosts communities adapted to this unusual environment.

Here, the foundation of the food web is different. Microorganisms use chemical energy to build organic matter, a process known as chemosynthesis. Instead of relying directly on sunlight, these microbes use energy from chemical reactions. Other organisms can depend on them, creating communities in places where sunlight never arrives. Hydrothermal vents reveal that life can thrive using energy sources beyond the familiar power of the sun.

An exploration vehicle such as NOAA's Deep Discoverer allows scientists to study these remote places without sending people into the crushing pressure. Cameras, lights, and sampling tools are controlled from a ship at the surface. Operators guide the vehicle slowly across the seabed, watching for animals, geological formations, and signs of habitats that may never have been documented before.

Every image adds another piece to the picture. Every sample and observation helps researchers build a better understanding of life under extreme conditions. The more we explore, the clearer it becomes that the deep is not a lifeless void. It is a living world of extraordinary adaptations, fragile habitats, and connections that reach all the way to the surface.

Beneath the waves, most of this world remains unseen. But with every careful dive, its hidden story comes into view.

And the discoveries do not end when a vehicle returns to the surface. Scientists compare observations, map habitats, and revisit locations to understand how these ecosystems change over time. Some questions take years to answer. Others begin with a single image of an unfamiliar animal passing through the lights. Each expedition reminds us how much remains beyond our view, and why careful exploration matters. The deep ocean is connected to the rest of the planet, and protecting it begins with understanding it.

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

import asyncio, math, os, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

W, H, FPS = 720, 1280, 15
OUT = Path("output")
ASSET = OUT / "ant"
ASSET.mkdir(parents=True, exist_ok=True)

NARRATION = [
    "Deep beneath the forest floor, a new ant colony begins with one remarkable insect: the queen.",
    "She lays tiny eggs in a protected chamber. Each egg carries the beginning of a future colony member.",
    "The eggs hatch into soft, hungry larvae. Worker ants feed them, clean them, and keep them safe.",
    "Next, each larva becomes a pupa. Inside, its body transforms into the adult ant.",
    "A new worker emerges. Some workers care for the young, others dig tunnels, gather food, or defend the nest.",
    "Together they build a living society. And when one worker's life ends, the colony continues. Every ant has a role."
]
VOICE = "en-US-GuyNeural"

def font(size, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, size)

def centered(draw, text, y, f, fill, maxw=650):
    words, lines, line = text.split(), [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0,0), test, font=f)[2] <= maxw: line = test
        else: lines.append(line); line = word
    if line: lines.append(line)
    for s in lines:
        box = draw.textbbox((0,0), s, font=f)
        draw.text(((W-(box[2]-box[0]))/2, y), s, font=f, fill=fill, stroke_width=2, stroke_fill=(20,28,34))
        y += f.size + 12
    return y

def ant(draw, x, y, scale=1, color=(62,39,31), legs=True):
    # Three-part ant body, six articulated legs, antennae.
    r = 23*scale
    draw.ellipse((x-45*scale,y-18*scale,x-8*scale,y+19*scale), fill=color)
    draw.ellipse((x-3*scale,y-13*scale,x+22*scale,y+13*scale), fill=color)
    draw.ellipse((x+20*scale,y-27*scale,x+68*scale,y+21*scale), fill=color)
    if legs:
        for dx in (-2, 8, 17):
            sx=x+dx*scale
            draw.line((sx,y+5*scale,sx-23*scale,y+34*scale,sx-32*scale,y+47*scale), fill=color, width=max(2,int(5*scale)))
            draw.line((sx,y-2*scale,sx+8*scale,y-30*scale,sx+23*scale,y-39*scale), fill=color, width=max(2,int(4*scale)))
        draw.line((x+43*scale,y-20*scale,x+50*scale,y-48*scale), fill=color, width=max(2,int(4*scale)))
        draw.line((x+53*scale,y-19*scale,x+70*scale,y-42*scale), fill=color, width=max(2,int(4*scale)))

def egg(draw,x,y,scale=1):
    draw.ellipse((x-15*scale,y-22*scale,x+15*scale,y+22*scale), fill=(255,244,211), outline=(190,161,118), width=2)

def larva(draw,x,y,scale=1):
    draw.arc((x-42*scale,y-30*scale,x+42*scale,y+34*scale), 185, 355, fill=(246,224,177), width=int(26*scale))
    draw.ellipse((x-40*scale,y-4*scale,x+40*scale,y+30*scale), fill=(246,224,177), outline=(179,139,92), width=2)

def pupa(draw,x,y,scale=1):
    draw.ellipse((x-22*scale,y-42*scale,x+22*scale,y+42*scale), fill=(236,218,177), outline=(166,133,91), width=3)
    draw.arc((x-16*scale,y-30*scale,x+16*scale,y+30*scale), 80, 280, fill=(192,161,119), width=2)

def scene(index, t, total):
    # Warm illustrated science-story palette; composition stays clear on a phone.
    im = Image.new("RGB",(W,H),(20,35,48))
    d = ImageDraw.Draw(im)
    # soft sky / soil split
    d.rectangle((0,0,W,440), fill=(39,74,82))
    d.ellipse((-150,-180,880,520), fill=(75,116,104))
    d.rectangle((0,420,W,H), fill=(102,70,49))
    # underground layered soil
    for yy in range(470,H,95):
        d.line((0,yy,W,yy+12), fill=(128,91,62), width=3)
    # nest chamber
    d.rounded_rectangle((65,610,655,1080), radius=110, fill=(65,47,39), outline=(169,119,75), width=7)
    d.rounded_rectangle((90,635,630,1055), radius=95, outline=(108,80,59), width=3)
    # headline
    titles=["A QUEEN'S NEW BEGINNING","THE TINY EGGS","A HUNGRY LARVA","THE GREAT TRANSFORMATION","A WORKER IS BORN","ONE COLONY, MANY ROLES"]
    centered(d,titles[index],75,font(37,True),(255,239,196))
    # small star-like soil specks
    for k in range(22):
        x=(k*97+33)%W; y=500+(k*61)%680
        d.ellipse((x,y,x+4,y+4),fill=(161,119,82))
    # moving activity within nest
    shift=int(12*math.sin(t*2.1))
    if index==0:
        # queen, larger than workers
        ant(d,340+shift,810,2.0,(49,31,27))
        centered(d,"The queen founds the colony",1110,font(22,True),(255,231,184))
    elif index==1:
        for j in range(9):
            egg(d,220+(j%3)*70,770+(j//3)*65,0.85)
        ant(d,480-shift,910,1.0)
        centered(d,"Each egg holds a new beginning",1110,font(22,True),(255,231,184))
    elif index==2:
        for j in range(3):
            larva(d,235+j*120,800+(j%2)*70,1.0)
        ant(d,480+shift,960,0.9)
        centered(d,"Workers feed and protect the larvae",1110,font(21,True),(255,231,184))
    elif index==3:
        for j in range(4):
            pupa(d,220+j*95,820+(j%2)*20,0.9)
        centered(d,"Inside, the adult body takes shape",1110,font(22,True),(255,231,184))
    elif index==4:
        ant(d,350+shift,850,1.45)
        for j in range(3): ant(d,180+j*155,990,0.75,(75,43,31))
        centered(d,"A worker joins the team",1110,font(22,True),(255,231,184))
    else:
        # workers in a living colony around a central queen
        ant(d,350,840,1.65,(49,31,27))
        for x,y,s in [(180,740,.72),(500,730,.72),(190,980,.72),(500,980,.72),(350,1010,.72)]:
            ant(d,x+int(7*math.sin(t*2+x)),y,s,(73,43,31))
        centered(d,"Every ant has a role in the colony",1110,font(21,True),(255,231,184))
    # connecting dotted progress line
    d.rounded_rectangle((95,1190,625,1203), radius=7, fill=(52,39,34))
    d.rounded_rectangle((95,1190,95+530*(index+1)/6,1203), radius=7, fill=(240,187,93))
    d.text((95,1220),"FACT BITES  •  LIFE CYCLES",font=font(18,True),fill=(255,239,196))
    return im

async def make_voice():
    text = " ".join(NARRATION)
    await edge_tts.Communicate(text, VOICE, rate="-3%", pitch="-2Hz").save(str(ASSET/"narration.mp3"))

def probe_duration(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)]).decode().strip())

asyncio.run(make_voice())
audio = ASSET/"narration.mp3"
duration = probe_duration(audio)
scene_len = duration/len(NARRATION)
raw = subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",str(OUT/"ant-silent.mp4")],stdin=subprocess.PIPE)
for i in range(len(NARRATION)):
    frames = max(1,round(scene_len*FPS))
    for n in range(frames):
        frame=scene(i,n/FPS,scene_len)
        raw.stdin.write(frame.tobytes())
raw.stdin.close()
if raw.wait()!=0: raise RuntimeError("FFmpeg animation render failed")
final = OUT/"FACT-BITES-ANT-LIFE-CYCLE.mp4"
subprocess.run(["ffmpeg","-y","-i",str(OUT/"ant-silent.mp4"),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",str(final)],check=True)
(OUT/"ant-silent.mp4").unlink(missing_ok=True)

# Speech-aligned-by-scene caption file, split into readable short lines.
def stamp(s):
    ms=int(round(s*1000)); h=ms//3600000; ms%=3600000; m=ms//60000; ms%=60000; sec=ms//1000; ms%=1000
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"
srt=[]
for i,line in enumerate(NARRATION):
    start=i*scene_len; end=min(duration,(i+1)*scene_len)
    srt += [str(i+1),f"{stamp(start)} --> {stamp(end)}",line,""]
(ASSET/"captions.srt").write_text("\n".join(srt),encoding="utf-8")
print(json.dumps({"video":str(final),"duration_seconds":round(duration,1),"captions":str(ASSET/"captions.srt"),"voice":VOICE}))

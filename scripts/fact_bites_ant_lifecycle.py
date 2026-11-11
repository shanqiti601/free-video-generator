import asyncio, math, subprocess, json, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

W, H, FPS = 720, 1280, 15
OUT = Path("output")
ASSET = OUT / "ant"
ASSET.mkdir(parents=True, exist_ok=True)
NARRATION = [
    "Welcome to the hidden world beneath our feet! This is an ant nest, a busy underground home with rooms and tunnels.",
    "The queen lays tiny, soft eggs in a safe nursery. Worker ants gently carry and care for them. An egg is the first stage of an ant's life.",
    "Soon, an egg hatches into a larva. Look closely: it has no legs yet, and its body has little sections. Worker ants bring it food so it can grow.",
    "When the larva is ready, it becomes a pupa. Some pupae rest inside a silk cocoon, while others are uncovered. Inside, the adult ant's body takes shape.",
    "A young adult ant emerges! An ant has six legs, two antennae, and three main body parts: head, thorax, and abdomen. Ants are insects because they have six legs.",
    "Now the worker joins the team. Some workers care for babies, some explore for food, and others help protect and repair the nest. Each ant helps the colony."
]
VOICE = "en-US-GuyNeural"
random.seed(12)

def font(size, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, size)

def centered(draw, text, y, f, fill, maxw=650):
    words, lines, line = text.split(), [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0,0), test, font=f)[2] <= maxw: line = test
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    for s in lines:
        box = draw.textbbox((0,0), s, font=f)
        draw.text(((W-(box[2]-box[0]))/2, y), s, font=f, fill=fill, stroke_width=2, stroke_fill=(29,24,21))
        y += f.size + 12
    return y

def oval(draw, box, fill, outline=(38,25,20), width=2):
    draw.ellipse(box, fill=fill, outline=outline, width=width)

def shiny(draw,box,base,edge):
    draw.ellipse(box,fill=base,outline=edge,width=2)
    x1,y1,x2,y2=box
    draw.ellipse((x1+(x2-x1)*.16,y1+(y2-y1)*.10,x1+(x2-x1)*.60,y1+(y2-y1)*.34),fill=tuple(min(255,int(c*1.4+20)) for c in base))
def ant(draw,x,y,scale=1,color=(55,31,25),legs=True,queen=False):
    dark=tuple(max(0,c-28) for c in color)
    if legs:
        pairs=[((-8,-4),(-25,-27),(-45,-9)),((-5,2),(-10,26),(8,48)),((2,4),(25,19),(45,38))]
        for side in (-1,1):
            for st,kn,ft in pairs:
                a=(x+st[0]*scale,y+st[1]*scale*side); b=(x+kn[0]*scale,y+kn[1]*scale*side); c=(x+ft[0]*scale,y+ft[1]*scale*side)
                draw.line((a,b,c),fill=dark,width=max(3,int(5*scale)),joint="curve")
                draw.ellipse((b[0]-3*scale,b[1]-3*scale,b[0]+3*scale,b[1]+3*scale),fill=tuple(min(255,v+25) for v in color))
    shiny(draw,(x-72*scale,y-25*scale,x-17*scale,y+27*scale),color,dark)
    shiny(draw,(x-16*scale,y-17*scale,x+20*scale,y+17*scale),tuple(min(255,c+8) for c in color),dark)
    shiny(draw,(x+13*scale,y-27*scale,x+62*scale,y+23*scale),tuple(min(255,c+5) for c in color),dark)
    draw.ellipse((x+45*scale,y-12*scale,x+52*scale,y-5*scale),fill=(245,193,111))
    draw.line((x+39*scale,y-22*scale,x+48*scale,y-45*scale,x+65*scale,y-50*scale),fill=dark,width=max(2,int(3*scale)),joint="curve")
    draw.line((x+29*scale,y-23*scale,x+29*scale,y-47*scale,x+39*scale,y-57*scale),fill=dark,width=max(2,int(3*scale)),joint="curve")
    if queen: draw.arc((x-29*scale,y-25*scale,x+23*scale,y+25*scale),190,350,fill=(222,166,103),width=max(2,int(4*scale)))

def egg(draw,x,y,scale=1):
    # Pearly white, rice-grain shaped egg with a bright highlight.
    shiny(draw,(x-17*scale,y-8*scale,x+17*scale,y+8*scale),(244,235,207),(174,151,119))
    draw.arc((x-12*scale,y-6*scale,x+7*scale,y+3*scale),190,310,fill=(255,255,245),width=2)

def larva(draw,x,y,scale=1):
    # Curled, legless grub with clear body segments and a small head.
    pts=[]
    for i in range(41):
        a=math.pi*(0.08+i/40*1.05)
        pts.append((x+42*scale*math.cos(a),y+29*scale*math.sin(a)))
    draw.line(pts,fill=(185,143,91),width=max(3,int(34*scale)),joint="curve")
    draw.line(pts,fill=(245,222,177),width=max(2,int(27*scale)),joint="curve")
    for i in range(1,7):
        px,py=pts[int(i*5.5)]
        draw.arc((px-8*scale,py-13*scale,px+8*scale,py+13*scale),70,285,fill=(202,171,127),width=max(1,int(2*scale)))
    hx,hy=pts[-1]
    oval(draw,(hx-7*scale,hy-7*scale,hx+7*scale,hy+7*scale),(181,139,99),(120,87,60),1)

def pupa(draw,x,y,scale=1,cocoon=True):
    if cocoon:
        draw.ellipse((x-27*scale,y-43*scale,x+27*scale,y+43*scale),fill=(220,196,151),outline=(151,119,80),width=max(2,int(3*scale)))
        for off in (-13,-5,4,13):
            draw.arc((x-22*scale,y-37*scale+off*scale,x+22*scale,y+37*scale+off*scale),185,350,fill=(183,151,111),width=1)
    else:
        draw.ellipse((x-19*scale,y-37*scale,x+19*scale,y+37*scale),fill=(232,211,169),outline=(155,124,88),width=2)
        draw.line((x-10*scale,y-15*scale,x+10*scale,y+15*scale),fill=(183,148,106),width=2)

def soil_background(im,d):
    d.rectangle((0,0,W,405),fill=(105,190,224)); d.ellipse((535,55,635,155),fill=(255,220,93))
    for x,y in [(90,105),(350,175),(600,235)]:
        d.ellipse((x,y,x+85,y+38),fill=(239,250,250)); d.ellipse((x+20,y-18,x+65,y+35),fill=(239,250,250))
    d.rectangle((0,350,W,410),fill=(83,157,77)); d.rectangle((0,410,W,H),fill=(151,101,59)); d.rectangle((0,410,W,470),fill=(113,77,49))
    for yy in range(470,H,86): d.line((0,yy,W,yy+4),fill=(181,132,79),width=3)
    for _ in range(450):
        x=random.randrange(W); y=random.randrange(465,H); r=random.choice((1,2,3))
        d.ellipse((x-r,y-r,x+r,y+r),fill=random.choice(((205,157,99),(103,69,45),(132,91,56),(224,174,111))))
    for x in range(10,W,27):
        d.line((x,407,x-8,378),fill=(38,119,57),width=5); d.line((x,407,x+8,372),fill=(47,139,64),width=5)
    for x in (115,245,520,660): d.line((x,408,x+5,510),fill=(111,80,40),width=5)
    # branching corridors connect distinct chambers
    paths=[[(355,450),(355,520),(345,580)],[(345,580),(220,625),(180,710)],[(345,580),(500,620),(525,735)],[(345,580),(350,810),(355,955)]]
    for p in paths:
        d.line(p,fill=(213,158,94),width=76,joint="curve"); d.line(p,fill=(49,37,30),width=54,joint="curve")
    # Separate queen room, nursery, food store and waste chamber
    for x1,y1,x2,y2 in [(48,650,278,855),(285,790,650,1115),(425,560,665,760),(430,1060,650,1190)]:
        d.ellipse((x1-8,y1-8,x2+8,y2+8),fill=(213,157,93),outline=(242,194,132),width=5)
        d.ellipse((x1,y1,x2,y2),fill=(49,37,30),outline=(118,79,49),width=5)
        d.arc((x1+5,y1+5,x2-5,y2-5),195,335,fill=(139,96,59),width=5)
    for x in range(75,630,22): d.arc((x,1035,x+30,1070),180,340,fill=(111,82,57),width=2)

def pill(draw, x, y, text, fill=(255,245,207), ink=(48,43,35), f=None):
    f = f or font(17, True)
    box = draw.textbbox((0,0),text,font=f)
    w = box[2]-box[0]+24; h = box[3]-box[1]+18
    draw.rounded_rectangle((x,y,x+w,y+h),radius=14,fill=fill,outline=(255,255,255),width=2)
    draw.text((x+12,y+7),text,font=f,fill=ink)
def scene(index,t,total):
    im=Image.new("RGB",(W,H),(34,48,48)); d=ImageDraw.Draw(im)
    soil_background(im,d)
    titles=["WELCOME TO THE ANT NEST","STAGE 1 • EGG","STAGE 2 • LARVA","STAGE 3 • PUPA","STAGE 4 • ADULT","A TEAM THAT WORKS TOGETHER"]
    centered(d,titles[index],42,font(31,True),(255,255,255))
    shift=int(9*math.sin(t*2.2))
    # Small lesson panel sits above the progress bar and stays clear of the edges.
    if index==0:
        ant(d,355+shift,835,1.8,(68,39,28),queen=True)
        pill(d,38,490,"QUEEN")
        pill(d,485,510,"NEST TUNNELS")
        pill(d,42,1125,"A colony is a family of ants")
    elif index==1:
        for j in range(20):
            egg(d,160+(j%5)*39,805+(j//5)*31,0.72)
        ant(d,485-shift,930,0.9)
        pill(d,125,700,"TINY • PALE • OVAL")
        pill(d,420,1060,"WORKERS CARE FOR EGGS")
    elif index==2:
        for j in range(3):
            larva(d,190+j*145,825+(j%2)*55,1.0)
        ant(d,505+shift,970,0.82)
        pill(d,115,700,"SOFT BODY • NO LEGS")
        pill(d,405,1060,"WORKERS BRING FOOD")
    elif index==3:
        pupa(d,220,845,0.95,True); pupa(d,365,850,0.95,False); pupa(d,510,845,0.95,True)
        pill(d,125,700,"COCOONED")
        pill(d,390,700,"UNCOVERED")
        pill(d,220,1065,"THE ADULT DEVELOPS INSIDE")
    elif index==4:
        ant(d,350+shift,850,1.55,(68,39,28))
        # Clear anatomy callouts
        pill(d,55,610,"ANTENNAE")
        d.line((170,635,420,800),fill=(255,246,203),width=3)
        pill(d,475,760,"HEAD")
        d.line((475,790,390,835),fill=(255,246,203),width=3)
        pill(d,55,940,"THORAX")
        d.line((155,955,335,850),fill=(255,246,203),width=3)
        pill(d,455,1010,"ABDOMEN")
        d.line((455,1020,285,865),fill=(255,246,203),width=3)
        pill(d,220,1090,"COUNT THE 6 LEGS!")
    else:
        ant(d,350,820,1.35,(68,39,28),queen=True)
        for x,y,s in [(175,735,.62),(520,735,.62),(175,975,.62),(520,975,.62),(350,1030,.62)]:
            ant(d,x+int(6*math.sin(t*2+x)),y,s,(83,49,31))
        pill(d,35,540,"NURSE")
        pill(d,520,540,"FOOD FINDER")
        pill(d,40,1110,"BUILD • CARE • PROTECT")
    # Scene-specific learning point in a clean bright strip
    facts=[
        "A nest has tunnels, rooms and a nursery",
        "Eggs are the first stage of an ant's life",
        "Larvae grow when worker ants feed them",
        "Inside the pupa, the adult body develops",
        "Six legs make an ant an insect",
        "Different jobs help one colony survive"
    ]
    d.rounded_rectangle((35,1160,685,1208),radius=18,fill=(255,238,185),outline=(255,255,255),width=2)
    fb=font(18,True); bb=d.textbbox((0,0),facts[index],font=fb)
    d.text(((W-(bb[2]-bb[0]))/2,1174),facts[index],font=fb,fill=(63,48,34))
    d.rounded_rectangle((95,1220,625,1230),radius=6,fill=(54,42,34))
    d.rounded_rectangle((95,1220,95+530*(index+1)/6,1230),radius=6,fill=(255,204,83))
    d.text((95,1240),"FACT BITES  •  LIFE CYCLES",font=font(15,True),fill=(255,245,218))
    return im

async def make_voice():
    await edge_tts.Communicate(" ".join(NARRATION), VOICE, rate="-3%", pitch="-2Hz").save(str(ASSET / "narration.mp3"))

def probe_duration(path):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ]).decode().strip())

asyncio.run(make_voice())
audio = ASSET / "narration.mp3"
if not audio.is_file() or audio.stat().st_size == 0:
    raise RuntimeError("Narration audio was not created")
duration = probe_duration(audio)
scene_len = duration / len(NARRATION)
silent = OUT / "ant-silent.mp4"
raw = subprocess.Popen([
    "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
    "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
    "-pix_fmt", "yuv420p", str(silent)
], stdin=subprocess.PIPE)
try:
    for i in range(len(NARRATION)):
        frame_count = max(1, round(scene_len * FPS))
        for n in range(frame_count):
            raw.stdin.write(scene(i, n / FPS, scene_len).tobytes())
    raw.stdin.close()
    if raw.wait() != 0:
        raise RuntimeError("FFmpeg silent-video render failed")
except Exception:
    if raw.stdin and not raw.stdin.closed:
        raw.stdin.close()
    raw.kill()
    raw.wait()
    raise

final = OUT / "FACT-BITES-ANT-LIFE-CYCLE.mp4"
subprocess.run([
    "ffmpeg", "-y", "-i", str(silent), "-i", str(audio),
    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
    "-c:a", "aac", "-b:a", "160k", "-shortest",
    "-movflags", "+faststart", str(final)
], check=True)
silent.unlink(missing_ok=True)
if not final.is_file() or final.stat().st_size < 100_000:
    raise RuntimeError("Final MP4 is missing or unexpectedly small")

def stamp(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"

srt = []
for i, line in enumerate(NARRATION):
    start = i * scene_len
    end = min(duration, (i + 1) * scene_len)
    srt.extend([str(i + 1), f"{stamp(start)} --> {stamp(end)}", line, ""])
caption_file = ASSET / "captions.srt"
caption_file.write_text("\n".join(srt), encoding="utf-8")
if not caption_file.is_file() or caption_file.stat().st_size < 100:
    raise RuntimeError("Subtitle file was not created correctly")

print(json.dumps({
    "video": str(final),
    "video_bytes": final.stat().st_size,
    "duration_seconds": round(duration, 1),
    "captions": str(caption_file),
    "caption_bytes": caption_file.stat().st_size,
    "voice": VOICE
}))

import asyncio, math, subprocess, json, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

W, H, FPS = 720, 1280, 15
OUT = Path("output")
ASSET = OUT / "ant"
ASSET.mkdir(parents=True, exist_ok=True)
NARRATION = [
    "Deep beneath the forest floor, a new ant colony begins with one remarkable insect: the queen.",
    "She lays tiny, pale eggs in a warm, protected nursery chamber. The eggs are clustered together and cared for by workers.",
    "The eggs hatch into soft, legless larvae. Their bodies are visibly segmented, and worker ants feed them as they grow.",
    "Next, each larva becomes a pupa. Depending on the species, a pupa may be wrapped in a silken cocoon or remain uncovered. Inside, the adult ant develops.",
    "A new worker emerges with six legs, a pair of antennae, and three main body sections: head, thorax, and abdomen.",
    "Workers care for young, maintain tunnels, gather food, and defend the nest. Together, they keep the colony alive."
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

def ant(draw, x, y, scale=1, color=(55,31,25), legs=True, queen=False):
    # Anatomically legible ant: head, narrow petiole, large gaster, six legs on thorax.
    dark = tuple(max(0,c-18) for c in color)
    thorax=(x-7*scale,y-7*scale)
    if legs:
        # Three pairs of jointed legs attached to the thorax.
        for side in (-1,1):
            for i, (ax, knee, foot) in enumerate([
                (-2, ( -23, -22), (-42, -4)),
                ( 0, ( -4,  27), ( 15, 48)),
                ( 5, ( 25,  15), ( 43, 39))
            ]):
                sx=x+ax*scale
                kx=x+knee[0]*scale
                ky=y+knee[1]*scale*side
                fx=x+foot[0]*scale
                fy=y+foot[1]*scale*side
                draw.line((sx,y, kx,ky, fx,fy), fill=dark, width=max(3,int(5*scale)), joint="curve")
                oval(draw,(kx-3*scale,ky-3*scale,kx+3*scale,ky+3*scale),dark,dark,1)
    # abdomen / gaster, petiole, thorax, head
    oval(draw,(x-68*scale,y-21*scale,x-18*scale,y+25*scale),color,dark,max(1,int(2*scale)))
    oval(draw,(x-20*scale,y-7*scale,x-8*scale,y+7*scale),dark,dark,1)
    oval(draw,(x-13*scale,y-15*scale,x+17*scale,y+15*scale),color,dark,max(1,int(2*scale)))
    oval(draw,(x+12*scale,y-24*scale,x+58*scale,y+22*scale),color,dark,max(1,int(2*scale)))
    # eye and mandibles
    oval(draw,(x+42*scale,y-12*scale,x+48*scale,y-6*scale),(245,194,102),(25,18,15),1)
    draw.arc((x+48*scale,y+3*scale,x+65*scale,y+19*scale),190,290,fill=dark,width=max(2,int(3*scale)))
    # two segmented antennae
    draw.line((x+40*scale,y-19*scale,x+48*scale,y-43*scale,x+62*scale,y-48*scale),fill=dark,width=max(2,int(3*scale)),joint="curve")
    draw.line((x+29*scale,y-21*scale,x+30*scale,y-45*scale,x+40*scale,y-55*scale),fill=dark,width=max(2,int(3*scale)),joint="curve")
    if queen:
        # subtle thorax enlargement and wing scars, not a fantasy crown
        draw.arc((x-25*scale,y-22*scale,x+18*scale,y+22*scale),190,350,fill=(205,147,89),width=max(2,int(3*scale)))

def egg(draw,x,y,scale=1):
    # Ant eggs are tiny, pale, rice-grain shaped, not round bird eggs.
    draw.ellipse((x-13*scale,y-6*scale,x+13*scale,y+6*scale),fill=(250,239,207),outline=(190,164,124),width=max(1,int(2*scale)))
    draw.arc((x-8*scale,y-4*scale,x+8*scale,y+4*scale),190,340,fill=(255,252,231),width=1)

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

def soil_background(im, d):
    # Layered soil with granular texture, roots, pebbles and a readable surface line.
    d.rectangle((0,0,W,405),fill=(105,151,133))
    d.ellipse((-170,-230,900,505),fill=(128,169,137))
    d.rectangle((0,390,W,H),fill=(112,76,49))
    d.rectangle((0,390,W,455),fill=(82,62,43))
    for yy in range(455,H,105):
        d.line((0,yy,W,yy+random.randint(-8,8)),fill=(139,98,62),width=3)
    for _ in range(320):
        x=random.randrange(W); y=random.randrange(455,H)
        r=random.choice((1,2,2,3))
        col=random.choice(((151,111,73),(83,57,40),(174,128,81),(96,68,48)))
        d.ellipse((x-r,y-r,x+r,y+r),fill=col)
    # roots descending from the grass line
    for x in (70,175,570,655):
        d.line((x,395,x+random.randint(-20,20),470,x+random.randint(-30,30),540),fill=(74,65,39),width=5,joint="curve")
    # grass tufts
    for x in range(15,W,35):
        d.line((x,398,x-8,378),fill=(49,99,63),width=4)
        d.line((x,398,x+5,374),fill=(55,112,67),width=4)
    # tunnel network, with dark cavity and warm raised edges
    d.line([(355,470),(355,555),(280,610),(280,720)],fill=(155,111,70),width=74,joint="curve")
    d.line([(355,470),(355,555),(280,610),(280,720)],fill=(47,37,31),width=56,joint="curve")
    d.line([(280,720),(280,820),(360,880)],fill=(155,111,70),width=72,joint="curve")
    d.line([(280,720),(280,820),(360,880)],fill=(47,37,31),width=54,joint="curve")
    # large nursery chamber
    d.ellipse((85,635,645,1110),fill=(155,111,70),outline=(187,137,86),width=5)
    d.ellipse((105,655,625,1090),fill=(48,37,31),outline=(91,67,49),width=5)
    # chamber floor bedding
    for x in range(135,600,27):
        d.arc((x,1000,x+35,1040),180,340,fill=(89,67,49),width=2)

def scene(index,t,total):
    im=Image.new("RGB",(W,H),(34,48,48)); d=ImageDraw.Draw(im)
    soil_background(im,d)
    titles=["A QUEEN'S NEW BEGINNING","THE TINY EGGS","A HUNGRY LARVA","THE PUPA STAGE","A WORKER EMERGES","LIFE INSIDE THE COLONY"]
    centered(d,titles[index],55,font(34,True),(255,244,216))
    shift=int(8*math.sin(t*2))
    if index==0:
        ant(d,345+shift,830,2.0,(59,34,27),queen=True)
        centered(d,"A queen begins a new colony",1120,font(21,True),(255,231,187))
    elif index==1:
        for j in range(18):
            egg(d,190+(j%6)*48,800+(j//6)*42,0.85)
        ant(d,485-shift,930,0.95)
        centered(d,"Pale eggs rest together in a nursery",1120,font(20,True),(255,231,187))
    elif index==2:
        for j in range(3):
            larva(d,220+j*135,825+(j%2)*55,1.05)
        ant(d,500+shift,970,0.88)
        centered(d,"Workers feed the growing larvae",1120,font(21,True),(255,231,187))
    elif index==3:
        pupa(d,235,845,1.0,True); pupa(d,365,850,1.0,False); pupa(d,495,845,1.0,True)
        centered(d,"An adult ant develops inside",1120,font(21,True),(255,231,187))
    elif index==4:
        ant(d,350+shift,850,1.5,(59,34,27))
        centered(d,"Six legs. Three body sections. Two antennae.",1120,font(18,True),(255,231,187))
    else:
        ant(d,350,830,1.55,(59,34,27),queen=True)
        for x,y,s in [(175,745,.7),(520,745,.7),(175,985,.7),(520,985,.7),(350,1030,.7)]:
            ant(d,x+int(5*math.sin(t*2+x)),y,s,(75,44,31))
        centered(d,"Every worker helps the colony survive",1120,font(20,True),(255,231,187))
    # clean episode progress bar and restrained brand footer
    d.rounded_rectangle((95,1190,625,1203),radius=7,fill=(39,31,27))
    d.rounded_rectangle((95,1190,95+530*(index+1)/6,1203),radius=7,fill=(240,190,105))
    d.text((95,1220),"FACT BITES  •  LIFE CYCLES",font=font(18,True),fill=(255,239,203))
    return im

async def make_voice():
    await edge_tts.Communicate(" ".join(NARRATION),VOICE,rate="-3%",pitch="-2Hz").save(str(ASSET/"narration.mp3"))

def probe_duration(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)]).decode().strip())

asyncio.run(make_voice())
audio=ASSET/"narration.mp3"; duration=probe_duration(audio); scene_len=duration/len(NARRATION)
raw=subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",str(OUT/"ant-silent.mp4")],stdin=subprocess.PIPE)
for i in range(len(NARRATION)):
    for n in range(max(1,round(scene_len*FPS))):
        raw.stdin.write(scene(i,n/FPS,scene_len).tobytes())
raw.stdin.close()
if raw.wait()!=0: raise RuntimeError("FFmpeg animation render failed")
final=OUT/"FACT-BITES-ANT-LIFE-CYCLE.mp4"
subprocess.run(["ffmpeg","-y","-i",str(OUT/"ant-silent.mp4"),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",str(final)],check=True)
(OUT/"ant-silent.mp4").unlink(missing_ok=True)

def stamp(s):
    ms=int(round(s*1000)); h=ms//3600000; ms%=3600000; m=ms//60000; ms%=60000; sec=ms//1000; ms%=1000
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"
srt=[]
for i,line in enumerate(NARRATION):
    srt += [str(i+1),f"{stamp(i*scene_len)} --> {stamp(min(duration,(i+1)*scene_len))}",line,""]
(ASSET/"captions.srt").write_text("\n".join(srt),encoding="utf-8")
print(json.dumps({"video":str(final),"duration_seconds":round(duration,1),"captions":str(ASSET/"captions.srt"),"voice":VOICE,"visual_revision":"detailed ant anatomy, rice-shaped eggs, segmented larvae, pupae, textured soil layers and visible tunnels"}))

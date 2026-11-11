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
    # Bright educational cutaway: lively surface above a richly detailed underground nest.
    d.rectangle((0,0,W,405),fill=(105,190,224))
    d.ellipse((535,55,635,155),fill=(255,220,93),outline=(255,244,180),width=5)
    # soft clouds
    for x,y in [(90,105),(350,175),(600,235)]:
        d.ellipse((x,y,x+85,y+38),fill=(239,250,250))
        d.ellipse((x+20,y-18,x+65,y+35),fill=(239,250,250))
    # green meadow and layered soil
    d.rectangle((0,350,W,410),fill=(83,157,77))
    d.rectangle((0,410,W,H),fill=(160,111,66))
    d.rectangle((0,410,W,470),fill=(119,83,53))
    for yy in range(470,H,92):
        d.line((0,yy,W,yy+random.randint(-7,7)),fill=(185,137,83),width=3)
    # soil speckles and stones
    for _ in range(440):
        x=random.randrange(W); y=random.randrange(465,H)
        r=random.choice((1,2,2,3,4))
        col=random.choice(((205,157,99),(111,74,47),(132,91,56),(224,174,111)))
        d.ellipse((x-r,y-r,x+r,y+r),fill=col)
    for x,y,r in [(65,570,13),(620,690,18),(95,1030,16),(580,1120,12),(470,520,9)]:
        d.ellipse((x-r,y-r,x+r,y+r),fill=(104,91,77),outline=(75,65,55),width=3)
    # grass blades, flowers and visible roots
    for x in range(10,W,27):
        d.line((x,407,x-8,378),fill=(38,119,57),width=5)
        d.line((x,407,x+8,372),fill=(47,139,64),width=5)
    for x in (115,245,520,660):
        d.line((x,408,x+random.randint(-18,18),510),fill=(111,80,40),width=5)
    for x,y in [(135,350),(555,360),(635,345)]:
        d.line((x,y+20,x,y-10),fill=(42,112,54),width=4)
        for dx,dy,col in [(-10,0,(255,117,145)),(10,0,(255,219,83)),(0,-9,(255,245,214))]:
            d.ellipse((x+dx-7,y+dy-7,x+dx+7,y+dy+7),fill=col)
    # connected tunnels with bright soil rims and dark interior
    paths=[[(355,455),(355,545),(275,610),(275,700)],
           [(275,700),(275,805),(365,875)],
           [(355,545),(470,600),(470,700)]]
    for path in paths:
        d.line(path,fill=(213,158,94),width=78,joint="curve")
        d.line(path,fill=(55,42,34),width=58,joint="curve")
    # roomy nursery chamber and side room
    d.ellipse((75,650,640,1115),fill=(207,151,88),outline=(240,190,123),width=6)
    d.ellipse((94,670,621,1095),fill=(57,43,34),outline=(119,82,53),width=5)
    d.ellipse((430,570,600,760),fill=(205,150,88),outline=(235,185,119),width=5)
    d.ellipse((443,583,587,747),fill=(55,42,34),outline=(115,79,50),width=4)
    for x in range(125,590,24):
        d.arc((x,1010,x+35,1050),180,340,fill=(111,82,57),width=2)

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


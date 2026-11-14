#!/usr/bin/env python3
import asyncio, json, os, re, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path
OUT=Path("output/unboxed"); UA="FACTBITESUNBOXED/1.0 educational video"
TOPICS=[
{"title":"Why a zipper stays closed","query":"zipper close up fastening teeth","hook":"A zipper looks simple. But one tiny slider is doing a surprisingly precise job.","lines":["Inside the slider are two channels shaped to guide the teeth together.","As you pull it, each side is guided into the other, making the teeth interlock.","Pull the slider the opposite way, and the channels separate the teeth again.","Tooth shapes vary by design, but the slider turns one small movement into a long, reliable closure."]},
{"title":"How a ballpoint pen controls ink","query":"ballpoint pen writing close up","hook":"This tiny metal ball is why a pen can carry ink without spilling it everywhere.","lines":["A ballpoint pen stores thick ink in a narrow reservoir.","At the tip, a tiny ball sits in a socket with just enough room to rotate.","As it rolls across paper, it picks up ink from inside and transfers a thin film onto the page.","The close fit helps control the flow, moving ink onto paper instead of letting the reservoir pour out."]},
{"title":"Why a microwave door has a metal mesh","query":"microwave oven door mesh close up","hook":"That tiny grid in a microwave door helps keep microwave energy inside.","lines":["The holes in the metal mesh are much smaller than the microwave's operating wavelength.","The conductive mesh reflects most microwave energy back into the oven cavity.","Visible light has a far shorter wavelength, so it passes through the holes and lets you see your food.","The door, mesh, seals and safety interlocks work together. Never operate a microwave with a damaged door."]},
{"title":"Why a tape measure blade curves","query":"retractable tape measure extended close up","hook":"A tape measure can stretch out several feet without folding. The secret is its curved blade.","lines":["The blade has a shallow curve across its width, making it stiffer than a flat strip.","That cross-section resists bending under its own weight, so the tape can extend outward for a while.","Push it back toward the case and the blade can flex into a tight coil.","Stand-out distance depends on blade width, thickness and design, but the curve gives the strip much of its strength."]},
{"title":"How a pop-up toaster stops","query":"pop up toaster bread toaster heating","hook":"A toaster can pop your bread up automatically. But what releases the latch?","lines":["In many traditional pop-up toasters, a timing circuit or thermal control determines when heating ends.","An electromagnet holds the bread carriage down during the heating cycle.","When the cycle ends, power to the magnet is cut, the latch releases, and a spring lifts the toast.","Models vary, but the pop-up action combines a latch, a spring and automatic control."]}
]
def run(c): subprocess.run(c,check=True)
def api(url):
 r=urllib.request.Request(url,headers={"User-Agent":UA})
 with urllib.request.urlopen(r,timeout=40) as x:return json.loads(x.read())
def candidates(q):
 p={"action":"query","format":"json","generator":"search","gsrnamespace":6,"gsrsearch":"filetype:video "+q,"gsrlimit":35,"prop":"imageinfo","iiprop":"url|extmetadata|size|mime"}
 data=api("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p)); out=[]
 for page in data.get("query",{}).get("pages",{}).values():
  inf=(page.get("imageinfo") or [{}])[0]; md=inf.get("extmetadata",{})
  def val(k):
   z=md.get(k,{}); return re.sub("<[^>]+>","",z.get("value","")) if isinstance(z,dict) else ""
  lic=(val("LicenseShortName")+" "+val("UsageTerms")).lower(); u=inf.get("url","")
  if not any(k in lic for k in ["cc0","public domain","cc by","cc-by","cc by-sa","cc-by-sa"]):continue
  if any(k in lic for k in ["noncommercial","non-commercial","no derivatives","cc nd"]):continue
  if not u.lower().endswith((".mp4",".webm",".ogv")) or inf.get("width",0)<640:continue
  out.append({"title":page.get("title",""),"url":u,"license":val("LicenseShortName") or val("UsageTerms"),"artist":val("Artist"),"page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(page.get("title","").replace(" ","_"))})
 return out
def download(url,path):
 r=urllib.request.Request(url,headers={"User-Agent":UA})
 with urllib.request.urlopen(r,timeout=100) as x,open(path,"wb") as f:
  while True:
   b=x.read(1024*1024)
   if not b:break
   f.write(b)
 if path.stat().st_size<100000:raise RuntimeError("File too small")
def duration(path):
 return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(path)],text=True).strip())
def ts(s):
 n=int(s*100);h,n=divmod(n,360000);m,n=divmod(n,6000);z,n=divmod(n,100);return f"{h}:{m:02}:{z:02}.{n:02}"
def captions(text,dest,total):
 sentences=re.split(r"(?<=[.!?])\s+",text.strip()); weights=[max(1,len(s.split())) for s in sentences]; t=0; ev=[]
 for s,w in zip(sentences,weights):
  span=total*w/sum(weights); words=s.split(); lines=[]; cur=""
  for word in words:
   if len(cur)+len(word)+1>34:lines.append(cur);cur=word
   else:cur=(cur+" "+word).strip()
  if cur:lines.append(cur)
  ev.append(f"Dialogue: 0,{ts(t)},{ts(min(total,t+span))},Caption,,0,0,0,,{r'\\N'.join(lines[:2])}");t+=span
 head=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 2","[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding","Style: Caption,DejaVu Sans,48,&H00FFFFFF,&H0000FFFF,&H00101010,&H90000000,1,0,0,0,100,100,0,0,1,3,1,2,100,100,190,1","Style: Brand,DejaVu Sans,44,&H0000D7FF,&H0000D7FF,&H00101010,&H90000000,1,0,0,0,100,100,1,0,1,2,1,8,80,80,90,1","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",f"Dialogue: 1,0:00:00.00,{ts(min(2.2,total))},Brand,,0,0,0,,FACT BITES UNBOXED"]
 dest.write_text("\n".join(head+ev)+"\n")
def main():
 OUT.mkdir(parents=True,exist_ok=True); topic=TOPICS[(int(os.getenv("GITHUB_RUN_NUMBER","1"))-1)%len(TOPICS)]
 narration=" ".join([topic["hook"]]+topic["lines"]); print("TOPIC="+topic["title"])
 found=candidates(topic["query"]); print("LICENSED_VIDEO_CANDIDATES="+str(len(found)))
 if len(found)<2:raise RuntimeError("BLOCKED: fewer than two relevant, openly licensed Commons video clips. No slideshow or unrelated filler will be made.")
 selected=[]
 for item in found:
  if len(selected)==3:break
  try:
   p=OUT/f"source_{len(selected)+1}"+Path(urllib.parse.urlparse(item["url"]).path).suffix;download(item["url"],p);d=duration(p)
   if d<2.5:continue
   item.update(local=str(p),duration=d);selected.append(item)
  except Exception as e:print("REJECTED",item["title"],str(e)[:120])
 if len(selected)<2:raise RuntimeError("BLOCKED: fewer than two Commons clips passed download and media validation.")
 import edge_tts
 voice=OUT/"narration.mp3"
 async def tts():await edge_tts.Communicate(narration,voice="en-US-GuyNeural",rate="+3%",pitch="-3Hz").save(str(voice))
 asyncio.run(tts()); total=duration(voice)
 if not 20<=total<=45:raise RuntimeError(f"BLOCKED: voice length {total:.1f}s is outside 20–45 seconds.")
 clips=[]; each=total/len(selected)
 for i,item in enumerate(selected):
  clip=OUT/f"scene_{i+1}.mp4";vf="scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,eq=contrast=1.04:saturation=1.08,unsharp=5:5:0.35,format=yuv420p"
  start=max(0,(item["duration"]-each)/2)
  run(["ffmpeg","-y","-loglevel","error","-ss",str(start),"-i",item["local"],"-t",str(each),"-vf",vf,"-an","-r","30","-c:v","libx264","-preset","fast","-crf","19","-pix_fmt","yuv420p",str(clip)]);clips.append(clip)
 concat=OUT/"concat.txt";concat.write_text("".join("file '"+str(x.resolve())+"'\n" for x in clips))
 silent=OUT/"silent.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy","-t",str(total),str(silent)])
 ass=OUT/"captions.ass";captions(narration,ass,total);final=OUT/"FACT-BITES-UNBOXED.mp4"
 run(["ffmpeg","-y","-loglevel","error","-i",str(silent),"-i",str(voice),"-vf",f"ass={ass}:fontsdir=/usr/share/fonts/truetype/dejavu","-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","fast","-crf","19","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart","-pix_fmt","yuv420p",str(final)])
 (OUT/"ASSET-CREDITS.txt").write_text("TOPIC: "+topic["title"]+"\n\n"+narration+"\n\n"+ "\n\n".join(f"{x['title']}\nCreator: {x['artist']}\nLicense: {x['license']}\nSource: {x['page']}" for x in selected))
 info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(final)],text=True));v=next(s for s in info["streams"] if s["codec_type"]=="video");d=float(info["format"]["duration"])
 if (v["width"],v["height"])!=(1080,1920) or not 20<=d<=45:raise RuntimeError("Final technical QA failed")
 print(f"VIDEO_READY={final}");print(f"DURATION={d:.2f}");print(f"FRAME={v['width']}x{v['height']}");print("VISUAL_REVIEW_REQUIRED=source relevance and subtitle timing need visual inspection")
if __name__=="__main__":
 try:main()
 except Exception as e:print(str(e),file=sys.stderr);sys.exit(1)

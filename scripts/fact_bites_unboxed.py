#!/usr/bin/env python3
"""FACT BITES UNBOXED: conservative, license-checked video assembly."""
import asyncio, json, os, re, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path
OUT=Path("output/unboxed"); UA="FACT-BITES-UNBOXED/1.1 educational video"
TOPICS=[
{"title":"Why a zipper stays closed","terms":["zipper","zip fastener","fastening zipper"],"hook":"A zipper looks simple. But one tiny slider is doing a surprisingly precise job.","lines":["Inside the slider are two channels shaped to guide the teeth together.","As you pull it, each side is guided into the other, making the teeth interlock.","Pull the slider the opposite way, and the channels separate the teeth again.","Tooth shapes vary by design, but the slider turns one small movement into a long, reliable closure."]},
{"title":"How a microwave magnetron makes microwaves","terms":["microwave magnetron","magnetron microwave","microwave oven magnetron"],"hook":"The microwave oven has a hidden power source: a device that turns electricity into invisible waves.","lines":["It is called a magnetron, a specialised vacuum tube inside the oven.","Electrons move through the tube under electric and magnetic fields, creating high-frequency microwave energy.","A waveguide carries that energy into the metal cooking cavity, where it reflects and spreads around the food.","The food absorbs some of that energy, causing molecules to move and heat up. The exact heating pattern depends on the oven and the food."]},
{"title":"How a ballpoint pen controls ink","terms":["ballpoint pen","pen writing","writing instrument"],"hook":"This tiny metal ball is why a pen can carry ink without spilling it everywhere.","lines":["A ballpoint pen stores thick ink in a narrow reservoir.","At the tip, a tiny ball sits in a socket with just enough room to rotate.","As it rolls across paper, it picks up ink from inside and transfers a thin film onto the page.","The close fit helps control the flow, moving ink onto paper instead of letting the reservoir pour out."]},
{"title":"Why a tape measure blade curves","terms":["tape measure","measuring tape","retractable tape"],"hook":"A tape measure can stretch out several feet without folding. The secret is its curved blade.","lines":["The blade has a shallow curve across its width, making it stiffer than a flat strip.","That cross-section resists bending under its own weight, so the tape can extend outward for a while.","Push it back toward the case and the blade can flex into a tight coil.","Stand-out distance depends on blade width, thickness and design, but the curve gives the strip much of its strength."]},
{"title":"How a pop-up toaster stops","terms":["pop up toaster","toaster bread","toaster mechanism"],"hook":"A toaster can pop your bread up automatically. But what releases the latch?","lines":["In many traditional pop-up toasters, a timing circuit or thermal control determines when heating ends.","An electromagnet holds the bread carriage down during the heating cycle.","When the cycle ends, power to the magnet is cut, the latch releases, and a spring lifts the toast.","Models vary, but the pop-up action combines a latch, a spring and automatic control."]}]
def getj(url):
 req=urllib.request.Request(url,headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=45) as r:return json.loads(r.read())
def license_ok(url,rights=""):
 s=(str(url)+" "+str(rights)).lower()
 if any(x in s for x in ["by-nc","by-nd","noncommercial","non-commercial","no derivatives"]):return False
 return any(x in s for x in ["creativecommons.org/licenses/by/","creativecommons.org/licenses/by-sa/","creativecommons.org/publicdomain/zero/","creativecommons.org/publicdomain/mark/","public domain"])
def ia(term):
 q=f'mediatype:movies AND (title:("{term}") OR description:("{term}"))'
 ps=[("q",q),("fl[]","identifier"),("fl[]","title"),("fl[]","description"),("fl[]","licenseurl"),("rows","10"),("output","json")]
 docs=getj("https://archive.org/advancedsearch.php?"+urllib.parse.urlencode(ps)).get("response",{}).get("docs",[])
 out=[]
 for d in docs[:8]:
  ident=d.get("identifier")
  if not ident:continue
  mdj=getj("https://archive.org/metadata/"+urllib.parse.quote(ident));m=mdj.get("metadata",{})
  lic=m.get("licenseurl",d.get("licenseurl",""));rights=m.get("rights","")
  if not license_ok(lic,rights):continue
  desc=str(m.get("description",""));title=str(m.get("title",d.get("title",ident)))
  tokens=[w for w in re.findall(r"[a-z0-9]+",term.lower()) if len(w)>2]
  corpus=(title+" "+desc+" "+str(m.get("subject",""))).lower()
  score=sum((2 if w in title.lower() else 1) for w in tokens if w in corpus)
  if score<1:continue
  files=[f for f in mdj.get("files",[]) if str(f.get("name","")).lower().endswith(".mp4") and f.get("source")=="original" and 500000<int(f.get("size",0) or 0)<350000000]
  if not files:continue
  f=max(files,key=lambda z:int(z.get("size",0) or 0))
  out.append({"title":title,"creator":m.get("creator",""),"description":desc[:1000],"url":"https://archive.org/download/"+urllib.parse.quote(ident,safe="")+"/"+urllib.parse.quote(f["name"],safe=""),"license":lic,"page":"https://archive.org/details/"+ident,"score":score})
 return sorted(out,key=lambda x:x["score"],reverse=True)
def commons(term):
 ps={"action":"query","format":"json","generator":"search","gsrnamespace":6,"gsrsearch":term,"gsrlimit":40,"prop":"imageinfo","iiprop":"url|extmetadata|size|mime"}
 pages=getj("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(ps)).get("query",{}).get("pages",{})
 out=[]
 for p in pages.values():
  inf=(p.get("imageinfo") or [{}])[0];md=inf.get("extmetadata",{})
  def val(k):
   x=md.get(k,{});return re.sub("<[^>]+>","",x.get("value","")) if isinstance(x,dict) else ""
  lic=val("LicenseShortName")+" "+val("UsageTerms");u=inf.get("url","")
  if not license_ok(lic) or not u.lower().endswith((".mp4",".webm",".ogv")):continue
  title=p.get("title","")
  out.append({"title":title,"creator":val("Artist"),"description":val("ImageDescription")[:1000],"url":u,"license":lic,"page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"score":1})
 return out
def run(c):subprocess.run(c,check=True)
def dur(p):return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(p)],text=True).strip())
def dl(item,p):
 req=urllib.request.Request(item["url"],headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=120) as r,open(p,"wb") as f:
  while b:=r.read(1024*1024):f.write(b)
 if p.stat().st_size<100000:raise RuntimeError("video file too small")
def stamp(t):
 n=int(t*100);h,n=divmod(n,360000);m,n=divmod(n,6000);s,n=divmod(n,100);return f"{h}:{m:02}:{s:02}.{n:02}"
def captions(text,path,total):
 sentences=re.split(r"(?<=[.!?])\s+",text.strip());weights=[max(1,len(s.split())) for s in sentences];den=sum(weights);t=0;ev=[]
 for s,w in zip(sentences,weights):
  span=total*w/den;lines=[];cur=""
  for word in s.split():
   if len(cur)+len(word)+1>32:lines.append(cur);cur=word
   else:cur=(cur+" "+word).strip()
  if cur:lines.append(cur)
  cap="\\N".join(lines[:2]);ev.append(f"Dialogue: 0,{stamp(t)},{stamp(min(total,t+span))},Caption,,0,0,0,,{cap}");t+=span
 head=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 2","[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding","Style: Caption,DejaVu Sans,48,&H00FFFFFF,&H0000FFFF,&H00101010,&H90000000,1,0,0,0,100,100,0,0,1,3,1,2,100,100,250,1","Style: Brand,DejaVu Sans,40,&H0000D7FF,&H0000D7FF,&H00101010,&H90000000,1,0,0,0,100,100,1,0,1,2,1,8,80,80,90,1","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",f"Dialogue: 1,0:00:00.00,{stamp(min(2.2,total))},Brand,,0,0,0,,FACT BITES UNBOXED"]
 path.write_text("\n".join(head+ev)+"\n",encoding="utf-8")
def main():
 OUT.mkdir(parents=True,exist_ok=True);topic=TOPICS[(int(os.getenv("GITHUB_RUN_NUMBER","1"))-1)%len(TOPICS)]
 narration=" ".join([topic["hook"]]+topic["lines"]);items=[]
 for term in topic["terms"][:2]:
  for label,fn in [("IA",ia),("COMMONS",commons)]:
   try:
    got=fn(term);print(label,term,"=",len(got));items.extend(got[:6])
   except Exception as e:print(label+"_WARNING",term,str(e)[:160])
 unique={x["url"]:x for x in items};candidates=sorted(unique.values(),key=lambda x:x["score"],reverse=True)
 selected=[]
 for item in candidates:
  if len(selected)>=3:break
  try:
   p=OUT / (f"source_{len(selected)+1}"+Path(urllib.parse.urlparse(item["url"]).path).suffix)
   dl(item,p);d=dur(p)
   if d<8:continue
   item.update(local=str(p),duration=d);selected.append(item)
   print("SELECTED",item["title"],"seconds",round(d,1),"license",item["license"],"source",item["page"])
  except Exception as e:print("REJECTED",item["title"],str(e)[:140])
 if not selected:raise RuntimeError("BLOCKED: neither Internet Archive nor Wikimedia Commons supplied a downloadable, explicitly reusable, topic-matched video. No irrelevant footage will be substituted.")
 import edge_tts
 voice=OUT/"narration.mp3"
 async def say():await edge_tts.Communicate(narration,voice="en-US-GuyNeural",rate="+2%",pitch="-3Hz").save(str(voice))
 asyncio.run(say());total=dur(voice)
 if not 20<=total<=45:raise RuntimeError(f"BLOCKED: narration duration {total:.1f}s outside 20–45 seconds.")
 clips=[];each=total/len(selected)
 for i,item in enumerate(selected):
  clip=OUT/f"scene_{i+1}.mp4";vf="scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1,eq=contrast=1.04:saturation=1.08,unsharp=5:5:0.35,format=yuv420p";start=max(0,(item["duration"]-each)/2)
  run(["ffmpeg","-y","-loglevel","error","-ss",str(start),"-i",item["local"],"-t",str(each),"-vf",vf,"-an","-r","30","-c:v","libx264","-preset","fast","-crf","19","-pix_fmt","yuv420p",str(clip)]);clips.append(clip)
 concat=OUT/"concat.txt";concat.write_text("".join("file '"+str(x.resolve())+"'\n" for x in clips))
 silent=OUT/"silent.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy","-t",str(total),str(silent)])
 ass=OUT/"captions.ass";captions(narration,ass,total);final=OUT/"FACT-BITES-UNBOXED.mp4"
 run(["ffmpeg","-y","-loglevel","error","-i",str(silent),"-i",str(voice),"-vf",f"ass={ass}:fontsdir=/usr/share/fonts/truetype/dejavu","-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","fast","-crf","19","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart","-pix_fmt","yuv420p",str(final)])
 frames=[]
 for i in range(3):
  frame=OUT/f"qa_{i+1}.jpg";at=min(total-0.5,total*(i+0.5)/3)
  run(["ffmpeg","-y","-loglevel","error","-ss",str(at),"-i",str(final),"-frames:v","1","-q:v","3",str(frame)]);frames.append(frame)
 run(["ffmpeg","-y","-loglevel","error","-i",str(frames[0]),"-i",str(frames[1]),"-i",str(frames[2]),"-filter_complex","hstack=inputs=3,scale=810:-1","-frames:v","1",str(OUT/"QA-CONTACT-SHEET.jpg")])
 credits="TOPIC: "+topic["title"]+"\n\n"+narration+"\n\nASSET CREDITS\n"+"\n\n".join(f"{x['title']}\nCreator: {x['creator']}\nLicense: {x['license']}\nSource: {x['page']}" for x in selected)
 (OUT/"ASSET-CREDITS.txt").write_text(credits,encoding="utf-8")
 info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show-format","-of","json",str(final)],text=True));v=next(s for s in info["streams"] if s["codec_type"]=="video");d=float(info["format"]["duration"])
 if (v["width"],v["height"])!=(1080,1920) or not 20<=d<=45 or not any(s["codec_type"]=="audio" for s in info["streams"]):raise RuntimeError("Final technical QA failed")
 print("VIDEO_READY="+str(final));print("CONTACT_SHEET="+str(OUT/"QA-CONTACT-SHEET.jpg"));print(f"DURATION={d:.2f}");print(f"FRAME={v['width']}x{v['height']}");print("SOURCE_COUNT="+str(len(selected)));print("VISUAL_REVIEW_REQUIRED=inspect contact sheet and playback before release")
if __name__=="__main__":
 try:main()
 except Exception as e:print(str(e),file=sys.stderr);sys.exit(1)

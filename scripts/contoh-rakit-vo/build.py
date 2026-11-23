import json, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R="/home/claude/siapnikah-media"; J="/tmp/job"
FONT="/tmp/fx/package/800ExtraBold/PlusJakartaSans_800ExtraBold.ttf"
FONT2="/tmp/fx/package/700Bold/PlusJakartaSans_700Bold.ttf"
MUS="/mnt/user-data/uploads/MARKBro-Studio/_pustaka/musik/calm-reassuring.mp3"
WH="/mnt/user-data/uploads/MARKBro-Studio/_pustaka/sfx/halus/transition_whoosh.wav"
DING="/mnt/user-data/uploads/MARKBro-Studio/_pustaka/sfx/halus/proper_ding.wav"
al=json.load(open(f"{J}/align.json"))
def run(c): subprocess.run(c,check=True)
PLAN={
 "a":{"src":f"{R}/reels/2026-11-24-a2.mp4","out":f"{R}/reels/2026-11-24-a3.mp4",
      "blocks":[("s",0,3.5),("s",3.5,7.3),("b",51844,"Kalian dua orang\nyang berbeda."),("s",7.3,11.5),("s",11.5,18.1),("s",18.1,22.3),("b",552,"Yang kuat bukan yang\ntanpa masalah."),("s",22.3,28.0)]},
 "b":{"src":f"{R}/reels/2026-11-24-b.mp4","out":f"{R}/reels/2026-11-24-b2.mp4",
      "blocks":[("s",0,3.5),("b",122389,"Merasa penghasilan\nbelum cukup?"),("s",3.5,8.9),("s",8.9,12.9),("s",12.9,17.3),("s",17.3,23.7),("b",172686,"Rezeki dijemput dengan\nikhtiar, dijalani\ndengan syukur."),("s",23.7,27.5),("s",27.5,33.0)]},
}
def overlay_png(text,path):
    im=Image.new("RGBA",(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    # bottom gradient
    g=Image.new("L",(1,1920))
    for y in range(1920): g.putpixel((0,y),int(max(0,(y-900)/1020)**1.3*215))
    grad=Image.merge("RGBA",[Image.new("L",(1080,1920),16)]*3+[g.resize((1080,1920))])
    im=Image.alpha_composite(im,grad); d=ImageDraw.Draw(im)
    # top soft band for brand
    f=ImageFont.truetype(FONT,78); fb=ImageFont.truetype(FONT2,36)
    lines=text.split("\n"); y=1420-len(lines)*48
    for ln in lines:
        w=d.textlength(ln,font=f); d.text(((1080-w)/2,y),ln,font=f,fill=(255,255,255,255),stroke_width=0); y+=98
    # accent bar
    d.rounded_rectangle((490,y+18,590,y+28),radius=5,fill=(231,111,81,255))
    # brand pill top-left
    d.rounded_rectangle((60,120,330,180),radius=30,fill=(248,244,227,230))
    d.text((88,128),"siapnikah.id",font=fb,fill=(16,92,67,255))
    im.save(path)
for key,P in PLAN.items():
    if len(sys.argv)>1 and key not in sys.argv[1:]: continue
    segs=al[key]["seg"]; vdur=al[key]["dur"]; assert len(segs)==len(P["blocks"])
    starts=[0.0]+[s[1] for s in segs[1:]]
    ends=starts[1:]+[vdur+1.6]
    parts=[]; cuts=[]; t=0
    for i,(blk,T) in enumerate(zip(P["blocks"],[e-s for s,e in zip(starts,ends)])):
        p=f"{J}/{key}_{i:02d}.mp4"
        if blk[0]=="s":
            _,a,b=blk; L=b-a; fct=min(T/L,1.35); rest=max(0,T-L*fct)
            vf=f"setpts={fct}*(PTS-STARTPTS),fps=30,tpad=stop_mode=clone:stop_duration={rest:.3f},trim=duration={T:.3f},scale=1080:1920,format=yuv420p"
            run(["ffmpeg","-nostdin","-loglevel","error","-y","-ss",f"{a}","-t",f"{L}","-i",P["src"],"-vf",vf,"-an","-c:v","libx264","-preset","veryfast","-crf","18",p])
        else:
            _,cid,txt=blk
            run(["python3",f"{R}/scripts/broll.py","--id",str(cid),"--detik",f"{T:.3f}","--out",f"{J}/br_{key}{i}"])
            src=[f for f in os.listdir(f"{J}/br_{key}{i}") if f.endswith(".mp4")][0]
            png=f"{J}/ov_{key}{i}.png"; overlay_png(txt,png)
            fc=(f"[0:v]scale=1080:1920,zoompan=z='min(zoom+0.0006,1.08)':d=1:s=1080x1920:fps=30[v];"
                f"[1:v]format=rgba,fade=t=in:st=0.15:d=0.35:alpha=1[o];[v][o]overlay=0:0,trim=duration={T:.3f},format=yuv420p")
            run(["ffmpeg","-nostdin","-loglevel","error","-y","-i",f"{J}/br_{key}{i}/{src}","-loop","1","-t",f"{T:.3f}","-i",png,"-filter_complex",fc,"-an","-c:v","libx264","-preset","veryfast","-crf","19",p])
            cuts+= [t, t+T]
        parts.append(p); t+=T
    total=t
    with open(f"{J}/{key}_list.txt","w") as f:
        for p in parts: f.write(f"file '{p}'\n")
    run(["ffmpeg","-nostdin","-loglevel","error","-y","-f","concat","-safe","0","-i",f"{J}/{key}_list.txt","-c","copy",f"{J}/{key}_video.mp4"])
    # audio mix
    inputs=["-i",f"/tmp/vo-{key}.wav","-stream_loop","-1","-i",MUS]
    fl=["[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=1.0,apad[vo]",
        f"[1:a]aresample=48000,volume=0.16,afade=t=in:d=1,afade=t=out:st={total-2.2:.2f}:d=2.2[mu]"]
    mixin=["[vo]","[mu]"]
    for k,ct in enumerate(cuts):
        inputs+=["-i",WH]; idx=2+k
        dly=max(0,int((ct-0.35)*1000))
        fl.append(f"[{idx}:a]aresample=48000,volume=0.35,adelay={dly}|{dly}[w{k}]"); mixin.append(f"[w{k}]")
    inputs+=["-i",DING]; idx=2+len(cuts); dly=int((starts[-1]+0.1)*1000)
    fl.append(f"[{idx}:a]aresample=48000,volume=0.25,adelay={dly}|{dly}[dg]"); mixin.append("[dg]")
    fl.append("".join(mixin)+f"amix=inputs={len(mixin)}:normalize=0:duration=first,atrim=duration={total:.3f},loudnorm=I=-15:TP=-1.5:LRA=11[aout]")
    run(["ffmpeg","-nostdin","-loglevel","error","-y",*inputs,"-filter_complex",";".join(fl),"-map","[aout]","-c:a","aac","-b:a","160k",f"{J}/{key}_audio.m4a"])
    run(["ffmpeg","-nostdin","-loglevel","error","-y","-i",f"{J}/{key}_video.mp4","-i",f"{J}/{key}_audio.m4a","-map","0:v","-map","1:a","-c:v","libx264","-preset","medium","-crf","23","-maxrate","4M","-bufsize","8M","-c:a","copy","-movflags","+faststart","-shortest",P["out"]])
    sz=os.path.getsize(P["out"])/1e6
    print(key,"durasi",round(total,1),"MB",round(sz,1),"cuts",[round(c,1) for c in cuts])

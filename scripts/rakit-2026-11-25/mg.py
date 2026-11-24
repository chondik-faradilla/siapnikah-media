#!/usr/bin/env python3
"""Render scene grafis siapnikah (1080x1920) dari naskah.json via Playwright.

python3 mg.py <key> [durasi_override.json]
Hasil: /tmp/job/<key>_s<idx>.mp4 untuk tiap block t=s/c.
Durasi scene = block["dur"] atau override {idx: detik} (dipakai saat VO ada).
Pose karakter: https://siapnikah.id/wp-content/themes/siapnikah-theme/assets/images/pose/<pose>.webp
(diunduh ke /tmp/job/pose). Font: npm @expo-google-fonts plus-jakarta-sans & fraunces di /tmp/fx.
"""
import json, sys, os, subprocess, base64, re, html
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(H))
J = "/tmp/job"; FX = "/tmp/fx"
PJ = f"{FX}/pkg-expo-google-fonts-plus-jakarta-sans-0.4.2"
FR = f"{FX}/pkg-expo-google-fonts-fraunces-0.4.1"
FPS = 30
LOGO = open(f"{R}/brand/logo-mark.svg").read()

def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()

def head_html(s):
    out = []; ital = False; i = 0
    for part in re.split(r"(\*)", s):
        if part == "*": ital = not ital; continue
        for w in part.split(" "):
            if not w: continue
            cls = "w it" if ital else "w"
            out.append(f'<span class="{cls}" data-i="{i}">{html.escape(w)}</span>'); i += 1
    return " ".join(out)

def sub_html(s):
    return " ".join(f'<span class="sw" data-i="{i}">{html.escape(w)}</span>' for i, w in enumerate(s.split()))

CSS = f"""
@font-face{{font-family:PJ;font-weight:800;src:url(data:font/ttf;base64,{b64(PJ+'/800ExtraBold/PlusJakartaSans_800ExtraBold.ttf')})}}
@font-face{{font-family:PJ;font-weight:600;src:url(data:font/ttf;base64,{b64(PJ+'/600SemiBold/PlusJakartaSans_600SemiBold.ttf')})}}
@font-face{{font-family:PJ;font-weight:700;src:url(data:font/ttf;base64,{b64(PJ+'/700Bold/PlusJakartaSans_700Bold.ttf')})}}
@font-face{{font-family:FR;font-style:italic;font-weight:600;src:url(data:font/ttf;base64,{b64(FR+'/600SemiBold_Italic/Fraunces_600SemiBold_Italic.ttf')})}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#F8F4E3;overflow:hidden;font-family:PJ;position:relative}}
.glow{{position:absolute;border-radius:50%;filter:blur(90px)}}
#g1{{width:620px;height:620px;left:-200px;top:300px;background:rgba(149,213,178,.55)}}
#g2{{width:420px;height:420px;right:-60px;top:260px;background:rgba(231,111,81,.16)}}
#g3{{width:640px;height:640px;right:-120px;bottom:120px;background:rgba(149,213,178,.6)}}
#bars{{position:absolute;left:80px;right:80px;top:290px;display:flex;gap:14px}}
#bars div{{flex:1;height:8px;border-radius:4px;background:rgba(16,92,67,.13);overflow:hidden}}
#bars i{{display:block;height:100%;background:#105C43;width:0}}
#logo{{position:absolute;left:80px;top:338px;display:flex;align-items:center;gap:14px;font-weight:700;font-size:38px;color:#105C43}}
#logo svg{{height:52px;width:auto}}
#pill{{position:absolute;left:80px;top:450px;padding:14px 30px;border-radius:40px;font-weight:800;font-size:34px;letter-spacing:2px;color:#fff}}
#head{{position:absolute;left:80px;right:80px;top:560px;font-weight:800;font-size:100px;line-height:1.12;color:#105C43;letter-spacing:-2px}}
.w{{display:inline-block;opacity:0}}
.it{{font-family:FR;font-style:italic;font-weight:600;color:#C4553A;letter-spacing:-1px}}
#sub{{position:absolute;left:80px;width:560px;font-weight:600;font-size:46px;line-height:1.38;color:#2D6A4F}}
.sw{{opacity:0}}
#pose{{position:absolute;right:30px;bottom:150px;height:820px;-webkit-mask-image:linear-gradient(to bottom,#000 86%,transparent 100%)}}
#cta{{position:absolute;left:80px;top:0;display:flex;flex-direction:column;gap:22px;opacity:0}}
#cta .btn{{background:#E76F51;color:#fff;font-weight:800;font-size:46px;padding:26px 44px;border-radius:60px;box-shadow:0 18px 40px rgba(231,111,81,.35)}}
#cta .url{{font-weight:800;font-size:60px;color:#105C43}}
"""

PAGE = """<html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class=glow id=g1></div><div class=glow id=g2></div><div class=glow id=g3></div>
<div id=bars>{bars}</div>
<div id=logo>{logo}<span>siapnikah.id</span></div>
<div id=pill style="background:{pc}">{label}</div>
<div id=head>{head}</div>
<div id=sub>{sub}</div>
<div id=cta><div class=btn>Cek kesiapanmu &rarr;</div><div class=url>siapnikah.id</div></div>
<img id=pose src="data:image/webp;base64,{pose}">
<script>
const D={dur}, SEG={seg}, NSEG={nseg}, CTA={cta};
const H=document.getElementById('head'), S=document.getElementById('sub');
const hw=[...document.querySelectorAll('.w')], sw=[...document.querySelectorAll('.sw')];
function ease(x){{x=Math.min(1,Math.max(0,x));return 1-Math.pow(1-x,3)}}
function back(x){{x=Math.min(1,Math.max(0,x));const c=1.5;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}}
// posisi sub di bawah headline
S.style.top=(H.offsetTop+H.offsetHeight+70)+'px';
const C=document.getElementById('cta'); C.style.top=(S.offsetTop+S.offsetHeight+60)+'px';
const bars=[...document.querySelectorAll('#bars i')];
window.setT=function(t){{
  bars.forEach((b,i)=>{{b.style.width=(i<SEG?100:(i==SEG?Math.min(100,t/D*100):0))+'%'}});
  const p=document.getElementById('pill'); const a=ease((t-0.05)/0.45);
  p.style.opacity=a; p.style.transform=`translateY(${{(1-a)*24}}px)`;
  hw.forEach((w,i)=>{{const k=back((t-0.2-i*0.07)/0.5); w.style.opacity=Math.min(1,Math.max(0,(t-0.2-i*0.07)/0.25)); w.style.transform=`translateY(${{(1-k)*40}}px)`}});
  const s0=0.35+hw.length*0.07+0.25;
  const spd=Math.max(0.04,Math.min(0.11,(D*0.55-s0)/Math.max(1,sw.length)));
  sw.forEach((w,i)=>{{w.style.opacity=0.12+0.88*ease((t-s0-i*spd)/0.3)}});
  const po=document.getElementById('pose'); const q=ease((t-0.15)/0.7);
  po.style.opacity=q; po.style.transform=`translate(${{(1-q)*90}}px, ${{Math.sin(t*1.6)*8}}px)`;
  const g=document.getElementById('g3'); g.style.transform=`scale(${{1+0.06*Math.sin(t*1.2)}})`;
  if(CTA){{const c=back((t-s0-0.3)/0.5); C.style.opacity=Math.min(1,Math.max(0,(t-s0-0.3)/0.3)); C.style.transform=`scale(${{0.85+0.15*c}})`; C.style.transformOrigin='left center';}}
  const out=ease((t-(D-0.22))/0.22); document.body.style.opacity=1-0.0*out;
}};
</script></body></html>"""

COL = {"o": "#E76F51", "g": "#2D6A4F", "m": "#52B788"}

def main():
    key = sys.argv[1]
    nas = json.load(open(f"{H}/naskah.json"))[key]["blocks"]
    ov = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    scenes = [i for i, b in enumerate(nas) if b["t"] in "sc"]
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1920})
        for n, i in enumerate(scenes):
            if only and str(i) not in only: continue
            b = nas[i]; D = float(ov.get(str(i), b["dur"]))
            page = PAGE.format(css=CSS, bars="".join("<div><i></i></div>" for _ in scenes),
                               logo=LOGO, pc=COL[b["lc"]], label=html.escape(b["label"]),
                               head=head_html(b["head"]), sub=sub_html(b["sub"]),
                               pose=b64(f"{J}/pose/{b['pose']}.webp"), dur=D, seg=n,
                               nseg=len(scenes), cta="true" if b["t"] == "c" else "false")
            open(f"{J}/{key}_s{i}.html", "w").write(page)
            pg.goto(f"file://{J}/{key}_s{i}.html"); pg.wait_for_timeout(300)
            out = f"{J}/{key}_s{i}.mp4"
            ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS),
                                   "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                                   "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
            nf = int(round(D * FPS))
            for f in range(nf):
                pg.evaluate(f"setT({f / FPS})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close(); ff.wait()
            print(out, D, flush=True)
        br.close()

if __name__ == "__main__":
    main()

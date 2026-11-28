#!/usr/bin/env python3
"""Cover 1080x1920 (aman dipotong 1080x1350 di tengah). python3 cover.py <key> <out.jpg>"""
import sys, os, html, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mg import CSS, LOGO, b64, J
from playwright.sync_api import sync_playwright
COV = {
 "a": {"kicker": "KEUANGAN", "title": "Punya utang? *Ceritakan* sebelum akad", "sub": "3 langkah jujur soal uang.", "pose": "pria-03"},
 "b": {"kicker": "BENEFIT MENIKAH", "title": "Menikah bikin *umur panjang?*", "sub": "Ini kata riset, dan syaratnya.", "pose": "hijab-04"},
}
def t(s):
    return re.sub(r"\*(.+?)\*", r'<span class=it>\1</span>', html.escape(s))
key, out = sys.argv[1], sys.argv[2]; c = COV[key]
page = f"""<html><head><meta charset="utf-8"><style>{CSS}
#k{{position:absolute;left:80px;top:340px;padding:16px 34px;border-radius:44px;background:#E76F51;color:#fff;font-weight:800;font-size:38px;letter-spacing:2px}}
#t{{position:absolute;left:80px;right:80px;top:450px;font-weight:800;font-size:128px;line-height:1.06;color:#105C43;letter-spacing:-3px}}
#s{{position:absolute;left:80px;width:520px;top:1080px;font-weight:600;font-size:50px;line-height:1.3;color:#2D6A4F}}
#pose{{opacity:1;bottom:240px;height:860px}}
#lg{{position:absolute;left:80px;bottom:320px;display:flex;align-items:center;gap:14px;font-weight:700;font-size:44px;color:#105C43}}
#lg svg{{height:60px;width:auto}}
</style></head><body>
<div class=glow id=g1></div><div class=glow id=g2></div><div class=glow id=g3></div>
<div id=k>{c['kicker']}</div><div id=t>{t(c['title'])}</div><div id=s>{html.escape(c['sub'])}</div>
<div id=lg>{LOGO}<span>siapnikah.id</span></div>
<img id=pose style="{'height:700px' if key=='a' else ''}" src="data:image/webp;base64,{b64(f"{J}/pose/{c['pose']}.webp")}">
</body></html>"""
open(f"{J}/cover_{key}.html", "w").write(page)
with sync_playwright() as pw:
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(f"file://{J}/cover_{key}.html"); pg.wait_for_timeout(400)
    pg.screenshot(path=out, type="jpeg", quality=90); br.close()
print(out)

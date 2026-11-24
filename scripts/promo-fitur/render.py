"""Render video promo fitur siapnikah.id 9:16 dalam 3 gaya (A hijau, B krem, C langkah)."""
import json, os, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 30
TUT = os.environ.get('SRC', 'src/')  # folder video panduan (unduh dari panduan/ di repo)
F_PJS = 'fonts/PlusJakartaSans.ttf'
F_FRA = 'fonts/Fraunces-Italic.ttf'
GREEN, DEEP, MINT, CREAM, ORANGE, INK = '#2D6A4F', '#105C43', '#95D5B2', '#F8F4E3', '#E76F51', '#1B1B2F'

def font(size, weight=800, path=F_PJS):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([weight] if path == F_PJS else [0, 0, 72, weight])
    except Exception:
        pass
    return f

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def text_block(d, text, f, x, y, maxw, fill, align='left', lh=1.18):
    lines = wrap(d, text, f, maxw)
    asc = f.size * lh
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=f)
        xx = x + (maxw - tw) / 2 if align == 'center' else x
        d.text((xx, y + i * asc), ln, font=f, fill=fill)
    return y + len(lines) * asc

def bg(style):
    im = Image.new('RGB', (W, H), CREAM if style == 'B' else DEEP)
    px = np.zeros((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H)[:, None]
    if style == 'A':
        c1, c2 = np.array([16, 92, 67]), np.array([45, 106, 79])
    elif style == 'B':
        c1, c2 = np.array([248, 244, 227]), np.array([252, 250, 242])
    else:
        c1, c2 = np.array([12, 50, 38]), np.array([27, 27, 47])
    px[:] = (c1 * (1 - yy) + c2 * yy)[:, :, None].transpose(0, 2, 1) if False else (c1[None, None, :] * (1 - yy[:, :, None]) + c2[None, None, :] * yy[:, :, None])
    im = Image.fromarray(px.astype(np.uint8))
    d = ImageDraw.Draw(im)
    # titik dekoratif halus
    dot = (255, 255, 255, 18) if style != 'B' else (45, 106, 79, 22)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for yy2 in range(40, H, 46):
        for xx2 in range(40, W, 46):
            od.ellipse((xx2, yy2, xx2 + 4, yy2 + 4), fill=dot)
    # blob lembut
    blob = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(blob)
    col = (149, 213, 178, 70) if style != 'B' else (149, 213, 178, 110)
    bd.ellipse((-260, 1250, 560, 2070), fill=col); bd.ellipse((640, -200, 1380, 540), fill=(231, 111, 81, 45))
    blob = blob.filter(ImageFilter.GaussianBlur(90))
    im = Image.alpha_composite(im.convert('RGBA'), blob)
    im = Image.alpha_composite(im, ov)
    return im

def pill(d, x, y, text, fg, bgc, size=34):
    f = font(size, 800)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle((x, y, x + tw + 52, y + size + 30), radius=40, fill=bgc)
    d.text((x + 26, y + 13), text, font=f, fill=fg)
    return x + tw + 52

def pose(name, h):
    im = Image.open(f'pose/{name}.webp').convert('RGBA')
    r = h / im.height
    return im.resize((int(im.width * r), h), Image.LANCZOS)

def header(im, style, hook):
    d = ImageDraw.Draw(im)
    fg = INK if style == 'B' else 'white'
    pill(d, 64, 96, 'siapnikah.id', 'white' if style == 'B' else DEEP, GREEN if style == 'B' else MINT)
    f = font(74, 800)
    y = text_block(d, hook, f, 64, 196, W - 128, fg)
    if style == 'B':
        d.rounded_rectangle((64, y + 14, 64 + 220, y + 26), radius=6, fill=ORANGE)
    else:
        d.rounded_rectangle((64, y + 14, 64 + 160, y + 24), radius=5, fill=ORANGE)
    return y + 40

def scene_png(spec, i, path):
    style = spec['style']
    im = bg(style)
    d = ImageDraw.Draw(im)
    n = len(spec['lines'])
    fg = INK if style == 'B' else 'white'
    if i == 0:  # hook
        f = font(108, 800)
        hook = spec['hook']
        y = 330
        pill(d, 64, 120, 'siapnikah.id', 'white' if style == 'B' else DEEP, GREEN if style == 'B' else MINT)
        if style == 'C':
            pill(d, 64, 230, 'PANDUAN SINGKAT', 'white', ORANGE, 30)
        y = text_block(d, hook, f, 64, y, W - 128, fg, lh=1.12)
        d.rounded_rectangle((64, y + 24, 64 + 260, y + 40), radius=8, fill=ORANGE)
        p = pose(spec['pose'], 820)
        im.alpha_composite(p, (W - p.width - 40, H - p.height - 40))
        f2 = font(40, 600)
        text_block(d, 'Fitur gratis di siapnikah.id', f2, 64, y + 80, 600, MINT if style != 'B' else GREEN)
    elif i == n - 1:  # CTA
        f = font(92, 800)
        pill(d, 64, 120, 'siapnikah.id', 'white' if style == 'B' else DEEP, GREEN if style == 'B' else MINT)
        y = text_block(d, 'Bukan cari jodoh.', f, 64, 330, W - 128, fg)
        ff = ImageFont.truetype(F_FRA, 92)
        y = text_block(d, 'Tapi siap untuk yang tepat.', ff, 64, y + 6, W - 128, ORANGE if style == 'B' else MINT)
        # tombol CTA
        bf = font(52, 800)
        label = 'Daftar gratis  →'
        tw = d.textlength(label, font=bf)
        d.rounded_rectangle((64, y + 70, 64 + tw + 90, y + 70 + 120), radius=60, fill=ORANGE)
        d.text((64 + 45, y + 70 + 30), label, font=bf, fill='white')
        f3 = font(46, 700)
        d.text((64, y + 230), 'siapnikah.id', font=f3, fill=fg)
        p = pose(spec['pose'], 760)
        im.alpha_composite(p, (W - p.width - 30, H - p.height - 40))
    else:
        top = header(im, style, spec['hook'])
        d = ImageDraw.Draw(im)
        # slot kartu (tempat klip) di y=CARD_Y
        cy = 640
        shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle((40 + 6, cy + 24, 1040 + 6, cy + 24 + 750), radius=34, fill=(0, 0, 0, 90))
        shadow = shadow.filter(ImageFilter.GaussianBlur(22)); im.alpha_composite(shadow)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((32, cy - 8, 1048, cy + 758), radius=36, fill='white')
        # caption
        cap = spec['caps'][i]
        cf = font(56, 800)
        capy = cy + 800
        if style == 'C':
            num = spec['steps'][i]
            d.ellipse((64, capy, 64 + 130, capy + 130), fill=ORANGE)
            nf = font(84, 800); tw = d.textlength(num, font=nf)
            d.text((64 + 65 - tw / 2, capy + 12), num, font=nf, fill='white')
            text_block(d, cap, cf, 220, capy + 10, W - 290, 'white')
        else:
            lines = wrap(d, cap, cf, W - 200)
            hh = len(lines) * cf.size * 1.18 + 56
            d.rounded_rectangle((48, capy, W - 48, capy + hh), radius=28, fill=CREAM if style == 'A' else GREEN)
            text_block(d, cap, cf, 84, capy + 26, W - 168, INK if style == 'A' else 'white')
        # progres
        for k in range(1, n - 1):
            x = 64 + (k - 1) * 46
            d.rounded_rectangle((x, H - 96, x + 34, H - 86), radius=5, fill=ORANGE if k == i else ((255, 255, 255, 90) if style != 'B' else (27, 27, 47, 60)))
        p = pose(spec['pose'], 400)
        im.alpha_composite(p, (W - p.width - 24, H - p.height - 10))
    im.convert('RGB').save(path)

def run(cmd):
    subprocess.run(cmd, check=True)

def build(spec, timing):
    vid = spec['id']; os.makedirs(f'out/{vid}', exist_ok=True)
    OFF = 0.35
    st = timing['starts']; vo_end = timing['dur']
    n = len(spec['lines'])
    bounds = [0.0] + [s + OFF - 0.12 for s in st[1:]] + [vo_end + OFF + 1.6]
    X = 0.25
    segs = []
    for i in range(n):
        png = f'out/{vid}/s{i}.png'; scene_png(spec, i, png)
        dur = bounds[i + 1] - bounds[i] + (X if i < n - 1 else 0)
        out = f'out/{vid}/s{i}.mp4'
        clip = spec['clips'][i]
        if clip:
            f, t0 = clip
            ch = 860 if 'menu-member' in f else 885
            cw = int(ch * 4 / 3) // 2 * 2
            x0 = (1920 - cw) // 2
            # klip 4:3 dalam kartu 1000x750 + zoom pelan + sudut membulat
            vf = (f"[1:v]scale=1920:1080,crop={cw}:{ch}:{x0}:0,scale=1000:750,"
                  f"scale=w='1000*(1+0.06*t/{dur:.2f})':h=-2:eval=frame,crop=1000:750,setsar=1,format=rgba,"
                  f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lt(min(min(X,W-1-X),min(Y,H-1-Y)),28),if(lt(hypot(min(X,W-1-X)-28,min(Y,H-1-Y)-28),28)+gt(min(X,W-1-X),27)+gt(min(Y,H-1-Y),27),255,0),255)'[c];"
                  f"[0:v][c]overlay=40:640:format=auto,format=yuv420p[v]")
            run(['ffmpeg', '-loglevel', 'error', '-y', '-loop', '1', '-t', f'{dur:.3f}', '-i', png,
                 '-ss', str(t0), '-t', f'{dur:.3f}', '-i', TUT + f, '-filter_complex', vf, '-map', '[v]',
                 '-r', str(FPS), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', out])
        else:
            vf = f"scale=w='{W}*(1+0.03*t/{dur:.2f})':h=-2:eval=frame,crop={W}:{H},format=yuv420p"
            run(['ffmpeg', '-loglevel', 'error', '-y', '-loop', '1', '-t', f'{dur:.3f}', '-i', png, '-vf', vf,
                 '-r', str(FPS), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', out])
        segs.append((out, dur))
    ins = []; [ins.extend(['-i', s]) for s, _ in segs]
    fc = ''; prev = '0:v'; acc = 0; trans = []
    tr = {'A': 'slideleft', 'B': 'smoothup', 'C': 'fade'}[spec['style']]
    for i in range(1, len(segs)):
        acc += segs[i - 1][1] - X
        fc += f'[{prev}][{i}:v]xfade=transition={tr}:duration={X}:offset={acc:.3f}[v{i}];'; prev = f'v{i}'
        trans.append(acc + X / 2)
    run(['ffmpeg', '-loglevel', 'error', '-y', *ins, '-filter_complex', fc.rstrip(';'), '-map', f'[{prev}]',
         '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', f'out/{vid}/video.mp4'])
    total = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'out/{vid}/video.mp4']))
    # audio
    inputs = ['-i', f'vo/{vid}.wav', '-i', f'music_{spec["style"]}.wav']; filt = []; extra = []; k = 2
    for t in trans:
        inputs += ['-i', 'whoosh.wav']; d = int(max(0, t - 0.3) * 1000)
        filt.append(f'[{k}:a]aresample=44100,adelay={d}|{d},volume=0.32[w{k}]'); extra.append(f'[w{k}]'); k += 1
    cta = int((bounds[n - 1] + 0.2) * 1000)
    inputs += ['-i', 'ding.wav']; filt.append(f'[{k}:a]aresample=44100,adelay={cta}|{cta},volume=0.4[dg]'); extra.append('[dg]')
    o = int(OFF * 1000)
    filt.append(f'[0:a]aresample=44100,adelay={o}|{o},apad=whole_dur={total + 1:.2f},asplit=2[vo][vok]')
    filt.append('[1:a]aresample=44100,volume=0.5[mu]')
    filt.append('[mu][vok]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[duck]')
    filt.append(f"[vo][duck]{''.join(extra)}amix=inputs={2 + len(extra)}:normalize=0,atrim=0:{total:.3f},afade=t=in:d=0.3,afade=t=out:st={total - 1.2:.3f}:d=1.2,loudnorm=I=-15:TP=-1.5:LRA=9[a]")
    run(['ffmpeg', '-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[a]', '-ac', '2', '-ar', '44100', f'out/{vid}/mix.wav'])
    run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'out/{vid}/video.mp4', '-i', f'out/{vid}/mix.wav', '-map', '0:v', '-map', '1:a',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-maxrate', '5M', '-bufsize', '10M', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-shortest', f'final/{vid}.mp4'])
    # cover dari scene hook
    Image.open(f'out/{vid}/s0.png').convert('RGB').save(f'final/{vid}.jpg', quality=90)
    print(vid, 'done', round(total, 1), 's')

if __name__ == '__main__':
    os.makedirs('final', exist_ok=True)
    S = json.load(open('scripts.json')); Tm = json.load(open('timing.json'))
    only = sys.argv[1:] or [s['id'] for s in S]
    for s in S:
        if s['id'] in only:
            build(s, Tm[s['id']])

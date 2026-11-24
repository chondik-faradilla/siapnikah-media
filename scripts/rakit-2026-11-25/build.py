#!/usr/bin/env python3
"""Rakit reel siapnikah 2026-11-25 (slot a/b) dari naskah.json.

python3 build.py <key> <out.mp4> [vo.wav]
- Tanpa vo.wav: durasi scene = naskah "dur" (versi darurat, item ditandai perlu_vo).
- Dengan vo.wav: jalankan whisper (align) -> durasi tiap block mengikuti kalimat VO,
  scene grafis di-render ulang via mg.py dengan durasi itu.
Butuh: /tmp/fx (font npm), /tmp/job/pose/*.webp, musik & SFX di /mnt/user-data/uploads/MARKBro-Studio.
"""
import json, subprocess, sys, os, re, difflib
from PIL import Image, ImageDraw, ImageFont
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(H)); J = "/tmp/job"
FONT = "/tmp/fx/package/800ExtraBold/PlusJakartaSans_800ExtraBold.ttf"
FONT2 = "/tmp/fx/package/700Bold/PlusJakartaSans_700Bold.ttf"
LIB = "/mnt/user-data/uploads/MARKBro-Studio/_pustaka"
MUS = f"{LIB}/musik/calm-reassuring.mp3"; WH = f"{LIB}/sfx/halus/transition_whoosh.wav"; DING = f"{LIB}/sfx/halus/proper_ding.wav"
def run(c): subprocess.run(c, check=True)

def align(key, blocks, vo):
    import numpy as np
    from faster_whisper import WhisperModel
    norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", vo, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, language="id", word_timestamps=True)
    words = [(norm(w.word), w.start, w.end) for s in segs for w in s.words if norm(w.word)]
    sw, owner = [], []
    for i, b in enumerate(blocks):
        for w in b["vo"].split():
            if norm(w): sw.append(norm(w)); owner.append(i)
    sm = difflib.SequenceMatcher(None, sw, [w[0] for w in words], autojunk=False)
    mp = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): mp[blk.a + k] = blk.b + k
    starts = []
    for i in range(len(blocks)):
        idx = [j for j, o in enumerate(owner) if o == i and j in mp]
        starts.append(words[mp[idx[0]]][1] if idx else None)
    dur = len(a) / 16000
    starts[0] = 0.0
    for i in range(1, len(starts)):  # isi yang kosong (block tanpa VO) di tengah
        if starts[i] is None: starts[i] = None
    # block tanpa vo: bagi rata dengan block sebelumnya
    st = list(starts)
    for i in range(len(st)):
        if st[i] is None:
            nxt = next((st[j] for j in range(i + 1, len(st)) if st[j] is not None), dur)
            st[i] = (st[i - 1] + nxt) / 2
    ends = st[1:] + [dur + 1.6]
    return [e - s for s, e in zip(st, ends)], st

def overlay_png(text, path):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    g = Image.new("L", (1, 1920))
    for y in range(1920): g.putpixel((0, y), int(max(0, (y - 900) / 1020) ** 1.3 * 215))
    grad = Image.merge("RGBA", [Image.new("L", (1080, 1920), 16)] * 3 + [g.resize((1080, 1920))])
    im = Image.alpha_composite(im, grad); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 78); fb = ImageFont.truetype(FONT2, 36)
    lines = text.split("\n"); y = 1420 - len(lines) * 48
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((1080 - w) / 2, y), ln, font=f, fill=(255, 255, 255, 255)); y += 98
    d.rounded_rectangle((490, y + 18, 590, y + 28), radius=5, fill=(231, 111, 81, 255))
    d.rounded_rectangle((60, 120, 330, 180), radius=30, fill=(248, 244, 227, 230))
    d.text((88, 128), "siapnikah.id", font=fb, fill=(16, 92, 67, 255))
    im.save(path)

def main():
    key, out = sys.argv[1], sys.argv[2]; vo = sys.argv[3] if len(sys.argv) > 3 else None
    blocks = json.load(open(f"{H}/naskah.json"))[key]["blocks"]
    if vo:
        Ts, starts = align(key, blocks, vo)
        ov = {str(i): T for i, T in enumerate(Ts) if blocks[i]["t"] in "sc"}
        json.dump(ov, open(f"{J}/{key}_dur.json", "w"))
        run(["python3", f"{H}/mg.py", key, f"{J}/{key}_dur.json"])
    else:
        Ts = [b["dur"] for b in blocks]
    parts, cuts, t = [], [], 0.0
    for i, (b, T) in enumerate(zip(blocks, Ts)):
        p = f"{J}/{key}_s{i}.mp4"
        if b["t"] == "b":
            d = f"{J}/br_{key}{i}"
            run(["python3", f"{R}/scripts/broll.py", "--id", str(b["id"]), "--detik", f"{T:.3f}", "--out", d, "--seed", "7"])
            src = [f for f in os.listdir(d) if f.endswith(".mp4")][0]
            png = f"{J}/ov_{key}{i}.png"; overlay_png(b["txt"], png)
            p = f"{J}/{key}_b{i}.mp4"
            fc = (f"[0:v]scale=1080:1920,zoompan=z='min(zoom+0.0006,1.08)':d=1:s=1080x1920:fps=30[v];"
                  f"[1:v]format=rgba,fade=t=in:st=0.15:d=0.35:alpha=1[o];[v][o]overlay=0:0,trim=duration={T:.3f},format=yuv420p")
            run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{d}/{src}", "-loop", "1", "-t", f"{T:.3f}", "-i", png,
                 "-filter_complex", fc, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", p])
            cuts += [t, t + T]
        parts.append(p); t += T
    total = t
    with open(f"{J}/{key}_list.txt", "w") as f:
        for p in parts: f.write(f"file '{p}'\n")
    run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{J}/{key}_list.txt", "-c", "copy", f"{J}/{key}_video.mp4"])
    cta_start = sum(Ts[:-1])
    inputs = ["-stream_loop", "-1", "-i", MUS]; mix = []
    musvol = 0.16 if vo else 0.42
    fl = [f"[0:a]aresample=48000,volume={musvol},afade=t=in:d=1,afade=t=out:st={total-2.2:.2f}:d=2.2[mu]"]; mix.append("[mu]")
    n = 1
    if vo:
        inputs += ["-i", vo]
        fl.append(f"[{n}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,apad[vo]"); mix.insert(0, "[vo]"); n += 1
    for k, ct in enumerate(sorted(set(round(c, 3) for c in cuts))):
        inputs += ["-i", WH]; dly = max(0, int((ct - 0.35) * 1000))
        fl.append(f"[{n}:a]aresample=48000,volume=0.35,adelay={dly}|{dly}[w{k}]"); mix.append(f"[w{k}]"); n += 1
    inputs += ["-i", DING]; dly = int((cta_start + 0.1) * 1000)
    fl.append(f"[{n}:a]aresample=48000,volume=0.25,adelay={dly}|{dly}[dg]"); mix.append("[dg]")
    fl.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=duration={total:.3f},loudnorm=I=-15:TP=-1.5:LRA=11[aout]")
    run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(fl), "-map", "[aout]", "-c:a", "aac", "-b:a", "160k", f"{J}/{key}_audio.m4a"])
    run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{J}/{key}_video.mp4", "-i", f"{J}/{key}_audio.m4a", "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "4M", "-bufsize", "8M", "-c:a", "copy", "-movflags", "+faststart", "-shortest", out])
    print(key, "durasi", round(total, 1), "MB", round(os.path.getsize(out) / 1e6, 1), "cuts", [round(c, 1) for c in cuts])

if __name__ == "__main__":
    main()

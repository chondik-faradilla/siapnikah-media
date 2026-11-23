#!/usr/bin/env python3
"""Siapkan klip B-roll Pixabay untuk reel siapnikah (9:16, 1080x1920).

Pakai katalog broll/katalog-pixabay.json (hanya URL CDN, tanpa API key).
Klip mentah TIDAK di-commit ke repo (lisensi Pixabay melarang distribusi
file mentah); yang di-commit hanya video jadi di reels/.

Contoh:
  python3 scripts/broll.py --tema cincin,makan-keluarga,sholat --detik 3.5 --out /tmp/broll
  python3 scripts/broll.py --daftar            # lihat tema & jumlah klip
  python3 scripts/broll.py --id 552 --detik 4 --out /tmp/broll

Hasil: <out>/<urutan>-<tema>-<id>.mp4 (tanpa audio) + <out>/broll.json
(id, tema, tags, halaman) untuk dicatat di laporan/QA. Klip yang sudah
dipakai 14 hari terakhir (dicatat di broll/terpakai.json) dilewati bila
masih ada pilihan lain. Klip di broll/ditolak.json ({"id": "alasan"}) tidak
pernah dipilih: WAJIB cek frame tiap klip; kalau tidak cocok (minuman keras,
pakaian terbuka, kemesraan berlebihan, simbol agama lain, tidak nyambung),
tambahkan id-nya ke ditolak.json lalu jalankan ulang untuk tema itu.
"""
import argparse, json, os, random, subprocess, sys, urllib.request, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAT = os.path.join(ROOT, "broll", "katalog-pixabay.json")
USED = os.path.join(ROOT, "broll", "terpakai.json")
TOLAK = os.path.join(ROOT, "broll", "ditolak.json")  # {id: alasan}
CACHE = os.path.expanduser("~/.cache/siapnikah-broll")


def load_used():
    try:
        return json.load(open(USED))
    except Exception:
        return {}


def recent_ids(used, days=14):
    cut = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    return {int(i) for i, d in used.items() if d >= cut}


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest + ".part", "wb") as f:
        f.write(r.read())
    os.replace(dest + ".part", dest)
    return dest


def render(src, dst, detik, mulai):
    # crop tengah ke 9:16, skala 1080x1920, sedikit hangat & lembut agar
    # menyatu dengan palet krem/hijau siapnikah
    vf = ("scale=-2:1920:flags=lanczos,crop=1080:1920,"
          "eq=saturation=0.88:contrast=0.97:brightness=0.02,"
          "colorbalance=rs=0.04:gs=0.01:bs=-0.04,fps=30,format=yuv420p")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{mulai:.2f}", "-i", src,
           "-t", f"{detik:.2f}", "-vf", vf, "-an", "-c:v", "libx264",
           "-preset", "veryfast", "-crf", "20", dst]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tema", default="")
    ap.add_argument("--id", default="")
    ap.add_argument("--detik", type=float, default=3.5)
    ap.add_argument("--out", default="/tmp/broll")
    ap.add_argument("--daftar", action="store_true")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()

    kat = json.load(open(KAT))["klip"]
    try:
        tolak = {int(i) for i in json.load(open(TOLAK))}
    except Exception:
        tolak = set()
    kat = [k for k in kat if k["id"] not in tolak]
    if a.daftar:
        from collections import Counter
        for t, n in sorted(Counter(k["tema"] for k in kat).items()):
            print(f"{t:20s} {n}")
        return

    rnd = random.Random(a.seed)
    used = load_used()
    recent = recent_ids(used)
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(CACHE, exist_ok=True)

    picks = []
    if a.id:
        ids = [int(x) for x in a.id.split(",") if x.strip()]
        picks = [k for i in ids for k in kat if k["id"] == i]
    else:
        for t in [x.strip() for x in a.tema.split(",") if x.strip()]:
            pool = [k for k in kat if k["tema"] == t and k["id"] not in {p["id"] for p in picks}]
            if not pool:
                print(f"! tema '{t}' tidak ada di katalog", file=sys.stderr)
                continue
            fresh = [k for k in pool if k["id"] not in recent] or pool
            picks.append(rnd.choice(fresh))

    meta = []
    for n, k in enumerate(picks, 1):
        src = fetch(k["url"], os.path.join(CACHE, f"{k['id']}.mp4"))
        dur = float(k.get("durasi") or 6)
        mulai = max(0.0, min(dur - a.detik - 0.3, rnd.uniform(0.3, max(0.3, dur * 0.4))))
        dst = os.path.join(a.out, f"{n:02d}-{k['tema']}-{k['id']}.mp4")
        render(src, dst, a.detik, mulai)
        used[str(k["id"])] = datetime.date.today().isoformat()
        meta.append({"file": dst, "id": k["id"], "tema": k["tema"], "tags": k["tags"], "halaman": k["halaman"]})
        print(dst)

    json.dump(meta, open(os.path.join(a.out, "broll.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(used, open(USED, "w"), indent=0, sort_keys=True)


if __name__ == "__main__":
    main()

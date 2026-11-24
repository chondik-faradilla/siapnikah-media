#!/usr/bin/env python3
"""Posting teks Threads @siapnikahindo — 5x sehari (07:00, 10:00, 13:00, 17:00, 21:00 WIB).

Antrean: threads/queue/<YYYY-MM-DD>-<n>.json  (n = 1..5)
  {"publish_after": "2026-11-25T07:00:00+07:00", "text": "... (≤500 karakter)", "topik": "..."}
Setelah terbit dipindah ke threads/posted/ dengan field result + posted_at.

Satu item per run (agar jarak antarposting terjaga); item yang tertinggal
diposting pada run berikutnya. Kalau THREADS_TOKEN / THREADS_USER_ID belum
diisi, antrean dibiarkan utuh (tidak ada yang dibuang).

Secrets: THREADS_TOKEN (long-lived user token Threads). Variable: THREADS_USER_ID.
"""
import datetime, glob, json, os, sys, time, urllib.error, urllib.parse, urllib.request

T = "https://graph.threads.net/v1.0"


def call(url, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method="POST" if body else "GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:400]}")


def main():
    tok, uid = os.environ.get("THREADS_TOKEN", ""), os.environ.get("THREADS_USER_ID", "")
    now = datetime.datetime.now(datetime.timezone.utc)
    due = []
    for f in sorted(glob.glob("threads/queue/*.json")):
        item = json.load(open(f))
        if datetime.datetime.fromisoformat(item["publish_after"]) <= now:
            due.append((f, item))
    if not due:
        print("nothing due"); return 0
    if not (tok and uid):
        print(f"{len(due)} item jatuh tempo, tapi THREADS_TOKEN/THREADS_USER_ID belum diisi; antrean dibiarkan")
        return 0
    f, item = due[0]
    text = item["text"].strip()[:500]
    try:
        cid = call(f"{T}/{uid}/threads", {"media_type": "TEXT", "text": text, "access_token": tok})["id"]
        time.sleep(4)
        pid = call(f"{T}/{uid}/threads_publish", {"creation_id": cid, "access_token": tok})["id"]
        item["result"] = {"threads": pid}; rc = 0
        print("threads OK", pid)
    except Exception as e:
        msg = str(e)
        print("threads FAILED", msg)
        # token/izin bermasalah → biarkan di antrean supaya bisa dicoba lagi setelah diperbaiki
        if any(k in msg for k in ("OAuth", "access token", "190", "permission", "401", "403")):
            return 1
        item["result"] = {"threads": f"ERROR: {msg}"}; rc = 1
    item["posted_at"] = now.isoformat()
    os.makedirs("threads/posted", exist_ok=True)
    json.dump(item, open(os.path.join("threads/posted", os.path.basename(f)), "w"), ensure_ascii=False, indent=1)
    os.remove(f)
    return rc


if __name__ == "__main__":
    sys.exit(main())

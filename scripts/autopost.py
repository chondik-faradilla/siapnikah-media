"""siapnikah autopost: publish the next due item in queue/ to IG Reels, FB Reels and Threads.

Secrets (GitHub repo settings): META_PAGE_TOKEN, THREADS_TOKEN
Variables: IG_USER_ID, FB_PAGE_ID, THREADS_USER_ID
Queue item (queue/<YYYY-MM-DD>-<slot>.json):
{"publish_after": "2026-11-24T11:30:00+07:00", "video_url": "...mp4", "cover_url": "...jpg",
 "caption": "...", "threads": ["text 1", "text 2"]}
"""
import json, os, sys, time, glob, datetime, urllib.request, urllib.parse

G = "https://graph.facebook.com/v21.0"
T = "https://graph.threads.net/v1.0"
ENV = os.environ


def call(url, data=None, method=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method or ("POST" if body else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:500]}")


def ig_reel(item):
    tok, ig = ENV["META_PAGE_TOKEN"], ENV["IG_USER_ID"]
    d = {"media_type": "REELS", "video_url": item["video_url"], "caption": item["caption"],
         "share_to_feed": "true", "access_token": tok}
    if item.get("cover_url"):
        d["cover_url"] = item["cover_url"]
    cid = call(f"{G}/{ig}/media", d)["id"]
    for _ in range(60):
        st = call(f"{G}/{cid}?fields=status_code&access_token={tok}")["status_code"]
        if st == "FINISHED":
            break
        if st == "ERROR":
            raise RuntimeError("IG container ERROR")
        time.sleep(10)
    return call(f"{G}/{ig}/media_publish", {"creation_id": cid, "access_token": tok})["id"]


def fb_reel(item):
    tok, page = ENV["META_PAGE_TOKEN"], ENV["FB_PAGE_ID"]
    vid = call(f"{G}/{page}/video_reels", {"upload_phase": "start", "access_token": tok})["video_id"]
    req = urllib.request.Request(f"https://rupload.facebook.com/video-upload/v21.0/{vid}", method="POST",
                                 headers={"Authorization": f"OAuth {tok}", "file_url": item["video_url"]})
    with urllib.request.urlopen(req, timeout=300) as r:
        r.read()
    call(f"{G}/{page}/video_reels", {"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
                                     "description": item["caption"], "access_token": tok})
    return vid


def threads_post(text):
    tok, uid = ENV["THREADS_TOKEN"], ENV["THREADS_USER_ID"]
    cid = call(f"{T}/{uid}/threads", {"media_type": "TEXT", "text": text[:500], "access_token": tok})["id"]
    time.sleep(5)
    return call(f"{T}/{uid}/threads_publish", {"creation_id": cid, "access_token": tok})["id"]


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    due = []
    for f in sorted(glob.glob("queue/*.json")):
        item = json.load(open(f))
        if datetime.datetime.fromisoformat(item["publish_after"]) <= now:
            due.append((f, item))
    if not due:
        print("nothing due"); return 0
    f, item = due[0]  # one item per run
    result, failed = {}, False
    steps = []
    if ENV.get("META_PAGE_TOKEN") and item.get("video_url"):
        if ENV.get("IG_USER_ID"): steps.append(("instagram", lambda: ig_reel(item)))
        if ENV.get("FB_PAGE_ID"): steps.append(("facebook", lambda: fb_reel(item)))
    if ENV.get("THREADS_TOKEN") and ENV.get("THREADS_USER_ID"):
        for i, t in enumerate(item.get("threads", [])):
            steps.append((f"threads_{i}", lambda t=t: threads_post(t)))
    if not steps:
        print("no credentials configured yet; leaving queue untouched"); return 0
    for name, fn in steps:
        try:
            result[name] = fn(); print(name, "OK", result[name])
        except Exception as e:
            result[name] = f"ERROR: {e}"; failed = True; print(name, "FAILED", e)
    item["result"] = result
    item["posted_at"] = now.isoformat()
    os.makedirs("posted", exist_ok=True)
    json.dump(item, open(os.path.join("posted", os.path.basename(f)), "w"), ensure_ascii=False, indent=1)
    os.remove(f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

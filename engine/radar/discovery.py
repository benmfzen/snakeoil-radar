"""Discovery — pull recent videos for watchlist creator handles (the open door).

By-creator only: TikTok's topic/hashtag search is locked down (extractors break),
but a public profile is a fixed, addressable page yt-dlp can read reliably.
"""
import subprocess, json


def normalize_handle(h: str) -> str:
    h = h.strip().rstrip("/")
    if h.startswith("http"):
        return h
    h = h.lstrip("@")
    return f"https://www.tiktok.com/@{h}"


def fetch_recent(handle: str, n: int = 6, timeout: int = 180) -> dict:
    """Return {handle, account_id, videos:[...]} with per-video metrics, or {error}."""
    url = normalize_handle(handle)
    try:
        p = subprocess.run(
            ["yt-dlp", "-J", "--playlist-items", f"1:{n}", "--socket-timeout", "30", url],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"handle": handle, "error": "timeout", "videos": []}
    if p.returncode != 0 or not p.stdout.strip():
        last = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else f"rc={p.returncode}"
        return {"handle": handle, "error": last, "videos": []}
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        # yt-dlp can return a non-JSON body (rate-limit/HTML page) with rc=0
        return {"handle": handle, "error": "invalid_json_response", "videos": []}
    vids = []
    for e in (data.get("entries") or []):
        if not e:
            continue
        vids.append({
            "id": e.get("id"),
            "url": e.get("webpage_url") or e.get("url"),
            "title": (e.get("title") or "").strip(),
            "views": e.get("view_count"),
            "likes": e.get("like_count"),
            "comments": e.get("comment_count"),
            "reposts": e.get("repost_count"),
            "timestamp": e.get("timestamp"),
            "duration": e.get("duration"),
            "uploader": e.get("uploader") or data.get("title"),
        })
    return {"handle": handle, "account_id": data.get("id"), "videos": vids}

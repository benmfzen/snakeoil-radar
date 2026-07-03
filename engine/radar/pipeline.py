"""Pipeline CLI — watchlist -> discovery -> triage -> transcripts -> shortlist.json

This is the deterministic half of snakeoil-radar. It produces `shortlist.json`:
the hot, fresh videos WITH transcripts, ready for the agent-driven half
(claim extraction + evidence grounding + verdict -> befunde.json).

Usage:
  python3 -m radar.pipeline --config path/to/config.json [--out DIR]

Config (see config/config.example.json):
  {
    "watchlist": ["@handle1", "@handle2"],   // REQUIRED, user-supplied (onboarding)
    "videos_per_account": 6,
    "max_age_days": 14,
    "top_n": 8
  }
"""
import argparse, json, os, sys, time

from .discovery import fetch_recent
from .triage import rank
from .transcript import fetch_transcript


def run(config: dict, out_dir: str) -> dict:
    watchlist = [h for h in config.get("watchlist", []) if h and not h.startswith("_")]
    if not watchlist:
        sys.exit(
            "Watchlist ist leer. Trag in der Config unter \"watchlist\" die Creator-Handles ein,\n"
            "die du beobachten willst (Onboarding) — sie wird bewusst NICHT mitgeliefert."
        )
    now = time.time()
    n = config.get("videos_per_account", 6)

    print(f"[1/3] Discovery: {len(watchlist)} Accounts …", file=sys.stderr)
    accounts = []
    for h in watchlist:
        acc = fetch_recent(h, n=n)
        state = f"{len(acc['videos'])} Videos" if not acc.get("error") else f"FEHLER: {acc['error']}"
        print(f"   @{h.lstrip('@')}: {state}", file=sys.stderr)
        accounts.append(acc)

    print("[2/3] Triage: Heat-Ranking …", file=sys.stderr)
    feed = rank(accounts, now,
                max_age_days=config.get("max_age_days", 14),
                top_n=config.get("top_n", 8))

    print(f"[3/3] Transkripte für Top {len(feed)} …", file=sys.stderr)
    langs = config.get("caption_lang_preference", [])
    use_whisper = config.get("whisper_fallback", True)
    for v in feed:
        t = fetch_transcript(
            v["url"], lang_preference=langs,
            whisper_fallback=use_whisper,
            whisper_lang=config.get("whisper_lang", "de"),
            whisper_model=config.get("whisper_model", "small"),
        )
        v["transcript"] = t if t.get("ok") else None
        v["transcript_status"] = t.get("lang") if t.get("ok") else t.get("reason", "no_captions")
        print(f"   {v['id']}: {v['transcript_status']}", file=sys.stderr)

    result = {
        "generated_at": int(now),
        "config": {k: config.get(k) for k in ("videos_per_account", "max_age_days", "top_n")},
        "accounts": [
            {"handle": a["handle"], "baseline_views": a.get("account_baseline_views"),
             "error": a.get("error")} for a in accounts
        ],
        "shortlist": feed,
    }
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "shortlist.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"OK -> {path}  ({len(feed)} Videos, "
          f"{sum(1 for v in feed if v['transcript'])} mit Transkript)", file=sys.stderr)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    with open(a.config, encoding="utf-8") as f:
        cfg = json.load(f)
    run(cfg, a.out)


if __name__ == "__main__":
    main()

"""Triage — score & rank videos by HEAT before the expensive fact-check.

Heat = how many people are seeing this *right now*, relative to the creator's norm.
- velocity        = views / age_in_days       (a fresh viral spike beats an old evergreen)
- account_baseline= median views of the creator's recent posts  (relevance, not fakeable
                    like follower counts; replaces the follower signal yt-dlp won't give)
- rel_reach       = this video's views / baseline  (is THIS one over-performing for them?)
- engagement_rate = (likes+comments+reposts) / views
Only fresh + hot videos survive to transcript + fact-check.
"""
import statistics


def _age_days(ts, now):
    if not ts:
        return None
    return max((now - ts) / 86400.0, 0.02)


def score_account(acc: dict, now: float) -> dict:
    vids = [v for v in acc.get("videos", []) if v.get("views") is not None]
    if not vids:
        acc["account_baseline_views"] = None
        return acc
    baseline = statistics.median(v["views"] for v in vids)
    acc["account_baseline_views"] = baseline
    for v in vids:
        age = _age_days(v.get("timestamp"), now)
        v["age_days"] = round(age, 2) if age else None
        v["velocity"] = round(v["views"] / age) if age else None
        eng = (v.get("likes") or 0) + (v.get("comments") or 0) + (v.get("reposts") or 0)
        v["engagement_rate"] = round(eng / max(v["views"], 1), 4)
        v["rel_reach"] = round(v["views"] / baseline, 2) if baseline else None
        vel = v["velocity"] or 0
        v["heat"] = round(vel * (1 + v["engagement_rate"]) * (v["rel_reach"] or 1))
    acc["videos"] = sorted(vids, key=lambda x: x.get("heat") or 0, reverse=True)
    return acc


def rank(accounts: list, now: float, max_age_days: float = 30, top_n: int = 20) -> list:
    """Flatten scored accounts into one heat-ranked, freshness-filtered feed."""
    feed = []
    for acc in accounts:
        score_account(acc, now)
        for v in acc.get("videos", []):
            if v.get("age_days") is not None and v["age_days"] <= max_age_days:
                v["handle"] = acc["handle"]
                v["account_baseline_views"] = acc.get("account_baseline_views")
                feed.append(v)
    feed.sort(key=lambda x: x.get("heat") or 0, reverse=True)
    return feed[:top_n]

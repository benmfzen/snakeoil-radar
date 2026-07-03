"""Offline unit tests — no network, no yt-dlp needed.

Run from the engine/ directory:
    python3 -m tests.test_core      # plain
    python3 -m pytest tests         # if pytest is installed
"""
from radar.triage import score_account
from radar.render_report import _n, _ampel


def test_heat_and_baseline():
    now = 1_000_000.0
    acc = {"handle": "x", "videos": [
        {"views": 1000, "likes": 100, "comments": 10, "reposts": 0, "timestamp": now - 86400},
        {"views": 3000, "likes": 50, "comments": 5, "reposts": 5, "timestamp": now - 2 * 86400},
    ]}
    score_account(acc, now)
    assert acc["account_baseline_views"] == 2000          # median of 1000, 3000
    assert acc["videos"][0]["velocity"] > 0
    assert acc["videos"][0]["heat"] > 0


def test_missing_views_does_not_crash():
    now = 1_000_000.0
    acc = {"handle": "x", "videos": [{"views": None, "timestamp": now}]}
    score_account(acc, now)                                # None-views video is filtered out
    assert acc["account_baseline_views"] is None


def test_render_number_safe():
    assert _n(12345) == "12,345"
    assert _n(None) == "?"                                 # regression: ':,' on missing value crashed
    assert _n("?") == "?"


def test_ampel_normalises():
    assert _ampel("gruen") == "🟢"
    assert _ampel("grün") == "🟢"                          # umlaut variant still maps
    assert _ampel("UNVERIFIED") == "⚪"
    assert _ampel("bogus") == "⚪"                          # unknown -> ⚪, never an empty string


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for name, fn in tests:
        fn()
        print("ok", name)
    print(f"all {len(tests)} passed")

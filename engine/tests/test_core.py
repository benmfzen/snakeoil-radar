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


def _befund(ampel="rot", react_score=100, belege=None, **extra):
    b = {
        "video": {"id": "1", "url": "http://x", "title": "T", "handle": "h", "age_days": 1.0},
        "hitze": {"views": 100, "velocity": 50, "heat": 60, "baseline_views": 90},
        "claim": "c", "claim_paraphrase": "p",
        "misrat": {"ungenauigkeit": True, "auslassung": False, "rahmung": False},
        "ampel": ampel, "begruendung": "b",
        "belege": belege if belege is not None else [], "react_score": react_score,
        "status": "neu",
    }
    b.update(extra)
    return b


def _render(befunde):
    import json, os, tempfile
    from radar.render_report import render
    p = os.path.join(tempfile.mkdtemp(), "befunde.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"befunde": befunde, "uebersprungen": []}, fh)
    return render(p)


def test_render_sort_survives_null_react_score():
    # regression: explicit react_score:null next to numbers crashed sorted()
    md = _render([_befund(react_score=None, ampel="unverified"), _befund(react_score=500)])
    assert md.index("react_score: 500") < md.index("react_score: ?")   # null sorts last


def test_render_empty_belege_footer_matches_verdict():
    md = _render([_befund(ampel="unverified")])
    assert "→ UNVERIFIED" in md
    md = _render([_befund(ampel="rot")])                   # contract violation: rot without evidence
    assert "→ UNVERIFIED" not in md
    assert "Vertrag verletzt" in md


def test_render_gegenprobe_required_for_rot():
    md = _render([_befund(ampel="rot", gegenprobe="stärkstes Pro-Argument trägt nicht, weil X")])
    assert "Gegenprobe (bestanden):" in md
    md = _render([_befund(ampel="rot")])                   # rot without gegenprobe -> flagged
    assert "Gegenprobe:** ⚠️ fehlt" in md
    md = _render([_befund(ampel="gelb")])                  # non-rot verdicts don't need one
    assert "Gegenprobe" not in md


def test_render_evidenz_queries_audit_line():
    md = _render([_befund(ampel="unverified",
                          evidenz_queries=["detox diets toxin elimination", "juice cleanse RCT"])])
    assert "Suchanfragen: detox diets toxin elimination · juice cleanse RCT" in md
    md = _render([_befund(ampel="gelb")])                  # absent field renders nothing (old befunde)
    assert "Suchanfragen" not in md


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for name, fn in tests:
        fn()
        print("ok", name)
    print(f"all {len(tests)} passed")

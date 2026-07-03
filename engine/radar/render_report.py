"""Render befunde.json -> report.md (human-readable, react_score-sorted)."""
import json, sys

AMPEL = {"rot": "🔴", "gelb": "🟡", "gruen": "🟢", "unverified": "⚪"}


def render(befunde_path: str) -> str:
    d = json.load(open(befunde_path, encoding="utf-8"))
    b = sorted(d["befunde"], key=lambda x: x.get("react_score", 0), reverse=True)
    out = ["# snakeoil-radar — Befund-Report", ""]
    out.append(f"*{len(b)} Befunde · nach react_score sortiert (Hitze × Schwere)*")
    out.append("")
    for i, f in enumerate(b, 1):
        v, h = f["video"], f["hitze"]
        out.append(f"## {i}. {AMPEL.get(f['ampel'],'')} {f['claim_paraphrase']}")
        out.append(f"**@{v['handle']}** · [{v['title'][:70]}]({v['url']})  ")
        out.append(f"👁 {h['views']:,} Views · ⚡ {h['velocity']:,}/Tag · 🌡 heat {h['heat']:,} "
                   f"· Baseline {h.get('baseline_views','?'):,} · {v['age_days']}d alt  ")
        out.append(f"**react_score: {f['react_score']:,}**")
        out.append("")
        out.append(f"> „{f['claim']}\"")
        out.append("")
        m = f["misrat"]
        flags = [k for k, val in m.items() if val]
        out.append(f"**Verdikt {AMPEL.get(f['ampel'],'')} {f['ampel'].upper()}** "
                   f"{'· MisRAT: '+', '.join(flags) if flags else '· keine MisRAT-Flags'}  ")
        out.append(f"{f['begruendung']}")
        out.append("")
        if f["belege"]:
            out.append("**Belege:**")
            for q in f["belege"]:
                out.append(f"- [{q['jahr']}] [{q['titel']}]({q['url']}) "
                           f"*({q['typ']})* — {q['kernaussage']}")
        else:
            out.append("**Belege:** ⚪ keine belastbare Evidenz gefunden → UNVERIFIED")
        out.append("")
        out.append("---")
        out.append("")
    if d.get("uebersprungen"):
        out.append("### Übersprungen")
        for s in d["uebersprungen"]:
            out.append(f"- `{s['id']}` — {s['grund']}")
    return "\n".join(out)


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "out/befunde.json"
    md = render(p)
    outp = p.rsplit("/", 1)[0] + "/report.md" if "/" in p else "report.md"
    open(outp, "w", encoding="utf-8").write(md)
    print(f"OK -> {outp}")

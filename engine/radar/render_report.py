"""Render befunde.json -> report.md (human-readable, react_score-sorted)."""
import json, sys

AMPEL = {"rot": "🔴", "gelb": "🟡", "gruen": "🟢", "unverified": "⚪"}


def _n(x):
    """Thousands-separated int, but never crash on a missing/non-numeric value."""
    return f"{x:,}" if isinstance(x, (int, float)) and not isinstance(x, bool) else str(x if x is not None else "?")


def _ampel_key(v) -> str:
    """Normalise the verdict key so 'grün', 'GRÜN', 'UNVERIFIED' etc. still map."""
    return str(v).strip().lower().replace("ü", "ue").replace("ä", "ae").replace("ö", "oe")


def _ampel(v):
    return AMPEL.get(_ampel_key(v), "⚪")


def render(befunde_path: str) -> str:
    d = json.load(open(befunde_path, encoding="utf-8"))
    # `or 0`, not a .get default: an explicit react_score:null must not break the sort
    b = sorted(d["befunde"], key=lambda x: x.get("react_score") or 0, reverse=True)
    out = ["# snakeoil-radar — Befund-Report", ""]
    out.append(f"*{len(b)} Befunde · nach react_score sortiert (Hitze × Schwere)*")
    out.append("")
    for i, f in enumerate(b, 1):
        v, h = f["video"], f["hitze"]
        out.append(f"## {i}. {_ampel(f['ampel'])} {f['claim_paraphrase']}")
        out.append(f"**@{v['handle']}** · [{v['title'][:70]}]({v['url']})  ")
        out.append(f"👁 {_n(h.get('views'))} Views · ⚡ {_n(h.get('velocity'))}/Tag · 🌡 heat {_n(h.get('heat'))} "
                   f"· Baseline {_n(h.get('baseline_views'))} · {v.get('age_days','?')}d alt  ")
        out.append(f"**react_score: {_n(f.get('react_score'))}**")
        out.append("")
        out.append(f"> „{f['claim']}\"")
        out.append("")
        m = f["misrat"]
        flags = [k for k, val in m.items() if val]
        out.append(f"**Verdikt {_ampel(f['ampel'])} {str(f['ampel']).upper()}** "
                   f"{'· MisRAT: '+', '.join(flags) if flags else '· keine MisRAT-Flags'}  ")
        out.append(f"{f['begruendung']}")
        out.append("")
        if _ampel_key(f["ampel"]) == "rot":
            if f.get("gegenprobe"):
                out.append(f"**Gegenprobe (bestanden):** {f['gegenprobe']}")
            else:
                out.append("**Gegenprobe:** ⚠️ fehlt — ein Rot ohne Gegenprobe ist "
                           "vertragswidrig, Verdikt prüfen")
            out.append("")
        if f["belege"]:
            out.append("**Belege:**")
            for q in f["belege"]:
                out.append(f"- [{q['jahr']}] [{q['titel']}]({q['url']}) "
                           f"*({q['typ']})* — {q['kernaussage']}")
        elif _ampel_key(f["ampel"]) == "unverified":
            out.append("**Belege:** ⚪ keine belastbare Evidenz gefunden → UNVERIFIED")
        else:
            # contract violation: every non-unverified verdict needs evidence
            out.append("**Belege:** ⚠️ keine angegeben — dieses Verdikt braucht Belege "
                       "(Vertrag verletzt, Befund prüfen)")
        if f.get("evidenz_queries"):
            out.append("")
            out.append(f"*Suchanfragen: {' · '.join(f['evidenz_queries'])}*")
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

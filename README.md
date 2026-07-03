# 🐍 snakeoil-radar

![license](https://img.shields.io/badge/license-MIT-green.svg)
![python](https://img.shields.io/badge/python-3.8+-blue.svg)
![api keys](https://img.shields.io/badge/API%20keys-none-brightgreen.svg)
![cost](https://img.shields.io/badge/cost-free-brightgreen.svg)
![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-8A2BE2.svg)

**A reaction radar for viral health misinformation — as a Claude Code skill.**

Watches a self-maintained **watchlist** of TikTok creator handles, ranks their fresh
videos by heat (view velocity × engagement × account baseline), pulls transcripts, and
checks the concrete factual claims against **real PubMed literature**. A traffic-light
verdict (🟢🟡🔴) is only issued with a retrievable source (PMID + link); otherwise the
claim is marked `UNVERIFIED`.

Free to run: `yt-dlp` + `curl` + PubMed E-utilities. No API keys, no subscriptions.

## Example output

One finding from `out/report.md` (handle anonymized):

```markdown
## 🟡 Baking soda removes "99% of all pesticides" from produce
@example_creator · "Removing pesticides from fruit?"
👁 4,013 views · ⚡ 33,442/day · 🌡 heat 38,743 · baseline 3,580 · 0.1d old
react_score: 58,114

> "Studies show you can remove up to 99% of all pesticides from your fruit and
>  vegetables with baking soda — sodium bicarbonate even works better than
>  washing with water or vinegar."

Verdict 🟡 YELLOW · MisRAT: inaccuracy, dangerous omission

True core, dangerously truncated. The study this echoes (Yang et al. 2017) found a
baking-soda solution removes SURFACE pesticides better than tap water or bleach — but
it took 12–15 min of soaking, and 4–20% of the pesticide had penetrated into the fruit
and could not be washed off at all. "99% of all pesticides" overstates it; systemic
residues remain. "Better than vinegar" was never even tested.

Evidence:
- [2017] Effectiveness of Commercial and Homemade Washing Agents in Removing Pesticide
  Residues on and in Apples — Evaluation Study, PMID 29067814
  → Sodium bicarbonate removes surface pesticides best (vs. water/bleach); needs
    12–15 min; 4–20% penetrate the fruit and are not washable.
```

Every verdict carries a PMID + link. A claim with no retrievable evidence comes back
`UNVERIFIED` — never guessed.

## Quickstart

```bash
# 1. Prerequisites (one-time)
pip install -r requirements.txt       # yt-dlp; curl + python3 ship with macOS/Linux
cd engine && python3 -m radar.setup   # optional: pulls local Whisper (free, no key)
python3 -m tests.test_core            # optional: run the offline test suite

# 2. Create your config — the watchlist ships EMPTY; you add your own handles
cp config/config.example.json config/config.json
#    "watchlist": ["@handle1", "@handle2", ...]

# 3. Pipeline (deterministic): discovery -> triage -> transcripts
cd engine && python3 -m radar.pipeline --config ../config/config.json --out ../out

# 4. Fact-check (agentic): run the skill in Claude Code —
#    it reads out/shortlist.json, extracts claims, fetches PubMed evidence,
#    and writes out/befunde.json + out/report.md
```

The full process and verdict rules live in [SKILL.md](SKILL.md). Topic presets
(vocabulary + search terms) live in [presets/](presets/) — a German nutrition preset is
included as an example; the radar itself is topic-agnostic.

## Architecture

```
config/config.json      your watchlist (onboarding, never shipped)
engine/radar/
  discovery.py          per-handle profile feeds (yt-dlp)
  triage.py             heat = velocity × (1+engagement) × rel_reach; freshness filter
  transcript.py         TikTok captions -> text; local Whisper fallback when absent
  setup.py              pulls faster-whisper + model (one-time, on-device, free)
  evidence.py           PubMed E-utilities: prefers meta-analyses/reviews, fail-closed
  pipeline.py           CLI: everything up to shortlist.json
  render_report.py      befunde.json -> report.md (deterministic, always in sync)
SKILL.md                the actual "code": the process the agent follows
presets/                domain vocabulary (optional)
out/                    shortlist.json -> befunde.json + report.md
```

## Design decisions

- **By-creator, not by-topic.** TikTok's topic search is locked down for free tools
  (`tiktok:tag` is broken); profile feeds are stable. The watchlist is the user's
  editorial choice — and therefore not part of this repo.
- **Baseline instead of follower count.** The platform doesn't expose follower counts
  cleanly and they can be bought. Median views of recent posts measure actual reach.
- **Fail-closed fact-checking.** Only what the evidence search actually returned gets
  cited. `UNVERIFIED` beats a hallucinated study.
- **Adversarial check before red.** A wrong red verdict is the most expensive mistake —
  it becomes public reaction content. So every red requires a documented counter-check
  (`gegenprobe`): defend the claim with the same evidence first; if the defense holds
  even partially, it's yellow. Search queries are logged per finding (`evidenz_queries`),
  so an `UNVERIFIED` shows *how* it was searched, not just that nothing was found.
- **One platform done well over three done shakily.** Viral clips are almost always
  cross-posted; covering TikTok catches the IG/Shorts mirrors by content.

## Limitations

Very fresh videos (<1 day) often have no captions yet — local Whisper transcribes them
on-device (free), otherwise the next run picks them up. Brand-new accounts only appear
once they're added to the watchlist. PubMed covers biomedicine; for other domains
(finance, etc.) swap the evidence module for a suitable source — the rest of the process
stays identical.

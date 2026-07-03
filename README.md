# 🐍 snakeoil-radar

**A reaction radar for viral health misinformation — as a Claude Code skill.**

Watches a self-maintained **watchlist** of TikTok creator handles, ranks their fresh
videos by heat (view velocity × engagement × account baseline), pulls transcripts, and
checks the concrete factual claims against **real PubMed literature**. A traffic-light
verdict (🟢🟡🔴) is only issued with a retrievable source (PMID + link); otherwise the
claim is marked `UNVERIFIED`.

Free to run: `yt-dlp` + `curl` + PubMed E-utilities. No API keys, no subscriptions.

## Quickstart

```bash
# 1. Prerequisites (one-time)
pip install -U yt-dlp        # curl + python3 ship with macOS/Linux
cd engine && python3 -m radar.setup   # optional: pulls local Whisper (free, no key)

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
- **One platform done well over three done shakily.** Viral clips are almost always
  cross-posted; covering TikTok catches the IG/Shorts mirrors by content.

## Limitations

Very fresh videos (<1 day) often have no captions yet — local Whisper transcribes them
on-device (free), otherwise the next run picks them up. Brand-new accounts only appear
once they're added to the watchlist. PubMed covers biomedicine; for other domains
(finance, etc.) swap the evidence module for a suitable source — the rest of the process
stays identical.

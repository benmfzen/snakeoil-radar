# 🐍 snakeoil-radar

**Ein Reaktions-Radar für viralen Gesundheits-Bullshit — als Claude-Code-Skill, nicht als App.**

Spürt „Snake Oil" auf: reichweitenstarke Videos mit Falschaussagen, bevor alle anderen
reagiert haben — und hält jede Behauptung gegen echte Studien, statt gegen Bauchgefühl.

Beobachtet eine selbst gepflegte **Watchlist** von TikTok-Creator-Handles, rankt deren
frische Videos nach Hitze (Views-Velocity × Engagement × Account-Baseline), zieht
Transkripte und prüft die konkreten Tatsachenbehauptungen gegen **echte PubMed-Literatur**
— Ampel-Verdikt (🟢🟡🔴) nur mit abrufbarer Quelle (PMID + Link), sonst `UNVERIFIED`.

Kostenlos: `yt-dlp` + `curl` + PubMed E-utilities. Keine API-Keys, keine Abos.

## Warum Skill statt App?

Plattform-Scraping bricht ständig — TikTok tauscht die Schlösser, Tools sterben.
Eine App darauf ist an Tag 1 veraltet und danach ein Pflegefall. Ein Skill ist ein
**Prozess**: die deterministischen Teile sind dünne Scripts, die man in Minuten an
neue Community-Releases anpasst; das Urteil fällt der Agent nach festen Ehrlichkeits-
Regeln. Wächst mit, statt zu verrotten.

## Quickstart

```bash
# 1. Voraussetzungen (einmalig)
pip install -U yt-dlp        # curl + python3 sind auf macOS/Linux schon da
cd engine && python3 -m radar.setup   # optional: zieht lokales Whisper (gratis, kein Key)

# 2. Config anlegen — Watchlist ist bewusst LEER, du trägst deine Handles selbst ein
cp config/config.example.json config/config.json
#    "watchlist": ["@handle1", "@handle2", ...]

# 3. Pipeline (deterministisch): Discovery -> Triage -> Transkripte
cd engine && python3 -m radar.pipeline --config ../config/config.json --out ../out

# 4. Faktencheck (agentisch): In Claude Code den Skill laufen lassen —
#    er liest out/shortlist.json, extrahiert Claims, holt PubMed-Belege
#    und schreibt out/befunde.json + out/report.md
```

Der komplette Prozess inkl. Verdikt-Regeln steht in [SKILL.md](SKILL.md).
Themen-Presets (Vokabular + Suchbegriffe) in [presets/](presets/) — Ernährung (DE)
liegt als Beispiel bei; das Radar selbst ist themen-agnostisch.

## Architektur

```
config/config.json      deine Watchlist (Onboarding, nie mitgeliefert)
engine/radar/
  discovery.py          Profil-Feeds je Handle (yt-dlp) — die "offene Tür"
  triage.py             Heat = velocity × (1+engagement) × rel_reach; Frische-Filter
  transcript.py         TikTok-Captions -> Text; lokales Whisper-Fallback ohne Captions
  setup.py              zieht faster-whisper + Modell (einmalig, on-device, gratis)
  evidence.py           PubMed E-utilities: Meta-Analysen/Reviews bevorzugt, fail-closed
  pipeline.py           CLI: alles bis shortlist.json
SKILL.md                der eigentliche "Code": der Prozess für den Agenten
presets/                Domänen-Vokabular (optional)
out/                    shortlist.json -> befunde.json + report.md
```

## Design-Entscheidungen (ehrlich)

- **By-creator statt by-topic:** TikToks Themensuche ist für freie Tools verriegelt
  (`tiktok:tag` broken), Profil-Feeds sind stabil. Die Watchlist ist eine redaktionelle
  Entscheidung des Nutzers — und genau deshalb nicht Teil des Repos.
- **Baseline statt Follower:** Follower-Zahlen liefert die Plattform nicht sauber und
  sie sind kaufbar. Median-Views der letzten Posts messen echte aktuelle Reichweite.
- **Fail-closed Faktencheck:** zitiert wird nur, was die Evidenz-Suche wirklich
  zurückgab. Lieber `UNVERIFIED` als eine halluzinierte Studie.
- **Eine Plattform sauber statt drei wackelig:** virale Clips sind fast immer
  cross-gepostet; TikTok-Abdeckung fängt die IG/Shorts-Spiegel inhaltlich mit.

## Grenzen

Sehr frische Videos (<1 Tag) haben oft noch keine Captions — lokales Whisper
transkribiert sie dann on-device (gratis), sonst greift der nächste Lauf.
Völlig neue Accounts erscheinen erst, wenn sie auf die Watchlist kommen.
PubMed deckt Biomedizin ab — für andere Domänen (Finanzen etc.) das Evidenz-Modul
gegen eine passende Quelle tauschen (der Rest des Prozesses bleibt identisch).

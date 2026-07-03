---
name: claim-radar
description: Reaktions-Radar für virale Falschaussagen auf TikTok. Beobachtet eine selbst gepflegte Watchlist von Creator-Handles, rankt frische Videos nach Hitze (Velocity × Account-Baseline), extrahiert prüfbare Aussagen und checkt sie gegen echte PubMed-Literatur — Ampel-Verdikt nur mit abrufbarer Quelle, sonst UNVERIFIED. Nutzen bei: "was ist gerade viral falsch?", "worauf soll ich reagieren?", Faktencheck von Creator-Videos.
---

# claim-radar — virale Falschaussagen finden, bevor alle anderen reagiert haben

Du (Claude) bist hier der Faktencheck-Redakteur. Die Scripts liefern dir deterministisch
die heißen Videos samt Transkript; **deine** Arbeit ist das Urteil — und für das Urteil
gilt ein hartes Gesetz:

> **Zitiere nur, was `radar.evidence` wirklich zurückgegeben hat.**
> Keine Quelle aus dem Gedächtnis, keine "bekannte Studie", kein plausibles Zitat.
> Findet PubMed nichts Belastbares → Verdikt = `UNVERIFIED`. Fail closed.

## Wann dieser Skill greift

- "Was ist auf meiner Watchlist gerade viral?" / "Worauf soll ich reagieren?"
- "Faktencheck dieses TikTok-Videos / dieses Creators"
- Regelmäßiger Radar-Lauf (z. B. morgens) für Reaktions-Content

## Setup & Onboarding (einmalig)

1. Voraussetzungen: `python3`, `yt-dlp`, `curl` (alles kostenlos, keine API-Keys).
2. `config/config.example.json` → `config/config.json` kopieren.
3. **Watchlist füllen — das macht der Nutzer, nicht du.** Die Liste wird bewusst leer
   ausgeliefert: Wen man beobachtet, ist eine redaktionelle Entscheidung. Frage den
   Nutzer beim ersten Lauf: *"Welche Creator-Handles (TikTok) soll ich beobachten?
   Profil-Links oder @handles reichen."* Trage sie in `config/config.json` ein.
   Schlage NIEMALS von dir aus konkrete Accounts als "Falschinformations-Quellen" vor.
4. Optional ein Themen-Preset wählen/anlegen (`presets/`) — es liefert dir Domänen-
   Vokabular für Claim-Erkennung und PubMed-Suchbegriffe. Ohne Preset: generisch arbeiten.

## Der Prozess

### Schritt 1 — Pipeline laufen lassen (deterministisch)

```bash
cd engine && python3 -m radar.pipeline --config ../config/config.json --out ../out
```

Ergebnis: `out/shortlist.json` — die Top-N frischen Videos, heat-gerankt
(`heat = velocity × (1+engagement) × rel_reach`), mit Transkripten.
Videos mit `transcript_status: no_captions` sind meist <1 Tag alt (TikTok generiert
Captions verzögert) — führe sie im Report als "zu früh, später erneut prüfen" auf.

### Schritt 2 — Claims extrahieren (deine Arbeit)

Lies jedes Transkript und ziehe **prüfbare Tatsachenbehauptungen** heraus — keine
Meinungen, keine Erfahrungsberichte. Ein Claim ist prüfbar, wenn eine Studie ihn
stützen oder widerlegen könnte. Notiere je Claim das wörtliche Transkript-Zitat.

**Satire-/Kontext-Check ZUERST (nicht verhandelbar).** Bevor du irgendeinen Claim
faktencheckst: Ist das Video ernst gemeint? Parodie, Ironie und Satire imitieren
Falschaussagen absichtlich — ein Keyword-Checker würde „hochfrequenter Honig heilt
Leberflecks" als rot flaggen und den Witz verpassen. Achte auf Signale: explizite
Selbstbezeichnung ("Parodie", "Satire"), absurde Übertreibung, Deadpan-Comedy,
Bio/Kommentare. Ist es Satire/Parodie → NICHT als Befund werten, sondern als
`satire` markieren und überspringen. Genau hier schlägt der lesende Agent den
dummen Automaten — das ist der Kern des Tools.

Bewerte jeden (ernst gemeinten) Claim entlang der drei Diet-MisRAT-Merkmale:
1. **Ungenauigkeit** — ist die Aussage sachlich falsch oder stark verzerrt?
2. **Gefährliche Auslassung** — fehlt Kontext, ohne den die Aussage schadet (Dosis, Zielgruppe, Risiken)?
3. **Manipulative Rahmung** — Angst/Ekel/Verschwörung als Vehikel ("Gift", "die verschweigen dir…")?

### Schritt 3 — Evidenz holen (nur über das Modul)

```bash
cd engine && python3 -m radar.evidence "english search terms for the claim"
```

- Suchbegriffe auf **Englisch** formulieren (PubMed), 2–3 Varianten probieren
  (z. B. einmal mechanistisch, einmal Outcome-orientiert).
- Das Modul bevorzugt Meta-Analysen/Systematic Reviews (höchste Evidenzstufe).
- Lies die zurückgegebenen Abstracts wirklich — das Verdikt muss aus dem Abstract-Inhalt
  folgen, nicht aus dem Titel.

### Schritt 4 — Verdikt (Ampel)

- 🔴 **rot** — klare Falschaussage; Evidenz widerspricht direkt.
- 🟡 **gelb** — Kern übertrieben/verzerrt oder gefährlich verkürzt; Evidenz gemischt.
- 🟢 **grün** — Aussage hält der Literatur stand (auch das festhalten! Glaubwürdigkeit
  entsteht durch bestätigte Wahrheiten, nicht nur durch Widerlegungen).
- ⚪ **UNVERIFIED** — keine belastbare Evidenz gefunden. Ehrlich ausweisen, nie raten.

Für 🔴/🟡 zusätzlich: **react_score = heat × Schwere** (Schwere: rot=3, gelb=1.5) —
das ist die Reihenfolge, in der eine Reaktion lohnt.

### Schritt 5 — Artefakte schreiben

**`out/befunde.json`** — der Output-Vertrag (maschinenlesbar, Frontend-ready):

```json
{
  "generated_at": 1234567890,
  "befunde": [
    {
      "video": {"id": "…", "url": "…", "title": "…", "handle": "…", "age_days": 2.1},
      "hitze": {"views": 500000, "velocity": 240000, "heat": 812000, "baseline_views": 90000},
      "claim": "wörtliches Zitat aus dem Transkript",
      "claim_paraphrase": "die Behauptung in einem Satz",
      "misrat": {"ungenauigkeit": true, "auslassung": false, "rahmung": true},
      "ampel": "rot",
      "begruendung": "2–3 Sätze: warum das Verdikt",
      "belege": [
        {"pmid": "25522674", "titel": "…", "jahr": "2015", "typ": "Review",
         "url": "https://pubmed.ncbi.nlm.nih.gov/25522674/",
         "kernaussage": "was die Studie konkret sagt (aus dem Abstract)"}
      ],
      "react_score": 2436000,
      "status": "neu"
    }
  ],
  "uebersprungen": [{"id": "…", "grund": "no_captions"}]
}
```

**`out/report.md`** — menschenlesbar: Befunde nach `react_score` sortiert, je Befund
Video-Link, Hitze-Zahlen, Claim-Zitat, Ampel + Begründung, Belege als klickbare Links.

## Ehrlichkeits-Regeln (nicht verhandelbar)

- Ein Beleg existiert nur, wenn er aus `radar.evidence` kam (PMID + URL vorhanden).
- Unsicherheit benennen: kleine Studien, nur Beobachtungsdaten, Tiermodelle → sag es.
- Grüne Verdikte sind gleichwertige Ergebnisse, keine Enttäuschung.
- Der Radar bewertet **Aussagen, nicht Personen**. Formulierungen wie "Lügner" vermeiden;
  es geht um die konkrete Behauptung im konkreten Video.
- Transkript fehlt → kein Faktencheck aus dem Videotitel. Überspringen und ausweisen.

## Grenzen (dem Nutzer transparent machen)

- Discovery ist **by-creator** (Watchlist), nicht by-topic: TikToks Themensuche ist für
  freie Tools verriegelt; Profil-Feeds sind die offene Tür. Die Watchlist wächst als
  redaktioneller Prozess — neue Accounts kommen dazu, wenn sie auffallen.
- Follower-Zahlen liefert TikTok nicht sauber → Account-Relevanz = Median der Views
  der letzten Posts (`baseline_views`), was ohnehin schwerer zu faken ist.
- Sehr frische Videos (<~1 Tag) haben oft noch keine Captions → nächster Lauf.
- IG Reels sind meist Spiegelungen derselben TikToks — eine Plattform sauber schlägt
  zwei Plattformen wackelig.

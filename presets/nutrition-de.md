# Preset: Ernährung (DE)

Domänen-Vokabular für claim-radar im deutschsprachigen Ernährungs-/Abnehm-Space.
Ein Preset ändert nichts am Prozess — es macht dich (Claude) schneller und präziser
bei Schritt 2 (Claim-Erkennung) und Schritt 3 (PubMed-Suchbegriffe).

## Typische prüfbare Claim-Familien

| Claim-Familie | Typische Formulierung | PubMed-Suchansatz (EN) |
|---|---|---|
| Süßstoffe | "Süßstoff ist Gift / macht dick / Insulin" | non-nutritive sweeteners weight RCT; aspartame safety review |
| Detox/Entgiften | "entgiftet deinen Körper", Saftkuren | detox diets toxin elimination evidence |
| Abendliche Carbs | "Kohlenhydrate nach 18 Uhr machen dick" | meal timing carbohydrate evening weight |
| Frühstück | "wichtigste Mahlzeit", "Stoffwechsel ankurbeln" | breakfast skipping weight RCT |
| Zucker-Sucht | "Zucker so süchtig wie Kokain" | sugar addiction evidence review human |
| Superfoods | "X heilt/verhindert Krankheit Y" | [food] [outcome] systematic review |
| Stoffwechsel-Mythen | "Stoffwechsel kaputt", "Hungermodus" | metabolic adaptation weight loss; starvation mode |
| Hormon-Framing | "Cortisol-Bauch", "Insulin blockiert Fettabbau" | insulin model obesity review; cortisol abdominal fat |
| Wundermittel | ACV, Zitronenwasser, Kollagen, Fatburner | apple cider vinegar weight meta-analysis etc. |
| Milch/Gluten-Angst | "Milch verschleimt", "Gluten entzündet alle" | milk mucus evidence; non-celiac gluten sensitivity |

## Red Flags für manipulative Rahmung (Diet-MisRAT Merkmal 3)

"Gift", "Chemie", "die Industrie verschweigt", "dein Arzt sagt dir nicht", "in 7 Tagen",
"nie wieder", Angst-Thumbnails, Vorher/Nachher ohne Zeitraum, "Studien zeigen" ohne Quelle.

## Kalibrierung

- Dosis & Zielgruppe immer mitdenken: eine Aussage kann für Gesunde falsch und für
  eine Nischengruppe (z. B. Phenylketonurie bei Aspartam) korrekt sein → gelb + Kontext.
- RCT/Meta-Analyse > Beobachtungsstudie > Tiermodell > Mechanismus-Spekulation.
- WHO/EFSA-Positionen einordnen, nicht als Totschlag-Argument (Beispiel Süßstoffe 2023:
  Beobachtungsdaten mit wahrscheinlicher reverser Kausalität — differenziert bleiben).

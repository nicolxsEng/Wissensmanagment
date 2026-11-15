# Kodierung der Fragetexte (AP06/AP09)

Leitfaden: [docs/kodierleitfaden_fragen.md](../../docs/kodierleitfaden_fragen.md)

## App starten

Im Repo-Ordner (einmalig vorher `uv sync`):

```bash
uv run marimo run notebooks/kodier_app.py
```

Die App öffnet sich im Browser. Oben Person und Bogen wählen. Jede Einordnung (G/U/S) wird sofort gespeichert; die App springt zur nächsten offenen Frage. Unterbrechen und später weitermachen ist jederzeit möglich. Die Rohdaten braucht man dafür nicht, die App liest nur `ansicht.parquet` (Titel und Text, ohne Jahr, Tags und Score).

## Ablauf

1. **Kalibrierung:** Beide kodieren getrennt ihren Bogen `kalibrierung_A.csv` bzw. `kalibrierung_B.csv` (dieselben 30 Fragen, andere Reihenfolge). Danach gemeinsam vergleichen und den Leitfaden schärfen.
2. **Kodierung:** Nicolas kodiert `kodierer_A.csv` (600 Fragen), Gentian `kodierer_B.csv` (150 Fragen, alle auch bei Nicolas). Keine Absprache während der Kodierung.
3. Danach berechnet AP09 Cohens Kappa und erzeugt die Konsensliste für die 150 Doppelten.

## Nicht öffnen

- `stichprobe_intern.csv` enthält Jahr und Link je Code. Es ist nur für die Auswertung gedacht.
- `split.csv` zeigt, welche Fragen doppelt kodiert werden (Testmenge).

Die Bögen sind CSV mit Semikolon. Beim Kodieren immer die App benutzen, nicht die CSV direkt bearbeiten.

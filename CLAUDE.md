# CLAUDE.md – Forschungsprojekt „Sichtbares Wissen auf Stack Overflow vor und nach ChatGPT“

Masterkurs „Studien zu Wissen in Organisationen“ (TH Nürnberg, WS 2026/27). Beschreibende Sekundärdatenanalyse: Stack-Overflow-Fragen aus dem Oktober jedes Jahres 2008–2026, Vergleich Grundlagen- gegen Umgebungsfragen, Bezug zu Leonardi (2014).

**Maßgeblich ist `plan.md`.** Dort stehen Definitionen (Abschnitt 5), Arbeitspakete (Abschnitt 6), Diagramm- und Tabellenkatalog (Abschnitte 7–8). Bei Widerspruch zwischen Code und Plan: nachfragen, nicht raten.

## Befehle

```bash
uv sync                              # Basis-Abhängigkeiten
uv sync --group topics --group ml    # BERTopic, SetFit (erst ab AP10/AP11)
make help                            # alle Pipeline-Schritte
uv run pytest                        # Tests
uv run ruff check . && uv run ruff format .
uv run marimo edit notebooks/<datei>.py
```

## Struktur

- `src/sov/` Paket mit der Logik (`config.py` = alle Konstanten und Pfade, nie Zahlen im Code verstreuen)
- `scripts/NN_*.py` dünne Einstiegspunkte, die Funktionen aus `src/sov` aufrufen; eine Nummer je AP
- `src/sov/figures/Fxx_*.py` je Abbildung eine Funktion `make()`; speichern nur über `sov.plotting.style.save_fig`
- `data/` und `results/models/` werden nicht versioniert; Rohdaten liegen in `../Datentest` (Pfad: `config.RAW_DIR`)

## Harte Regeln

1. **Rohdaten nur lesen.** Nichts in `../Datentest` ändern, verschieben oder löschen.
2. **API-Keys nie ausgeben**, nie in Dateien außerhalb von `.env` schreiben, nie in Logs. Stack-Exchange-Key liegt in `../Datentest/.env` und wird über `../Datentest/scripts/se_api.py` geladen. 
3. **Menschliche Kodierung bleibt menschlich.** Dateien `coding/**/kodierer_*.csv`, `coding/**/kalibrierung_*.csv`, `coding/tags/uebung_10.csv`, `coding/topics/themen_benennen*.csv`, `coding/topics/themen_check_*.csv`, `coding/**/konsens_*.csv`, `coding/**/*_check_*.csv` und `coding/checks/*` füllen nur die Autor:innen aus. Claude Code trägt dort keine Labels ein und schlägt keine Kategorien für einzelne Tags oder Fragen vor.
4. **Blindheit schützen.** Kodierbögen für Tags enthalten keine Fragezahlen, Jahre oder Trends. Kodieransichten für Fragen zeigen weder Jahr noch Tags noch Score. Beim Erstellen solcher Dateien keine Zahlen zu einzelnen Tags im Chat ausgeben, solange AP05 nicht abgeschlossen ist.
5. **Testmenge gesperrt.** Die 150 Konsensfragen (`coding/questions/split.csv`, `split == "test"`) nie für Hypothesensätze, Training oder Einstellungen verwenden. Jeder Kandidat wird darauf genau einmal ausgewertet.
6. **Nur lokale Modelle.** Keine Cloud-Sprachmodelle oder -APIs (OpenAI, Anthropic, Google usw.) für Klassifikation, Themen oder Themennamen; Fragetexte verlassen den Rechner nicht. Erlaubt: scikit-learn, SetFit, Zero-Shot-Modelle über `transformers`, BERTopic/sentence-transformers. Modellnamen stehen in `config.py`; beim ersten Lauf die Revision (Commit-Hash) in `config.MODEL_REVISIONS` eintragen und je Lauf eine Modellkarte in `results/` schreiben (Modell, Revision, Paketversionen, Seed, Einstellungen, Laufzeit). Rechnen auf `mps`, falls verfügbar; Läufe über 10 Minuten vorher ankündigen und im Hintergrund starten.
7. **Zufall nur mit `config.SEED`** (bzw. davon abgeleiteten Seeds). Jede Stichprobe muss bei erneutem Lauf identisch sein.
8. **Keine Ursachenbehauptungen** in generierten Texten (`results/ergebnisse.md` usw.): „verändert sich“, „weicht vom Trend ab“, nicht „wegen ChatGPT“.

## Konventionen

- Code und Bezeichner Englisch, Kommentare, Docstrings, Logs und Berichte Deutsch.
- Datenverarbeitung mit **Polars** (lazy, wo sinnvoll); pandas nur an Schnittstellen zu statsmodels/sklearn.
- Jede Kennzahl ist eine reine Funktion mit Test in `tests/` (kleine Hand-Beispiele, deren Ergebnis von Hand ausgerechnet ist).
- Ergebnisse von Skripten als CSV in `data/processed/` (lange Form: `year, population, metric, value`), Berichte als Markdown in `results/`.
- Neue methodische Entscheidung → Eintrag in `docs/entscheidungen.md` (Datum, Entscheidung, Begründung, Alternative).
- Nach Abschluss eines AP: Akzeptanzkriterien aus `plan.md` prüfen, Status in `plan.md` Abschnitt 15 abhaken (mit Datum), kurz berichten, was nicht geprüft wurde.

## Abbildungen

- Immer `from sov.plotting.style import apply_style, save_fig, COLORS, add_chatgpt_marker, de_formatter`.
- Farben nach Bedeutung (`COLORS["grundlagen"]`, `COLORS["umgebung"]`, `COLORS["sonstige"]`, `COLORS["gesamt"]`, `COLORS["trend"]`), nie Standardfarben von matplotlib.
- Kein Titel im Bild, Achsen auf Deutsch, Dezimalkomma, eine y-Achse je Feld, Linien direkt beschriften wenn ≤ 4.
- Jahre 2025/2026 als Bestätigung kennzeichnen (hohle Marker, `style.mark_confirmation_years`).
- Nach dem Erzeugen die PNG ansehen (Read-Tool) und auf überlappende Beschriftungen prüfen.

## Bekannte Datenbesonderheiten

- **Tags immer zusammengeführt (D15):** `sov.io.load_questions()` bildet Synonyme standardmäßig auf den Haupt-Tag ab. Rohe Tags nur mit `canonical_tags=False` und nur, wenn es einen Grund gibt (AP03). Kandidaten-Tags: 269.
- `score`, `view_count`, `answer_count` sind heutige Werte; Antwortkennzahlen deshalb nur aus Antworten im 7-Tage-Fenster.
- `advice` / `best-practices` = neue Fragetypen ab Oktober 2025 (siehe plan.md 5.1 und 11).
- Rohdateien sind gzip mit mehreren aneinandergehängten Blöcken; Python `gzip` liest das korrekt.
- `owner` kann fehlen (gelöschte Nutzer, ca. 1 % der Antworten). Nutzer-IDs werden für AP14 nur gezählt, nie in Abbildungen, Tabellen, CSV-Ausgaben oder Berichten ausgegeben, auch nicht im Chat.
- Erwartete Kontrollwerte: Fragen 2022 = 105.739, 2024 = 23.161, 2026 = 949; gesamt 2.013.828 Fragen, 3.025.782 Antworten.

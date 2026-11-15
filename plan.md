# Umsetzungsplan: Sichtbares Wissen auf Stack Overflow vor und nach ChatGPT

*Stand: 15.11.2026 · Grundlage: Exposé Variante B (Engelmann, Jetullahu), Projektstand vom 14.11.2026, Rohdaten in `../Datentest`*

Dieses Dokument ist der Fahrplan für das Datenprojekt. Es legt fest, **was** berechnet wird, **wie** es definiert ist, **welche Diagramme und Tabellen** entstehen und **in welcher Reihenfolge** gearbeitet wird. Jedes Arbeitspaket (AP) ist so beschrieben, dass Claude Code es direkt umsetzen kann:

```text
/ap AP01
```

(Der Befehl liegt in `.claude/commands/ap.md`. Er liest dieses Dokument, `CLAUDE.md` und das genannte AP, setzt es um und prüft die Akzeptanzkriterien.)

---

## Inhalt

1. Kurzfassung
2. Was wir machen und was bewusst nicht
3. Technische Entscheidungen (Werkzeuge, Diagramme)
4. Projektstruktur und Datenfluss
5. Definitionen (verbindlich)
6. Arbeitspakete AP00–AP15
7. Diagrammkatalog
8. Tabellenkatalog
9. Evaluation (Abgleich mit Exposé Abschnitt 6)
10. Zeitplan
11. Präzisierungen und Abweichungen gegenüber dem Exposé
12. Risiken und Gegenmaßnahmen
13. Offene Entscheidungen fürs Team
14. Zuordnung zur Gliederung des Papers
15. Statusübersicht

---

## 1 Kurzfassung

- **Daten:** 19 Oktober-Monate (2008–2026), 2.013.828 Fragen, 3.025.782 Antworten, bereits vollständig geladen in `../Datentest/<Jahr>/*.jsonl.gz`.
- **Schritt 1:** Rohdaten einmal in Parquet-Tabellen umwandeln, mit allen abgeleiteten Feldern (7-Tage-Fenster, Textlänge ohne Code, neue Fragetypen). Danach laufen alle Analysen in Sekunden.
- **TF1:** Kennzahlen je Oktober, Abweichung vom Trend 2015–2022 (unterbrochene Zeitreihe), Gegenprobe Score ≥ 1.
- **TF2:** Blinde Einordnung der 272 Tags durch beide, Cohens Kappa, Gruppenindex (2022 = 100), Permutationstest mit 10.000 Zufallsgruppen, Weglassen einzelner Tags, Placebo-Test. Dazu 600 von Hand kodierte Fragen, ein automatisches Verfahren (Macro-F1 ≥ 0,70) und dessen Anwendung auf 2.000 Fragen je Jahr.
- **TF3:** Textlänge, KI-Tags, Themenanalyse der Titel (BERTopic gegen NMF, Auswahl nach Probelauf).
- **Sichtbare Antwortende (AP14):** Wie viele Personen zeigen öffentlich, dass sie sich mit Grundlagen bzw. Umgebungen auskennen? Das misst Leonardis „wer weiß was“ direkt.
- **Nur lokale Modelle:** Alle Modelle laufen auf dem eigenen Rechner. Es gibt keine Cloud-Sprachmodelle, keine API-Kosten, und kein Fragetext verlässt den Rechner.
- **Ergebnis:** etwa 20 Abbildungen und 10 Tabellen, die `make figures tables` jederzeit neu erzeugt, dazu `results/kennzahlen.json` mit allen Zahlen fürs Paper.

---

## 2 Was wir machen und was bewusst nicht

| Machen wir | Machen wir nicht (und warum) |
|---|---|
| Beschreiben, wie sich Umfang, Antwortverhalten und Inhalte verändert haben | Keine Ursache nachweisen. Die Arbeit ist beschreibend (Exposé Abschnitt 2 und 7). |
| Abweichung vom Trend vor ChatGPT zeigen (unterbrochene Zeitreihe) | Keine Signifikanztests als Hauptaussage. Bei 2 Mio. Fragen ist fast alles signifikant, deshalb Veränderungen und Effektstärken. |
| Grundlagen- gegen Umgebungsfragen, blind gebildet und gegengeprüft | Keine Schwierigkeitsstufen. Das machen Han et al. (2026) schon. |
| Themen der Titel vor und nach ChatGPT | Keine Prüfung, welche Antwort eine KI gegeben hätte. Das war im Projektstand eine Idee, gehört aber nicht zu den Teilfragen und kostet viel. |
| Ein Monat je Jahr (Oktober), voll ausgezählt | Keine Monatsreihen. Die Daten liegen nur für Oktober vor. |
| Sichtbare Antwortende je Gruppe (AP14) als Messung von „wer weiß was“; optional KI-Erwähnungen im Fragetext (AP15) | Keine Daten aus Unternehmen und keine Befragung. Der Bezug zu Leonardi bleibt eine Analogie. |
| Nur lokale Modelle: TF-IDF, SetFit, Zero-Shot-Modell, BERTopic, NMF | Keine Cloud-Sprachmodelle (OpenAI, Anthropic usw.): keine Kosten, keine Weitergabe der Texte, Ergebnisse mit fester Modellversion wiederholbar |

---

## 3 Technische Entscheidungen

### 3.1 Jupyter oder etwas anderes?

**Entscheidung: Analyse-Code als Python-Module und Skripte, Erkunden in marimo-Notebooks, alle Paper-Abbildungen per Skript.**

| Option | Vorteil | Nachteil | Einsatz hier |
|---|---|---|---|
| **Python-Module + Skripte + Makefile** | reproduzierbar, testbar, eine Änderung an einer Definition wirkt überall; Claude Code kann alles direkt lesen, ändern und ausführen | weniger „Spielwiese“ | **Hauptweg** für Datenaufbereitung, Kennzahlen, Statistik und alle Abbildungen fürs Paper |
| **marimo** | Notebooks sind normale `.py`-Dateien (gut für Git und Claude Code), reaktiv (keine veralteten Zellen), als Skript ausführbar, Export nach HTML, einfache Bedienelemente | neu zu lernen (ähnlich wie Jupyter) | **Erkunden**, Zwischenstände anschauen, Kodier-Oberfläche für die 600 Fragen |
| Jupyter (.ipynb) | aus der Bachelorarbeit bekannt | JSON-Format mit Ausgaben, schwer zu vergleichen und für Claude Code umständlich zu bearbeiten, versteckter Zellzustand | weiter möglich, aber nicht für Code, auf dem Ergebnisse beruhen |
| Quarto | Paper und Code in einem Dokument | zusätzliches Werkzeug, Format des Papers noch offen | nicht nötig |

Merksatz: **Was ins Paper kommt, entsteht durch ein Skript. Notebooks dienen nur zum Anschauen.**

### 3.2 Bibliotheken

| Zweck | Wahl | Begründung |
|---|---|---|
| Umgebung | `uv` (bereits installiert), Python 3.12 | schnelle, reproduzierbare Installation; 3.12 wegen PyTorch/BERTopic |
| Datentabellen | **Polars** + Parquet | 2 Mio. Zeilen in Sekunden, wenig Arbeitsspeicher (24 GB reichen locker) |
| HTML-Bereinigung | `selectolax` | schnell genug für 2 Mio. Fragetexte |
| Statistik | `statsmodels`, `scipy`, `scikit-learn` | unterbrochene Zeitreihe, Kappa, F1, Konfidenzintervalle |
| Diagramme | **matplotlib** mit eigenem Stil (`src/sov/plotting/style.py`) | volle Kontrolle für druckfähige Abbildungen, Vektor-PDF für Word und LaTeX |
| Themenanalyse | `bertopic`, `sentence-transformers` (optionale Gruppe `topics`) | etabliertes Verfahren, läuft auf dem M4 |
| Klassifikation | `scikit-learn` (Basislinie), `setfit` und ein Zero-Shot-Modell über `transformers` (Gruppe `ml`) | die drei Kandidaten aus AP10 |
| Modelle | alle lokal; Gewichte werden einmal von Hugging Face geladen, Name und Revision stehen in `config.py`; Rechnen auf der Apple-GPU (`mps`) | wiederholbar, kostenlos, Texte verlassen den Rechner nicht |
| Tests und Stil | `pytest`, `ruff` | Definitionen absichern |

### 3.3 Diagramme: einheitliche Regeln

- Ausgabe jeder Abbildung als **PDF (Vektor) und PNG (300 dpi)** in `figures/`, Dateiname = ID aus dem Diagrammkatalog, z. B. `F08_index_gruppen.pdf`.
- **Farben nach Bedeutung, immer gleich:** Grundlagen = Blau `#2a78d6`, Umgebung = Orange `#eb6834`, Sonstige/keine Gruppe = Grau `#898781`, Gesamt = Schwarz `#0b0b0b`, Trend-Fortschreibung = Grau gestrichelt mit hellem Band. Diese drei Farben sind auch bei Farbsehschwäche unterscheidbar (geprüft mit dem Palettenvalidator der dataviz-Vorgaben).
- **ChatGPT-Markierung** in jedem Zeitverlauf: senkrechte gestrichelte Linie zwischen 2022 und 2023, Beschriftung „ChatGPT“. Jahre 2025/2026 heller oder hohl markiert („nur Bestätigung“, kleine Fallzahlen).
- **Kein Titel im Bild** (der steht in der Bildunterschrift im Paper), Achsen auf Deutsch, Dezimalkomma, Tausenderpunkt.
- **Eine y-Achse** je Diagramm. Zwei Größen mit verschiedenen Skalen kommen in zwei Felder (Small Multiples) oder werden indexiert.
- Linien direkt beschriften statt Legendenkasten, wo es bei ≤ 4 Linien passt.
- Breiten: ganze Seite 16 cm, halbe Seite 7,8 cm (Konstanten in `style.py`).

---

## 4 Projektstruktur und Datenfluss

```text
Wissensmanagment/                (GitHub-Repo, liegt neben ../Datentest)
├── plan.md                     dieser Plan
├── CLAUDE.md                   Regeln für Claude Code
├── README.md                   Einrichtung und Befehle
├── pyproject.toml              Abhängigkeiten (uv)
├── Makefile                    Pipeline: make data, make metrics, … make figures
├── .claude/commands/ap.md      /ap APxx setzt ein Arbeitspaket um
├── config/ai_tags.txt          die 26 KI-Tags (Exposé 5.1)
├── docs/
│   ├── datenmodell.md          Spalten der Parquet-Tabellen
│   ├── entscheidungen.md       Entscheidungsprotokoll (fürs Methodenkapitel)
│   ├── kodierleitfaden_tags.md Entwurf
│   └── kodierleitfaden_fragen.md Entwurf
├── src/sov/                    Python-Paket (sov = "Stack Overflow Visibility")
│   ├── config.py               alle Konstanten und Pfade
│   ├── io.py                   Laden der Rohdaten und Parquet-Tabellen
│   ├── text.py                 HTML → Text, Code entfernen, Längen
│   ├── metrics.py              Kennzahlen TF1/TF3
│   ├── its.py                  unterbrochene Zeitreihe
│   ├── groups.py               Gruppenindex, Permutation, Weglassen, Placebo
│   ├── agreement.py            Kappa, F1, Konfusionsmatrix
│   ├── sampling.py             Stichproben mit festem Seed
│   ├── answerers.py            sichtbare Antwortende (AP14)
│   ├── classify/               Basislinie, SetFit, Zero-Shot
│   ├── topics/                 BERTopic, NMF
│   ├── figures/                eine Funktion je Abbildung
│   └── plotting/style.py       Stil, Farben, Speichern
├── scripts/                    nummerierte Einstiegspunkte (rufen src/sov auf)
├── notebooks/                  marimo-Notebooks (nur Erkunden + Kodier-App)
├── coding/                     Kodierbögen (füllen nur Menschen aus)
│   ├── tags/
│   ├── questions/
│   └── topics/
├── data/                       (nicht versionieren)
│   ├── interim/                questions.parquet, answers.parquet, texts.parquet
│   └── processed/              Kennzahlen als CSV
├── results/                    kennzahlen.json, Modellkarten, Logs
├── figures/                    F01 … F23 als PDF + PNG
├── tables/                     T1 … T8 als CSV, Markdown, LaTeX
└── tests/
```

**Datenfluss:**

```text
../Datentest/<Jahr>/*.jsonl.gz
   │  AP01 build_dataset
   ▼
data/interim/{questions,answers,texts}.parquet
   ├─ AP02 metrics ─────────► data/processed/metrics_yearly.csv ─┐
   ├─ AP03 tag_audit ───────► tags_272.csv, tag_wiki.csv        │
   │     AP04 coding_sheets ► coding/tags/*.csv  (Menschen kodieren)
   │     AP05 agreement ────► groups.json, kappa ───────────────┤
   ├─ AP06 samples ─────────► coding/questions/*.csv (Menschen) │
   ├─ AP07 group_compare ───► group_index.csv, permutation.csv ─┤
   ├─ AP08 its ─────────────► its_results.csv ──────────────────┤
   ├─ AP10 classify ────────► classified_sample.parquet ────────┤
   ├─ AP11 topics ──────────► topics.parquet, topic_shares.csv ─┤
   ├─ AP12 checks ──────────► checks.md                         │
   └─ AP14 answerers ───────► answerers_yearly.csv ─────────────┤
                                                                ▼
                               AP13 figures + tables → figures/, tables/, results/kennzahlen.json
```

---

## 5 Definitionen (verbindlich)

Alle Konstanten stehen in `src/sov/config.py`. Änderungen an einer Definition werden in `docs/entscheidungen.md` protokolliert.

### 5.1 Grundgesamtheit

- **Jahr** = Oktober des Jahres, 1.10. 00:00 bis 31.10. 23:59:59 UTC, nach `creation_date` der Frage.
- **Neue Fragetypen** (seit Oktober 2025): Frage trägt den Tag `advice` oder `best-practices` **und** wurde ab 1.10.2025 gestellt. Vorher kommen beide Tags nur vereinzelt als normale Tags vor (13 Fragen 2008–2020, bleiben klassisch); 2025: 41 Fragen (alle ab 21.10.2025), 2026: 67. Sie werden in allen TF1-Kennzahlen zum Antwortverhalten **ausgeschlossen** und getrennt berichtet. Bei der Zahl der Fragen wird beides gezeigt (gesamt und davon neue Typen).
- **Klassische Fragen** = alle anderen. Das ist die Grundgesamtheit für TF1-Antwortverhalten, TF2 und TF3.
- **Gegenprobe Score ≥ 1:** dieselben Kennzahlen nur für Fragen mit heutigem `score ≥ 1`.

### 5.2 Antwortfenster

- **Antwort im Fenster** = Antwort mit `0 ≤ creation_date(Antwort) − creation_date(Frage) ≤ 7 × 24 h`.
- Antworten mit negativem Abstand (bei zusammengelegten Fragen möglich) zählen nie und werden im Datenprotokoll gezählt.
- Alle Antwortkennzahlen nutzen nur das Fenster, nie `answer_count` (das ist der heutige Wert).

### 5.3 Kennzahlen TF1 und TF3

| ID | Kennzahl | Definition | Grundgesamtheit |
|---|---|---|---|
| K1 | Fragen | Anzahl Fragen je Oktober (zusätzlich: davon neue Typen) | alle |
| K2 | Antworten je Frage | Mittelwert und Median der Antworten im Fenster | klassisch |
| K3 | Unbeantwortet | Anteil Fragen ohne Antwort im Fenster | klassisch |
| K4 | Zeit bis zur ersten Antwort | Median in Stunden über Fragen mit Antwort im Fenster | klassisch, beantwortet |
| K5 | Antwort in 24 h | Anteil aller Fragen mit erster Antwort innerhalb 24 h | klassisch |
| K6 | Akzeptierte Antwort | Anteil Fragen, deren akzeptierte Antwort im Fenster geschrieben wurde | klassisch |
| K7 | Gruppenanteil | Anteil Fragen mit ≥ 1 Tag der Gruppe; Index = Anteil / Anteil 2022 × 100 | klassisch |
| K8 | Textlänge | Median der Zeichen im Fragetext ohne Codeblöcke (`<pre>` entfernt, Inline-`<code>` bleibt Text, Leerraum zusammengefasst) | klassisch |
| K9 | KI-Bezug | Anteil Fragen mit ≥ 1 der 26 KI-Tags (`config/ai_tags.txt`) | klassisch |

Zusätzlich für Abbildungen und Gegenproben (ohne eigene Teilfrage): Anteil Fragen mit Codeblock, Anteil geschlossener Fragen, Gründe für Schließung.

### 5.4 Effektstärken

- Zählungen und Mediane: **Veränderung in Prozent** (2022 → 2024, 2022 → 2025, 2022 → 2026).
- Anteile: zusätzlich **Cohens h** zwischen 2022 und dem Vergleichsjahr.
- Abweichung vom Trend: **beobachtet / erwartet − 1** in Prozent, mit 95-%-Vorhersageintervall der Fortschreibung.
- Gruppenvergleich: **Abstand der Indexwerte** (Umgebung − Grundlagen) und **Verhältnis der Behaltensquoten** (Anteil 2024 / Anteil 2022 je Gruppe, dann Umgebung ÷ Grundlagen).

### 5.5 Unterbrochene Zeitreihe (Bernal et al. 2017)

Für jede TF1-Kennzahl und jeden Gruppenanteil, Jahre als Zeitpunkte t:

1. **Hauptauswertung (Fortschreibung):** lineares Modell auf 2015–2022 (8 Punkte). Für Zählungen und Wartezeiten auf der Log-Skala, für Anteile auf der Logit-Skala. Fortschreibung auf 2023–2026 mit 95-%-Vorhersageintervall. Berichtet wird die Abweichung beobachtet/erwartet je Jahr.
2. **Ergänzung (segmentierte Regression):** `y = β0 + β1·t + β2·nach + β3·(t − 2022)·nach` über 2015–2026, berichtet werden β2 (Niveausprung) und β3 (Steigungsänderung) beschreibend mit Konfidenzintervall. Hinweis im Paper: nur 12 Punkte, Autokorrelation nicht modellierbar, deshalb nur beschreibend.
3. 2024 ist Hauptvergleichsjahr; 2025/2026 werden gezeigt, aber als Bestätigung markiert.

### 5.6 Gruppen (TF2)

- Kandidaten: alle Tags mit ≥ 150 klassischen Fragen im Oktober 2022 (erwartet: 272).
- Gruppe Grundlagen (G) bzw. Umgebung (U) = Tags, die **beide** Kodierenden gleich als G bzw. U einordnen. Alles andere: keine Gruppe.
- Eine Frage zählt zu einer Gruppe, wenn sie ≥ 1 Tag der Gruppe hat. Fragen mit Tags aus beiden Gruppen zählen in beiden (Anteil wird berichtet). Gegenprobe: nur Fragen, die genau einer Gruppe angehören.

---

## 6 Arbeitspakete

Jedes AP hat: **Ziel · Eingaben · Ausgaben · Umsetzung · Akzeptanzkriterien**. „Mensch“ markiert Schritte, die Claude Code nicht übernehmen darf.

### AP00 Einrichtung

- **Ziel:** lauffähige Umgebung.
- **Umsetzung:** `uv sync` (Basis), später `uv sync --group topics --group ml`. Git-Repository anlegen (`git init`), `data/`, `results/models/` und `.env` sind in `.gitignore`. Pfad zu den Rohdaten über `SOV_RAW_DIR` (Standard `../Datentest`).
- **Akzeptanz:** `uv run python -c "import sov.config as c; print(c.RAW_DIR.exists())"` gibt `True`; `uv run pytest` läuft.

### AP01 Datenbasis als Parquet

- **Ziel:** einmalige Umwandlung der Rohdaten in drei Tabellen mit allen abgeleiteten Feldern (Spalten siehe `docs/datenmodell.md`).
- **Eingaben:** `../Datentest/<Jahr>/{questions,answers}.jsonl.gz`, `_progress.json`.
- **Ausgaben:** `data/interim/questions.parquet`, `answers.parquet`, `texts.parquet`; `results/logs/build_dataset.md` (Datenprotokoll).
- **Umsetzung:**
  - `src/sov/io.py`: Rohdaten zeilenweise lesen (gzip, mehrere aneinandergehängte Blöcke beachten), je Jahr parallel (`concurrent.futures`, 8 Prozesse).
  - `src/sov/text.py`: `html_to_text(body, drop_code=True)`, Codeblöcke = `<pre>`; Code separat als Text; HTML-Entitäten auflösen; Leerraum zusammenfassen. Platzhalter `[CODE]` an Stelle entfernter Blöcke für die Klassifikation.
  - Abgeleitete Felder: `is_new_type`, `n_answers_7d`, `first_answer_hours`, `answered_7d`, `answered_24h`, `accepted_7d`, `body_len_nocode`, `has_code`, `code_chars`, `is_closed`, `closed_reason`, `n_ai_tags`.
  - Datenprotokoll: Fragen und Antworten je Jahr, Abgleich mit `_progress.json`, Antworten ohne zugehörige Frage, negative Antwortabstände, fehlende Felder.
- **Akzeptanz:**
  - Fragen je Jahr = `_progress.json` (z. B. 2022: 105.739, 2024: 23.161, 2026: 949); Summe 2.013.828, Antworten 3.025.782.
  - Median Textlänge weicht höchstens ±5 Zeichen vom Projektstand ab (2022: 426, 2024: 588, 2026: 719); falls nicht, Ursache im Protokoll erklären.
  - Tests in `tests/test_text.py` (Code-Entfernung, Entitäten) und `tests/test_window.py` (7-Tage-Grenzen, negative Abstände).
  - Laufzeit des gesamten Aufbaus unter 15 Minuten.

### AP02 Kennzahlen TF1 und TF3 neu berechnen

- **Ziel:** K1–K6, K8, K9 je Oktober, jeweils für „klassisch“ und „Score ≥ 1“.
- **Ausgaben:** `data/processed/metrics_yearly.csv` (lang: `year, population, metric, value`), `data/processed/new_types.csv` (neue Fragetypen getrennt: Anzahl, Score, Antworten, akzeptiert, geschlossen), `data/processed/ai_tags_yearly.csv`, `data/processed/top_tags_yearly.csv` (Top 25).
- **Umsetzung:** `src/sov/metrics.py` mit einer Funktion je Kennzahl, Eingabe ist ein Polars-DataFrame. Veränderungen in Prozent und Cohens h in `data/processed/changes.csv`.
- **Akzeptanz:** Fragenzahlen identisch zum Projektstand; KI-Anteil 2022 ≈ 0,08 %, 2026 ≈ 1,7 % (Abweichung nur durch den Ausschluss neuer Typen erklärbar); Unit-Tests mit einer Mini-Tabelle von 6 Fragen, deren Kennzahlen von Hand ausgerechnet sind.

### AP03 Tag-Prüfung: Kandidaten, Synonyme, Brüche

- **Ziel:** Liste der 272 Kandidaten-Tags plus Kontext für die blinde Einordnung, ohne Zahlen.
- **Ausgaben:** `data/processed/tags_candidates.csv` (Tag, Fragen 2022, intern), `data/processed/tag_wiki.csv` (Tag, Auszug aus dem Tag-Wiki), `data/processed/tag_synonyms.csv`, `results/logs/tag_audit.md`.
- **Umsetzung:**
  - Kandidaten aus `questions.parquet` (klassisch, 2022, ≥ 150).
  - Tag-Wiki-Auszüge und Synonyme über die Stack Exchange API: `/tags/{tags}/wikis` und `/tags/{tags}/synonyms`, bis zu 100 Tags je Anfrage, also wenige Anfragen. Dafür `../Datentest/scripts/se_api.py` wiederverwenden (Key bleibt in `../Datentest/.env`, wird nie ausgegeben).
  - Brüche finden: Tags, deren Anteil von einem Jahr aufs nächste auf < 10 % fällt oder auf 0 springt (Beispiel `selenium`), und Tags, die erst nach 2015 entstehen. Für jeden Fund im Protokoll eine Empfehlung (behalten, mit Nachfolger zusammenlegen, ausschließen). Die Entscheidung trifft das Team und trägt sie in `docs/entscheidungen.md` ein.
- **Akzeptanz:** genau 272 Kandidaten (oder Abweichung begründet); jeder Kandidat hat einen Wiki-Auszug oder den Vermerk „kein Wiki“.

### AP04 Kodierbögen für die Tags

- **Ziel:** zwei getrennte, gleich aufgebaute Bögen, **ohne Fragezahlen, ohne Jahre, ohne Trends**.
- **Ausgaben:** `coding/tags/tags_kodierer_A.csv`, `coding/tags/tags_kodierer_B.csv` mit Spalten `nr, tag, wiki_auszug, kategorie (G/U/K), unsicher (x), notiz`. Reihenfolge je Bogen zufällig (eigener Seed je Bogen), damit keine Reihenfolgeeffekte gleich wirken.
- **Umsetzung:** kleines Skript; Leitfaden `docs/kodierleitfaden_tags.md` finalisieren (Entwurf liegt bei).
- **Akzeptanz:** keine Spalte enthält Zahlen außer `nr`; beide Bögen enthalten dieselben 272 Tags.
- **Mensch:** beide kodieren unabhängig, ohne Absprache, ohne Zahlen anzusehen. Claude Code füllt diese Bögen nicht aus und schlägt keine Kategorien vor.

### AP05 Übereinstimmung Tags und Gruppen festlegen

- **Ziel:** Cohens Kappa, endgültige Gruppen.
- **Ausgaben:** `results/agreement_tags.md` (Kappa gesamt, Übereinstimmung in Prozent, Kreuztabelle 3×3, Kappa je Kategorie gegen Rest), `data/processed/groups.json` (`{"G": [...], "U": [...]}`), Tabelle T4.
- **Umsetzung:** `src/sov/agreement.py` (`sklearn.metrics.cohen_kappa_score`, Bootstrap-Konfidenzintervall, 2.000 Wiederholungen).
- **Akzeptanz:** Kappa ≥ 0,61. Falls darunter: Leitfaden schärfen, zweite Runde nur für die strittigen Tags dokumentieren, Wert im Paper offenlegen (Exposé Abschnitt 6).

### AP06 Stichproben und Kodier-App für Fragen

- **Ziel:** 30 Kalibrierungsfragen, 600 Stichprobenfragen (50 je Jahr 2015–2026), davon 150 doppelt kodiert.
- **Ausgaben:**
  - `coding/questions/kalibrierung_30.csv` (aus 2015–2026, nicht in der Stichprobe)
  - `coding/questions/stichprobe_600.csv` (interne Liste mit Jahr, nur für die Auswertung)
  - `coding/questions/kodierer_A.csv`, `kodierer_B.csv` (A: alle 600; B: die 150 Doppelten; jeweils gemischte Reihenfolge)
  - `notebooks/kodier_app.py` (marimo)
- **Umsetzung:**
  - `src/sov/sampling.py`: geschichtete Zufallsstichprobe aus klassischen Fragen mit `config.SEED`. Die 150 Doppelten: geschichtet, etwa 12–13 je Jahr.
  - **Kodieransicht ohne Jahr, ohne Tags, ohne Score**, nur Titel und Text mit Codeblöcken (gekürzt auf 4.000 Zeichen). So sehen Menschen dasselbe wie das automatische Verfahren, und das Wissen um Jahr oder Tag beeinflusst die Einordnung nicht.
  - Kodier-App: zeigt eine Frage, Knöpfe G/U/S, Feld „unsicher“, speichert nach jedem Klick in die CSV des gewählten Kodierers, kann unterbrochen und fortgesetzt werden.
  - Aufteilung für AP10: Die 150 Doppelten sind die **Testmenge** (Konsenslabel nach Klärung), die übrigen 450 die Trainings- und Entwicklungsmenge. Die Testmenge wird in `coding/questions/split.csv` festgeschrieben.
- **Akzeptanz:** Stichprobe reproduzierbar (zweimal erzeugen ergibt dieselben IDs); keine Überschneidung von Kalibrierung und Stichprobe; App läuft mit `uv run marimo run notebooks/kodier_app.py`.
- **Mensch:** Kalibrierung (30 Fragen gemeinsam besprechen, Leitfaden schärfen), dann Kodierung. Danach Konsens für die 150 Doppelten (Spalte `konsens` in `coding/questions/konsens_150.csv`).

### AP07 Gruppenvergleich (TF2, Tags)

- **Ziel:** Index Grundlagen gegen Umgebung und seine Absicherung.
- **Ausgaben:** `data/processed/group_index.csv`, `permutation.csv`, `leave_one_out.csv`, `placebo.csv`, `tag_shift.csv`.
- **Umsetzung** (`src/sov/groups.py`):
  1. Anteil und Index je Gruppe und Jahr (K7), auch für die Gegenproben „Score ≥ 1“ und „nur eine Gruppe“.
  2. **Permutationstest:** 10.000-mal zwei nicht überlappende Zufallsgruppen derselben Größe wie G und U aus denselben 272 Tags; Abstand der Indexwerte für 2023, 2024, 2025, 2026. Berichtet: Perzentil des beobachteten Abstands, p = (k + 1)/(N + 1), Median und 95-%-Quantil der Zufallsabstände. Vektorisiert über eine Matrix Tag × Jahr mit Fragezahlen, damit es in Sekunden läuft (Achtung: Fragen mit mehreren Tags einer Gruppe nur einmal zählen; dafür eine dünn besetzte Matrix Frage × Tag nutzen).
  3. **Weglassen einzelner Tags:** Abstand 2024 ohne jeweils einen Tag.
  4. **Placebo-Test:** gleiche Rechnung mit Basis 2019 = 100 und Vergleichsjahr 2021 (beide vor ChatGPT). Erwartung: kleiner Abstand.
  5. **Behaltensquote je Tag:** Anteil 2024 / Anteil 2022 und Vortrend Anteil 2022 / Anteil 2019, für alle 272 Tags mit Gruppe.
- **Akzeptanz:** Mit den 20+20 Tags aus dem Projektstand reproduziert die Funktion die Werte 52,5 und 129,1 (Test); Permutation läuft < 1 Minute.

### AP08 Unterbrochene Zeitreihe (TF1, TF2)

- **Ziel:** Abweichung vom Trend für K1–K6, K8 und beide Gruppenanteile.
- **Ausgaben:** `data/processed/its_fit.csv` (je Kennzahl und Jahr: beobachtet, erwartet, Intervall, Abweichung), `data/processed/its_segmented.csv` (β2, β3 mit KI), Tabelle T3.
- **Umsetzung:** `src/sov/its.py` nach Abschnitt 5.5, `statsmodels.OLS` und `get_prediction().summary_frame(alpha=0.05)`.
- **Akzeptanz:** Unit-Test mit künstlicher Reihe (bekannter Sprung wird gefunden); für K1 2023 liegt der beobachtete Wert unter dem Vorhersageintervall (Plausibilitätsprüfung, keine Erwartung, die erzwungen wird).

### AP09 Doppelkodierung auswerten

- **Ziel:** Kappa der 150 Doppelten, Konsensmenge als Testmenge.
- **Ausgaben:** `results/agreement_questions.md`, Tabelle T4 (zweite Zeile), `coding/questions/labels_600.csv` (A für 450, Konsens für 150).
- **Akzeptanz:** Kappa ≥ 0,61, sonst wie AP05.

### AP10 Automatische Einordnung von Fragetexten (TF2 ohne Tags)

- **Ziel:** Verfahren mit bestem Macro-F1 (≥ 0,70) wählen und auf 2.000 Fragen je Jahr anwenden.
- **Kandidaten** (alle **lokal**, alle auf denselben Eingaben: Titel + Text mit `[CODE]`-Platzhaltern bzw. gekürztem Code, ohne Tags, ohne Jahr):
  1. **Basislinie:** TF-IDF + logistische Regression (scikit-learn), trainiert auf den 450.
  2. **SetFit:** ein Sentence-Transformer (`config.SETFIT_BASE_MODEL`), mit den 450 Beispielen feinabgestimmt. Dafür ist SetFit gebaut: Klassifikation mit wenigen hundert Beispielen.
  3. **Zero-Shot-Modell ohne eigenes Training:** ein für Zero-Shot-Klassifikation trainiertes Modell (`config.ZERO_SHOT_MODEL`, Alternative `config.ZERO_SHOT_MODEL_ALT`). Jede Kategorie wird als Hypothesensatz aus dem Kodierleitfaden formuliert, z. B. „Die Lösung hängt von Betriebssystem, Versionen, Konfiguration oder Werkzeugen ab.“ Das Modell gibt an, welcher Satz am besten zum Fragetext passt. Das ist das „Sprachmodell ohne eigenes Training“ aus Exposé 5.2. Die Hypothesensätze werden **nur** mit den 450 entwickelt.
- **Regel gegen Überanpassung:** Die 150 Testfragen werden je Kandidat **genau einmal** am Ende ausgewertet. Vorher dient Kreuzvalidierung auf den 450 zur Auswahl von Einstellungen.
- **Rechenaufwand:** Basislinie in Sekunden, SetFit wenige Minuten, Zero-Shot auf ≈ 23.000 Fragen je nach Modellgröße 1–3 Stunden auf der Apple-GPU (`device="mps"`); kann über Nacht laufen. Vorher mit 200 Fragen die Laufzeit messen.
- **Ausgaben:** `results/classify/vergleich.csv` (Macro-F1, F1 je Klasse, Genauigkeit je Kandidat, mit Bootstrap-KI), Konfusionsmatrix des Gewinners, `data/processed/classified_sample.parquet` (question_id, year, label, Verfahren), `data/processed/text_group_shares.csv` (Anteil G/U/S je Jahr mit Wilson-Intervall), Modellkarte `results/classify/modell.md` (Modellname, Revision/Commit-Hash von Hugging Face, Paketversionen, Datum, Einstellungen, Hypothesensätze, Laufzeit).
- **Anwendung:** 2.000 zufällige klassische Fragen je Jahr 2015–2025, 2026 alle 949, ohne die 600 kodierten. Gegenprobe: Anteile mit der Konfusionsmatrix korrigieren (adjusted classify and count) und neben den Rohanteilen zeigen.
- **Modelle:** werden einmal von Hugging Face heruntergeladen und danach offline genutzt. Name und Revision stehen in `config.py`, damit der Lauf später exakt wiederholbar ist. Keine Cloud-API.
- **Akzeptanz:** Gewinner hat Macro-F1 ≥ 0,70 auf den 150. Falls kein Kandidat das erreicht: Ergebnis trotzdem berichten, Textanalyse nur als Hinweis deuten, im Paper offenlegen.

### AP11 Themenanalyse (TF3)

- **Ziel:** Themen der Fragetitel je Jahr 2015–2026.
- **Eingabe:** je Oktober 2015–2026 gleich viele Titel, so viele wie 2026 klassische Fragen hat (≈ 880–949), zufällig mit Seed. Zusammen etwa 11.000 Titel.
- **Probelauf (1.000 Titel, gleich verteilt über die Jahre):**
  - **A: BERTopic** mit lokalem Embedding-Modell (`config.EMBEDDING_MODEL`, Alternative `config.EMBEDDING_MODEL_ALT`), UMAP mit festem `random_state`, HDBSCAN, c-TF-IDF mit KeyBERTInspired-Darstellung, Reduktion auf 20–40 Themen. BERTopic ist für kurze Texte wie Titel geeignet, weil es mit Satz-Embeddings statt Wortzählungen arbeitet.
  - **B: NMF** (Non-negative Matrix Factorization) auf TF-IDF der Titel (scikit-learn), gleiche Themenzahl. Das ist ein etabliertes klassisches Verfahren als Vergleich und kommt mit kurzen Texten besser zurecht als LDA.
  - **Themennamen** vergeben beide Autor:innen gemeinsam aus den Schlüsselwörtern und 5 typischen Titeln je Thema. Geprüft wird danach mit **anderen**, zufällig gezogenen Titeln.
  - Beide Verfahren werden mit der Themenprüfung aus Abschnitt 9 bewertet (10 zufällige Titel je Thema, beide unabhängig). Gewählt wird das Verfahren mit dem höheren Anteil bestandener Themen (≥ 8/10 passend).
- **Hauptlauf** mit dem gewählten Verfahren auf allen ~11.000 Titeln; danach Themenprüfung erneut.
- **Ausgaben:** `data/processed/topics.parquet` (question_id, year, topic_id), `data/processed/topic_shares.csv`, `results/topics/themen.md` (Name, Beschreibung, 5 Beispieltitel mit Link, Anteil vor/nach), Prüfbögen `coding/topics/themen_check_{A,B}.csv`.
- **Akzeptanz:** ≥ 80 % der Themen bestehen die Prüfung; Ergebnisse mit festem Seed und fester Modellrevision reproduzierbar (zweiter Lauf ergibt dieselben Themen); Modellkarte `results/topics/modell.md`.

### AP12 Datenprüfung und Literaturabgleich

- **Ziel:** Richtigkeit der Daten und Einordnung.
- **Umsetzung:**
  - 20 zufällige Fragen (Seed) mit Link, Erstellzeit, Tags, Zahl der Antworten im Fenster, Zeit bis zur ersten Antwort, akzeptiert ja/nein in `coding/checks/datenpruefung_20.csv`. **Mensch:** auf stackoverflow.com vergleichen, Spalte `stimmt` ausfüllen. Abweichungen erklären (z. B. Antworten seitdem gelöscht).
  - Literaturabgleich: Rückgang der Fragen 2022 → 2023 (bisher −50,5 %) neben Burtch et al. (2024) und del Rio-Chanona et al. (2024) stellen. Beachten: andere Zeiträume und Vergleichsdesigns, deshalb nur Richtung und Größenordnung vergleichen.
  - Neue Fragetypen: 5 Fragen mit `advice`/`best-practices` aus 2025 und 5 aus 2026 auf der Website ansehen (Abstimmung möglich? akzeptierte Antwort möglich?), Befund in `docs/entscheidungen.md`.
- **Ausgaben:** `results/checks.md`.

### AP13 Abbildungen, Tabellen, Kennzahlen fürs Paper

- **Ziel:** alle Abbildungen aus Abschnitt 7 und Tabellen aus Abschnitt 8 mit einem Befehl.
- **Umsetzung:** `src/sov/figures/<id>.py` mit je einer Funktion `make()`; `scripts/13_figures.py` ruft alle auf. Tabellen als CSV, Markdown und LaTeX. `results/kennzahlen.json` sammelt alle im Text genannten Zahlen (z. B. `tf2.abstand_2024`), damit im Paper keine Zahl von Hand abgeschrieben werden muss.
- **Akzeptanz:** `make figures tables` läuft ohne Fehler; jede Abbildung einmal angesehen (Beschriftungen überlappen nicht, Farben nach Abschnitt 3.3); `results/ergebnisse.md` fasst die Kernaussagen je Teilfrage mit Verweis auf Abbildung und Tabelle zusammen.

### AP14 Sichtbare Antwortende: Wer zeigt, dass er sich auskennt? (fest eingeplant)

- **Ziel:** messen, wessen Wissen auf Stack Overflow sichtbar bleibt, getrennt nach Grundlagen und Umgebung.
- **Begründung (für Kapitel 2a und 3c des Papers):**
  1. **Metawissen ist Wissen über Personen.** Leonardi (2014) beschreibt Metawissen als Wissen darüber, *wer was weiß* und *wer wen kennt*. Es entsteht, weil Dritte fremde Kommunikation mitlesen und vom Inhalt einer Nachricht auf das Wissen der Absendenden schließen (*message transparency*). Auf Stack Overflow ist jede Antwort ein solches Signal: Sie verbindet einen Namen öffentlich mit einem Problem und seiner Lösung.
  2. **Fragen zeigen, *was* besprochen wird, Antwortende zeigen, *wessen* Wissen sichtbar wird.** Ohne die Antwortenden spräche die Arbeit über Leonardi, würde aber nur Themen zählen. Mit ihnen wird der Kernbegriff (wer weiß was) direkt gemessen.
  3. **Das Exposé behauptet es bereits.** Abschnitt 7 endet mit „Sichtbar bliebe dann vor allem, wer sich mit bestimmten Umgebungen auskennt.“ Das ist eine Aussage über Personen. AP14 prüft sie, statt sie nur aus Fragezahlen abzuleiten.
  4. **Es fällt unter die Forschungsfrage.** Diese nennt ausdrücklich „Antwortverhalten“ und „die Sichtbarkeit von Wissen im Sinne von Leonardi“. Neue Daten sind nicht nötig, die Antwortenden stehen schon in den Rohdaten.
  5. **Es schließt eine Lücke aus Exposé Abschnitt 3.** Kim et al. (2026) untersuchen Antwortende nach Rolle, aber für alle Themen zusammen und nur bis 2023. AP14 trennt nach Grundlagen und Umgebung und reicht bis 2026.
  6. **Wiederholung macht Kompetenz erkennbar.** Eine einzelne Antwort ist ein schwaches Signal. Wer im selben Monat mehrfach im selben Bereich antwortet, wird für Mitlesende als Ansprechperson erkennbar. Deshalb gibt es neben der Zahl der Antwortenden auch „erkennbare Expert:innen“.
- **Kennzahlen** (nur Antworten im 7-Tage-Fenster, nur klassische Fragen, je Oktober):

  | ID | Kennzahl | Definition |
  |---|---|---|
  | A1 | Sichtbare Antwortende | verschiedene Nutzerkonten mit ≥ 1 Antwort |
  | A2 | Antwortende je Gruppe | verschiedene Konten mit ≥ 1 Antwort auf eine Frage der Gruppe G bzw. U; als Index (2022 = 100) und je 100 Fragen der Gruppe |
  | A3 | Erkennbare Expert:innen je Gruppe | Konten mit ≥ `config.EXPERT_MIN_ANSWERS` (= 3) Antworten auf Fragen derselben Gruppe im selben Oktober; Index 2022 = 100 |
  | A4 | Konzentration | Anteil der Antworten von den aktivsten 10 % der Antwortenden |
  | A5 | Kontinuität | Anteil der Antwortenden eines Oktobers, die schon im Oktober des Vorjahres geantwortet haben |

- **Deutung:** Die Zahl der Antwortenden muss sinken, wenn es weniger Fragen gibt. Aussagekräftig ist deshalb der **Vergleich der Gruppen** (Index G gegen U, wie in AP07) und die Abweichung vom Trend (AP08), nicht die absolute Zahl. Die Erwartung aus dem Exposé lautet: Erkennbare Expert:innen für Umgebung bleiben anteilig eher erhalten als die für Grundlagen.
- **Grenzen:** Ein Nutzerkonto ist nicht immer eine Person. Antworten gelöschter Konten fehlen (vorab geprüft: 1,6 % der Fenster-Antworten 2015, 1,1 % 2022, 0,6 % 2024, im Protokoll berichten). Reputation wird nicht verwendet, weil sie ein heutiger Wert ist.
- **Datenschutz:** Nutzer-IDs werden nur gezählt, nie in Tabellen, Abbildungen oder Berichten ausgegeben. Es gibt nur Aggregate je Jahr und Gruppe.
- **Vorab geprüfte Größenordnung:** 2022 gab es 30.538 Antwortende (6.695 mit ≥ 3 Antworten), 2024 8.623 (1.434), 2026 489 (78). Je Gruppe reicht das bis 2024 gut, 2025/2026 nur als Bestätigung.
- **Ausgaben:** `data/processed/answerers_yearly.csv`, `answerers_groups.csv`, Abbildungen F07 und F23, Tabelle T10.
- **Abhängigkeit:** A1, A4 und A5 laufen nach AP01; A2 und A3 brauchen die Gruppen aus AP05.
- **Akzeptanz:** Unit-Test mit Mini-Daten (bekannte Zahl Antwortender, Expert:innen, Konzentration); A1 für 2022 = 30.538 (Vorabprüfung); keine Nutzer-ID in irgendeiner Ausgabedatei (Test durchsucht `data/processed/` und `results/`).

### AP15 KI-Erwähnungen im Fragetext (optional)

- Anteil Fragen, die ChatGPT, Copilot, Claude, Gemini, „AI generated“ o. Ä. im Text erwähnen (Wortliste mit Wortgrenzen in `config/ai_mentions.txt`, 50 Treffer von Hand prüfen). Zeigt, ob Fragende auf Stack Overflow kommen, nachdem eine KI nicht geholfen hat. Ergänzt K9 (KI-Tags). Abbildung F22.

---

## 7 Diagrammkatalog

„Pflicht“ = gehört ins Paper. „Anhang“ = Anhang oder Gegenprobe. „Optional“ = nur bei Zeit.

### TF1 Umfang und Antwortverhalten

| ID | Inhalt | Form | Daten | Status |
|---|---|---|---|---|
| F01 | Fragen je Oktober 2008–2026, neue Fragetypen als eigener Teil | Linie (lineare Achse) mit kleinem zweiten Feld in Log-Skala | metrics_yearly | Pflicht |
| F02 | Fragen 2015–2026 gegen Fortschreibung des Trends 2015–2022 | Punkte + Trendlinie gestrichelt + Vorhersageband | its_fit | Pflicht |
| F03 | Antwortverhalten: K2, K3, K4, K5, K6 mit Fortschreibung | 5 kleine Felder (Small Multiples), gemeinsame x-Achse | metrics_yearly, its_fit | Pflicht |
| F04 | Abweichung vom Trend 2023–2026 je Kennzahl in % | Punktdiagramm (Kennzahlen als Zeilen, Jahre als Punkte), 0-Linie | its_fit | Pflicht |
| F05 | Gegenprobe Score ≥ 1 für K2–K6 | wie F03, zwei Linien (alle / Score ≥ 1) | metrics_yearly | Anhang |
| F06 | Verteilung der Zeit bis zur ersten Antwort 2019, 2022, 2023, 2024, 2025 | empirische Verteilungsfunktion, Log-x | questions | Pflicht |
| F07 | Sichtbare Antwortende (A1), Konzentration (A4), Kontinuität (A5) 2008–2026 | 3 kleine Felder, gemeinsame x-Achse | answerers_yearly | Pflicht |

### TF2 Grundlagen und Umgebung

| ID | Inhalt | Form | Daten | Status |
|---|---|---|---|---|
| F08 | Index Grundlagen und Umgebung 2008–2026 (2022 = 100), Trendzeitraum ab 2015 hervorgehoben | 2 Linien, direkt beschriftet | group_index | Pflicht (Hauptabbildung) |
| F09 | Anteile in % (nicht indexiert) für G, U und keine Gruppe | Linien | group_index | Anhang |
| F10 | Permutationstest: Verteilung der 10.000 Zufallsabstände 2024 und beobachteter Abstand | Histogramm + senkrechte Linie; Felder für 2023–2026 | permutation | Pflicht |
| F11 | Behaltensquote je Tag (Anteil 2024 / 2022), alle Tags beider Gruppen | sortiertes Punktdiagramm, Farbe = Gruppe, Linie bei 1 | tag_shift | Pflicht |
| F12 | Vortrend (2019 → 2022) gegen Behaltensquote (2022 → 2024) je Tag | Streudiagramm, Farbe = Gruppe, Log-Achsen | tag_shift | Pflicht |
| F13 | Weglassen einzelner Tags und Placebo-Test | Spanne als Punkt mit Balken | leave_one_out, placebo | Anhang |
| F14 | Textbasierte Anteile G/U/S je Jahr 2015–2026 mit Intervall, daneben Tag-basierter Index | 2 Felder: Linien mit Band | text_group_shares, group_index | Pflicht |
| F15 | Güte der Verfahren: Macro-F1 je Kandidat mit KI; Konfusionsmatrix des Gewinners | 2 Felder: Punkte mit Balken; Heatmap | classify | Anhang |
| F16 | Gruppenindex nach Schließung: Anteil geschlossener Fragen je Gruppe | Linien | questions | Optional |

### TF3 Inhalte

| ID | Inhalt | Form | Daten | Status |
|---|---|---|---|---|
| F17 | Textlänge (Median, Interquartilsband) 2008–2026, dazu je Gruppe G/U | Linie mit Band; 2 Felder | metrics_yearly | Pflicht |
| F18 | KI-Bezug: Anteil mit KI-Tag 2015–2026; daneben die häufigsten KI-Tags 2023–2026 | Linie; horizontale Balken | ai_tags_yearly | Pflicht |
| F19 | Themenanteile je Jahr (Themen × Jahre) | Heatmap, eine Farbe hell → dunkel, Themen nach Veränderung sortiert | topic_shares | Pflicht |
| F20 | Gewinner und Verlierer: Veränderung der Themenanteile (Mittel 2015–2022 gegen Mittel 2023–2026) | divergierende Balken (Blau/Rot) | topic_shares | Pflicht |
| F21 | Rangverlauf der Top-10-Tags 2015–2026 | Rangdiagramm (Bump Chart) | top_tags_yearly | Optional |
| F22 | KI-Erwähnungen im Fragetext (AP15) | Linie | questions/texts | Optional |

### Sichtbare Antwortende (AP14, gehört zu TF1 und TF2)

| ID | Inhalt | Form | Daten | Status |
|---|---|---|---|---|
| F23 | Antwortende (A2) und erkennbare Expert:innen (A3) je Gruppe, Index 2022 = 100 | 2 Felder, je 2 Linien (G blau, U orange), wie F08 | answerers_groups | Pflicht |

---

## 8 Tabellenkatalog

| ID | Inhalt | Kapitel |
|---|---|---|
| T1 | Kennzahlen K1–K9 je Oktober 2008–2026 (Basis für alle Linien) | Anhang |
| T2 | Veränderung 2022 → 2024/2025/2026 in %, Cohens h | 4a |
| T3 | Unterbrochene Zeitreihe: Abweichung vom Trend 2023/2024, β2, β3 | 4a |
| T4 | Übereinstimmung: Kappa Tags, Kappa Fragen, Kreuztabellen | 3e |
| T5 | Gruppen: Tags in G und U (vollständige Liste) | Anhang |
| T6 | Gruppenvergleich: Index 2022/2024, Abstand, Perzentil im Permutationstest, Spanne beim Weglassen, Placebo | 4b |
| T7 | Vergleich der Klassifikationsverfahren | 3d / Anhang |
| T8 | Themen: Name, Beschreibung, Beispiel mit Link, Anteil vorher/nachher, Prüfergebnis | 4c |
| T9 | Neue Fragetypen 2025/2026: Anzahl, Antworten, akzeptiert, geschlossen | 4a |
| T10 | Sichtbare Antwortende: A1–A5 für 2015, 2022, 2024, 2026, je Gruppe, Veränderung in % | 4a/4b |

---

## 9 Evaluation (Abgleich mit Exposé Abschnitt 6)

| Prüfung | AP | Wer | Umfang | Kriterium | Werkzeug |
|---|---|---|---|---|---|
| Einordnung der Tags | AP04/05 | beide unabhängig | 272 Tags | Kappa ≥ 0,61 | Bögen + `agreement.py` |
| Kalibrierung | AP06 | beide gemeinsam | 30 Fragen außerhalb | Leitfaden geschärft | Kodier-App |
| Doppelkodierung | AP09 | beide unabhängig | 150 der 600 | Kappa ≥ 0,61 | Kodier-App + `agreement.py` |
| Klassifikation | AP10 | eine Person | 150 Konsensfragen | Macro-F1 ≥ 0,70 | `classify/` |
| Themen | AP11 | beide unabhängig | 10 Titel je Thema | ≥ 8/10 passen | Prüfbögen |
| Datenabfrage | AP12 | eine Person | 20 Fragen | stimmt mit Website | Prüfbogen |
| Literatur | AP12 | eine Person | Rückgang 2022 → 2023 | Richtung und Größenordnung | `checks.md` |
| Antwortende | AP14 | eine Person | 10 zufällige Antworten | Antwort und Konto stimmen mit Website; Anteil ohne Konto berichtet | `checks.md` |

---

## 10 Zeitplan

| Zeitraum | Arbeitspakete | Menschliche Arbeit | Meilenstein (Exposé) |
|---|---|---|---|
| 16.11.–22.11. | AP00, AP01, AP02, AP03, AP04; Leitfäden finalisieren | Leitfäden lesen und anpassen; Entscheidungen zu Tag-Brüchen | Leitfäden stehen |
| 23.11.–29.11. | AP05, AP06; AP08 (läuft schon ohne Gruppen für TF1) | **272 Tags einordnen (beide, ca. 2–3 h je Person)**; Kalibrierung 30 Fragen | Gruppen festgelegt |
| 30.11.–06.12. | AP07, AP09; Vorbereitung AP10 (Basislinie, SetFit, Hypothesensätze für Zero-Shot an den ersten kodierten Fragen) | **600 + 150 Fragen kodieren (ca. 8–10 h für A, 2–3 h für B)**; Konsens | Kodierung abgeschlossen, Kappa berechnet |
| 07.12.–14.12. | AP10, AP11 (Probelauf + Hauptlauf), AP12, AP14 | Themenprüfung (beide), Datenprüfung 20 Fragen | Datenerhebung abgeschlossen |
| 15.12.–21.12. | AP13, Gegenproben, ggf. AP15 | Abbildungen ansehen, erste Deutung | Erste Ergebnisse stehen |
| 22.12.–06.01. | Puffer | | |
| ab Januar 2027 | Paper; Zahlen nur aus `results/kennzahlen.json` | | laut Kursplan |

Tipp zur Verteilung: Während die Menschen kodieren, kann Claude Code an den Paketen arbeiten, die keine Kodierung brauchen (AP02, AP03, AP08, AP14 A1/A4/A5, Basislinie in AP10, Probelauf in AP11).

---

## 11 Präzisierungen und Abweichungen gegenüber dem Exposé

Diese Punkte sind beim Planen aufgefallen. Sie sollten im Methodenteil stehen und in `docs/entscheidungen.md` übernommen werden.

1. **Neue Fragetypen sind 2026 nicht mehr ohne Votes.** Das Exposé schreibt, sie hätten „keine Votes und keine akzeptierte Antwort“. In den Daten stimmt das für Oktober 2025 (Fragen mit `advice`: 0 % akzeptiert, 74 % mit Score 0). Im Oktober 2026 haben sie aber Scores und akzeptierte Antworten (`best-practices`: 43 % akzeptiert, `advice`: 19 %). AP12 prüft das auf der Website; der Satz im Exposé muss für das Paper angepasst werden. Die getrennte Auswertung bleibt trotzdem sinnvoll, weil es eine andere Art von Frage ist.
2. **Kodierende sehen weder Jahr noch Tags** der 600 Fragen (AP06). Das ist strenger als im Exposé und verhindert, dass das Wissen um den Zeitpunkt die Einordnung beeinflusst.
3. **Testmenge gesperrt:** Die 150 Doppelten werden nur einmal am Ende zur Auswahl des Verfahrens genutzt (AP10).
4. **Placebo-Test 2019 → 2021** ergänzt den Permutationstest (AP07).
5. **Antwortverhalten ohne neue Fragetypen:** Das Exposé nennt den Ausschluss nur für akzeptierte Antworten. Der Plan schließt sie bei allen Antwortkennzahlen aus, weil sie anders funktionieren.
6. **Nur lokale Modelle.** Exposé 5.2 und 5.3 lassen das Verfahren offen und nennen „ein Sprachmodell ohne eigenes Training“ bzw. „Verfahren, bei denen ein Sprachmodell Themen vorschlägt“. Umgesetzt wird das mit lokalen Modellen: ein Zero-Shot-Klassifikationsmodell (AP10) und BERTopic mit lokalem Embedding-Modell gegen NMF (AP11). Themennamen vergeben die Autor:innen. Im Paper so beschreiben; Modellnamen und Revisionen kommen in den Anhang.
7. **Sichtbare Antwortende (AP14)** kommen als Kennzahlen A1–A5 hinzu. Sie stehen nicht als eigene Teilfrage im Exposé, gehören aber zu „Antwortverhalten“ (TF1) und zur „Sichtbarkeit von Wissen im Sinne von Leonardi“ in der Forschungsfrage. Begründung siehe AP14. Im Paper: Abschnitt 3c um A1–A5 ergänzen, Ergebnisse in 4a (gesamt) und 4b (je Gruppe).
8. **Vorwissen bei der Tag-Einordnung:** Nicolas kennt die Rückgänge der 40 Tags aus der Voruntersuchung. Das lässt sich nicht ungeschehen machen und gehört offen in die Grenzen. Gemildert wird es dadurch, dass nur übereinstimmende Tags in eine Gruppe kommen.

---

## 12 Risiken und Gegenmaßnahmen

| Risiko | Wirkung | Gegenmaßnahme |
|---|---|---|
| Kappa < 0,61 | Gruppen angreifbar | Kalibrierung, Leitfaden schärfen, zweite Runde; offenlegen |
| Gruppen werden sehr klein (viele „K“) | Index schwankt stark | Größe der Gruppen berichten; Permutation mit gleicher Größe macht es vergleichbar |
| Kein Verfahren erreicht Macro-F1 0,70 | Textanalyse schwach | als Hinweis deuten; Tag-Analyse bleibt Hauptbefund |
| 2025/2026 sehr klein (5.262 / 949) | große Schwankungen | Intervalle zeigen, als Bestätigung markieren |
| Tag-Brüche (Umbenennung) | falsche Rückgänge | AP03 vor jeder Tag-Zeitreihe |
| Zero-Shot-Modell zu schwach für die feine Unterscheidung G/U | Kandidat 3 fällt aus | SetFit ist meist stärker; Gewinner wird nach Macro-F1 gewählt, Ergebnis aller Kandidaten berichten |
| Lokale Modelle zu langsam | Zeitplan | Laufzeit an 200 Fragen messen, Apple-GPU nutzen, kleineres Modell (Alternative in `config.py`), über Nacht laufen lassen |
| Modellversionen ändern sich auf Hugging Face | Wiederholbarkeit | Revision (Commit-Hash) festschreiben, Modellkarte je Lauf |
| Antwortende sinken mit der Fragezahl (AP14) | Scheinbefund | nur Gruppenvergleich und Trendabweichung deuten, zusätzlich je 100 Fragen |
| Gelöschte Fragen fehlen, ältere Jahre bereinigter | Verzerrung | Gegenprobe Score ≥ 1; in den Grenzen nennen |

---

## 13 Offene Entscheidungen fürs Team

1. ~~Sprachmodell für AP10/AP11~~ **entschieden (15.11.2026): nur lokale Modelle** (D10).
2. **Format des Papers** (Word, LaTeX, Typst). Die Abbildungen gehen in jedem Fall (PDF/PNG), Tabellen werden in allen drei Formaten erzeugt.
3. **Umgang mit Tag-Brüchen** aus AP03 (zusammenlegen oder ausschließen).
4. ~~Sichtbare Antwortende~~ **entschieden (15.11.2026): fest eingeplant als AP14** (D11). Offen bleibt nur AP15 (KI-Erwähnungen, optional).
5. **Schwelle für „erkennbare Expert:innen“** (Voreinstellung ≥ 3 Antworten je Gruppe und Monat). Gegenprobe mit ≥ 2 und ≥ 5 einplanen.

---

## 14 Zuordnung zur Gliederung des Papers

| Kapitel (Exposé 9) | Inhalte aus diesem Plan |
|---|---|
| 2a Leonardi (2014) | Begründung in AP14 (Metawissen = wer weiß was; Antworten als sichtbare Signale) |
| 3a Daten und Zeitraum | Abschnitt 5.1–5.2, Datenprotokoll AP01, T9 |
| 3b Grundlagen- und Umgebungsfragen | Leitfäden, AP04–AP06, T4, T5 |
| 3c Kennzahlen | Abschnitt 5.3–5.5, A1–A5 aus AP14 |
| 3d Gruppenvergleich und Themenanalyse | AP07, AP10, AP11, T7 |
| 3e Evaluation | Abschnitt 9, T4 |
| 4a Umfang und Antwortverhalten | F01–F07, T2, T3, T10 |
| 4b Grundlagen und Umgebung | F08, F10–F12, F14, F23, T6 |
| 4c Inhalte | F17–F20, T8 |
| 5 Diskussion und Grenzen | Abschnitt 11–12, Gegenproben F05, F09, F13 |
| Anhang | T1, T5, F05, F09, F13, F15, Leitfäden, Abfragen |

---

## 15 Statusübersicht

Claude Code setzt nach jedem abgeschlossenen AP den Haken und trägt das Datum ein.

| AP | Inhalt | Status | Datum |
|---|---|---|---|
| AP00 | Einrichtung | ☑ | 15.11.2026 |
| AP01 | Datenbasis Parquet | ☑ | 15.11.2026 |
| AP02 | Kennzahlen TF1/TF3 | ☐ | |
| AP03 | Tag-Prüfung | ☐ | |
| AP04 | Kodierbögen Tags | ☐ | |
| AP05 | Kappa Tags, Gruppen | ☐ | |
| AP06 | Stichproben, Kodier-App | ☐ | |
| AP07 | Gruppenvergleich | ☐ | |
| AP08 | Unterbrochene Zeitreihe | ☐ | |
| AP09 | Doppelkodierung | ☐ | |
| AP10 | Klassifikation | ☐ | |
| AP11 | Themenanalyse | ☐ | |
| AP12 | Datenprüfung, Literatur | ☐ | |
| AP13 | Abbildungen, Tabellen | ☐ | |
| AP14 | Sichtbare Antwortende | ☐ | |
| AP15 | KI-Erwähnungen (optional) | ☐ | |

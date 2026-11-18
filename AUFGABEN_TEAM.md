# Was wir selbst machen müssen

*Stand 16.11.2026: Die Kodierung (Tags, Fragen, Themen) übernehmen zwei lokale Sprachmodelle (siehe `docs/ki_einsatz.md`). Wir prüfen nur noch Stichproben, seit 18.11.2026 blind (D29). Zusammen etwa 2 Stunden.*

Abhaken mit `[x]`. Nach jedem Schritt steht, was Claude Code danach ausführt.

**Einmalig:** im Repo-Ordner `uv sync` ausführen (für die Kodier-App reicht das).

---

## 1 Leitfäden kurz durchsehen (optional, beide, ca. 20 min)

- [ ] `docs/kodierleitfaden_tags.md` und `docs/kodierleitfaden_fragen.md` überfliegen: Passen Kategorien und Beispiele? Die Modelle bekommen genau diese Leitfäden als Anweisung.

**Wichtig für 2 und 3 (blind, D29):** Vorher keine Modell-Einordnungen ansehen (`coding/tags/llm_*`, `coding/questions/llm_*`, `data/processed/groups.json`, `results/agreement_*`) und euch erst nach dem Ausfüllen austauschen. Ihr ordnet selbst ein, verglichen wird danach automatisch.

## 2 Tags einordnen (beide, jede Person für sich, ca. 20 min)

Voraussetzung: erfüllt, die Bögen sind erzeugt.

- [ ] Person A: `coding/pruefung/tags_40_A.csv`, Spalte `kategorie` = `G`, `U` oder `K` nach `docs/kodierleitfaden_tags.md`; bei Zweifel `unsicher` = `x`
- [ ] Person B: dasselbe in `coding/pruefung/tags_40_B.csv` (gleiche Tags, andere Reihenfolge)

## 3 Fragen einordnen (eine Person oder aufgeteilt, ca. 60 min)

- [ ] Kodier-App (`uv run marimo run notebooks/kodier_app.py`): 100 Fragen, je Frage G, U oder S wählen, bei Zweifel „unsicher“ ankreuzen

Danach führt Claude Code `scripts/17_pruefung.py auswerten` und AP07 erneut aus.

## 4 Themen durchsehen (beide, ca. 15 min)

Voraussetzung: Claude Code hat AP11 mit Benennung und Prüfung durch die Modelle ausgeführt.

- [ ] `results/topics/themen.md`: Sind die Themennamen verständlich und plausibel? Auffälligkeiten kurz notieren.

## 5 Ergebnisse durchsehen (beide, ca. 15 min)

- [ ] `docs/ki_einsatz.md`: Tabelle „Ergebnisse der Prüfung“ ansehen. Sind die Kappa-Werte plausibel? (`results/pruefung.md`)
- [ ] `results/checks.md`: automatischer Abgleich von 20 Fragen mit der API

## 6 Offene Entscheidungen

- [ ] Schwelle für „erkennbare Expert:innen“: ≥ 3 Antworten (Gegenproben 2 und 5). Passt das?
- [ ] AP15 (KI-Erwähnungen im Fragetext) machen oder weglassen?
- [ ] Format des Papers (Word, LaTeX, Typst)

## 7 Fürs Paper

- **Methodentext und Erklärung zum KI-Einsatz:** Textbausteine in `docs/ki_einsatz.md`
- **Modellwahl mit Literatur:** `docs/modellwahl.md`
- **Abweichungen vom Exposé:** `plan.md` Abschnitt 11 (269 statt 272 Tags, 24 statt 26 KI-Tags, neue Fragetypen ab 1.10.2025, sichtbare Antwortende, Kodierung durch Modelle)

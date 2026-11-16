# Was wir selbst machen müssen

*Stand 16.11.2026: Die Kodierung (Tags, Fragen, Themen) übernehmen zwei lokale Sprachmodelle (siehe `docs/ki_einsatz.md`). Wir prüfen nur noch Stichproben. Zusammen etwa 1,5 Stunden.*

Abhaken mit `[x]`. Nach jedem Schritt steht, was Claude Code danach ausführt.

**Einmalig:** im Repo-Ordner `uv sync` ausführen (für die Kodier-App reicht das).

---

## 1 Leitfäden kurz durchsehen (optional, beide, ca. 20 min)

- [ ] `docs/kodierleitfaden_tags.md` und `docs/kodierleitfaden_fragen.md` überfliegen: Passen Kategorien und Beispiele? Die Modelle bekommen genau diese Leitfäden als Anweisung.

## 2 Tags prüfen (eine Person, ca. 15 min)

Voraussetzung: Claude Code hat AP16 (Tags) und AP05 ausgeführt.

- [ ] `coding/pruefung/tags_40.csv`: je Tag die Einordnung der Modelle ansehen, Spalte `stimmt` = `j` oder `n`

## 3 Fragen prüfen (eine Person oder aufgeteilt, ca. 45 min)

Voraussetzung: Claude Code hat AP16 (Fragen) und AP09 ausgeführt.

- [ ] Kodier-App im Prüfmodus (`uv run marimo run notebooks/kodier_app.py`): 100 Fragen, je Frage `stimmt` ja/nein

## 4 Themen durchsehen (beide, ca. 15 min)

Voraussetzung: Claude Code hat AP11 mit Benennung und Prüfung durch die Modelle ausgeführt.

- [ ] `results/topics/themen.md`: Sind die Themennamen verständlich und plausibel? Auffälligkeiten kurz notieren.

## 5 Ergebnisse durchsehen (beide, ca. 15 min)

- [ ] `docs/ki_einsatz.md`: Tabelle „Ergebnisse der Prüfung“ ansehen. Sind Kappa und Zustimmung plausibel?
- [ ] `results/checks.md`: automatischer Abgleich von 20 Fragen mit der API

## 6 Offene Entscheidungen

- [ ] Schwelle für „erkennbare Expert:innen“: ≥ 3 Antworten (Gegenproben 2 und 5). Passt das?
- [ ] AP15 (KI-Erwähnungen im Fragetext) machen oder weglassen?
- [ ] Format des Papers (Word, LaTeX, Typst)

## 7 Fürs Paper

- **Methodentext und Erklärung zum KI-Einsatz:** Textbausteine in `docs/ki_einsatz.md`
- **Modellwahl mit Literatur:** `docs/modellwahl.md`
- **Abweichungen vom Exposé:** `plan.md` Abschnitt 11 (269 statt 272 Tags, 24 statt 26 KI-Tags, neue Fragetypen ab 1.10.2025, sichtbare Antwortende, Kodierung durch Modelle)

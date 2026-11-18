# Was wir selbst machen müssen

*Stand 18.11.2026: Einordnen und Prüfen übernehmen lokale Sprachmodelle: zwei kodieren (Qwen, Phi-4), ein drittes prüft den Konsens (Ministral 3, D30). Wir ordnen nichts selbst ein (mit der Betreuerin abgesprochen). Übrig bleibt Durchsehen und Entscheiden.*

Abhaken mit `[x]`.

---

## 1 Leitfäden kurz durchsehen (optional, ca. 20 min)

- [ ] `docs/kodierleitfaden_tags.md` und `docs/kodierleitfaden_fragen.md` überfliegen: Passen Kategorien und Beispiele? Die Modelle bekommen genau diese Leitfäden als Anweisung.

## 2 Methodenteil: fehlende menschliche Prüfung

- [ ] Im Paper offen nennen, dass keine Person die Einordnungen geprüft hat (Textbausteine in `docs/ki_einsatz.md`) und dass dies mit der Betreuerin abgesprochen ist.

## 3 Ergebnisse durchsehen (beide, ca. 15 min)

- [ ] `docs/ki_einsatz.md`: Tabelle „Ergebnisse der Prüfung“ ansehen (Prüfung durch Ministral bestanden: Tags κ 0,85, Fragen κ 0,82; `results/pruefung.md`)
- [ ] `results/checks.md`: automatischer Abgleich von 20 Fragen und 10 Antworten mit der API (alle Abweichungen erklärt)
- [ ] Literaturabgleich in `results/checks.md`: die Zahlen aus Burtch et al. (2024) und del Rio-Chanona et al. (2024) hat Claude Code aus den Originalen entnommen. Vor dem Zitieren im Paper kurz an den Originalen prüfen (ca. 10 min).

## 4 Offene Entscheidungen

- [ ] Schwelle für „erkennbare Expert:innen“: ≥ 3 Antworten (Gegenproben 2 und 5). Passt das?
- [ ] AP15 (KI-Erwähnungen im Fragetext) machen oder weglassen?
- [ ] Format des Papers (Word, LaTeX, Typst)

## 7 Fürs Paper

- **Methodentext und Erklärung zum KI-Einsatz:** Textbausteine in `docs/ki_einsatz.md`
- **Modellwahl mit Literatur:** `docs/modellwahl.md`
- **Abweichungen vom Exposé:** `plan.md` Abschnitt 11 (269 statt 272 Tags, 24 statt 26 KI-Tags, neue Fragetypen ab 1.10.2025, sichtbare Antwortende, Kodierung durch Modelle)

---
description: Setzt ein Arbeitspaket aus plan.md um (z. B. /ap AP01)
argument-hint: APxx
---

Setze das Arbeitspaket **$ARGUMENTS** aus `plan.md` um.

1. Lies `CLAUDE.md` und in `plan.md` die Abschnitte 5 (Definitionen) und 6 (das Arbeitspaket $ARGUMENTS) sowie die Abbildungen/Tabellen aus Abschnitt 7–8, die dieses AP betreffen.
2. Prüfe, ob die Eingaben des AP vorhanden sind (Ausgaben vorheriger APs, ausgefüllte Kodierbögen). Fehlt etwas, sag genau was, und hör auf.
3. Lege eine Aufgabenliste an. Schreibe zuerst die Tests für die Definitionen, dann den Code in `src/sov/`, dann das Skript in `scripts/` und das Makefile-Ziel.
4. Führe das Skript aus und prüfe jedes Akzeptanzkriterium einzeln. Nenne Kriterien, die nicht erfüllt oder nicht prüfbar sind, ausdrücklich.
5. Methodische Entscheidungen, die der Plan offenlässt: kurz nachfragen, wenn sie Ergebnisse verändern; sonst die naheliegende Wahl treffen und in `docs/entscheidungen.md` eintragen.
6. Hake das AP in `plan.md` Abschnitt 15 ab (mit Datum) und fasse in 3–5 Sätzen zusammen: was entstanden ist, zentrale Zahlen, was offen ist.

Beachte die harten Regeln aus `CLAUDE.md` (keine menschlichen Labels ausfüllen, Testmenge gesperrt, keine kostenpflichtigen LLM-Läufe ohne Bestätigung).

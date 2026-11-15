# Entscheidungsprotokoll

Jede methodische Entscheidung mit Datum, Begründung und verworfener Alternative. Grundlage für das Methodenkapitel und die Grenzen. Neue Einträge unten anhängen.

| Nr. | Datum | Entscheidung | Begründung | Verworfene Alternative |
|---|---|---|---|---|
| D01 | 15.11.2026 | Antworten nur im Fenster 0–7 Tage nach der Frage | Oktober 2026 hatte beim Download (ab 11.11.) nur so viel Vorlauf; heutige `answer_count` bevorzugt alte Fragen | heutige Antwortzahl; 30-Tage-Fenster |
| D02 | 15.11.2026 | Neue Fragetypen = Tag `advice` oder `best-practices` **und** gestellt ab 1.10.2025 | die API liefert kein Feld für den Fragetyp; beide Tags kommen vorher vereinzelt als normale Tags vor (13 Fragen 2008–2020, AP01-Protokoll), die bleiben klassisch | nur Tag (hätte 13 alte Fragen falsch ausgeschlossen); Erkennung über Score/Antworten |
| D03 | 15.11.2026 | Neue Fragetypen bei allen Antwortkennzahlen ausgeschlossen, getrennt berichtet | funktionieren anders (2025 ohne Votes und Akzeptanz); Anteil 2026 ≈ 7 % würde die Reihe verzerren | nur bei akzeptierten Antworten ausschließen (Exposé) |
| D04 | 15.11.2026 | Fortschreibung des Trends 2015–2022 als Hauptauswertung der unterbrochenen Zeitreihe; segmentierte Regression ergänzend | nur 4 Punkte nach dem Schnitt, davon 2 als Bestätigung | nur segmentierte Regression |
| D05 | 15.11.2026 | Kodieransicht der Fragen ohne Jahr, Tags und Score | Einordnung soll nicht vom Wissen um Zeitpunkt oder Tag beeinflusst werden; gleiche Information wie das Verfahren | volle Ansicht wie auf der Website |
| D06 | 15.11.2026 | Die 150 doppelt kodierten Fragen sind Testmenge, nur einmal je Kandidat ausgewertet | sonst Überanpassung an die Testmenge | Kreuzvalidierung über alle 600 |
| D07 | 15.11.2026 | Fragen mit Tags beider Gruppen zählen in beiden; Gegenprobe mit nur einer Gruppe | entspricht der Voruntersuchung; Gegenprobe zeigt, ob Überschneidung das Ergebnis trägt | Überschneidungen ausschließen |
| D08 | 15.11.2026 | Placebo-Test 2019 = 100 gegen 2021 | zeigt, wie groß Abstände ohne ChatGPT-Schnitt ausfallen | keiner |
| D09 | 15.11.2026 | Seed 20261116 für alle Stichproben | Reproduzierbarkeit | |
| D10 | 15.11.2026 | Nur lokale Modelle: TF-IDF + logistische Regression, SetFit, Zero-Shot-Modell (AP10); BERTopic mit lokalem Embedding-Modell gegen NMF (AP11); Themennamen vergeben die Autor:innen | keine Kosten, Fragetexte verlassen den Rechner nicht, mit fester Modellrevision exakt wiederholbar; Modelle sind für Klassifikation bzw. Themenmodellierung gebaut | Cloud-Sprachmodelle (Claude, GPT) für Einordnung, Themenvorschläge und Themennamen |
| D11 | 15.11.2026 | Sichtbare Antwortende (A1–A5) fest eingeplant (AP14) | misst Leonardis Metawissen („wer weiß was“) direkt; prüft die Schlussfolgerung aus Exposé 7; fällt unter „Antwortverhalten“ der Forschungsfrage; keine neuen Daten nötig | nur Fragen auswerten |
| D12 | 15.11.2026 | Erkennbare Expert:innen = ≥ 3 Antworten auf Fragen derselben Gruppe im selben Oktober; Gegenproben ≥ 2 und ≥ 5 | eine einzelne Antwort ist ein schwaches Signal, Wiederholung macht Kompetenz für Mitlesende erkennbar | Reputation (nur heutiger Wert verfügbar) |
| D13 | 15.11.2026 | Textlänge: `<pre>`-Blöcke entfernt, Inline-`<code>` bleibt Text, Text der HTML-Elemente mit Leerzeichen verbunden, Leerraum zusammengefasst (selectolax/Lexbor) | reproduziert die Mediane des Projektstands auf ±2 Zeichen in allen 19 Jahren | Inline-Code ebenfalls entfernen |
| D14 | 15.11.2026 | Zeit bis zur ersten Antwort (`first_answer_hours`) über alle Antworten mit Abstand ≥ 0; K4 nutzt nur Fragen mit Antwort im Fenster | so ist K4 sauber auf das Fenster beschränkt, das Feld bleibt für Verteilungen (F06) vollständig | nur Fenster-Antworten speichern |
| | | *offen: Umgang mit Tag-Brüchen aus AP03* | | |

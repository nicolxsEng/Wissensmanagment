# KI-Einsatz im Projekt – zentrale Übersicht

*Stand: 18.11.2026. Diese Datei ist die **eine** Stelle, an der festgehalten ist, welche Schritte KI-Werkzeuge übernommen haben und welche die Autor:innen. Sie ist die Grundlage für den Methodenteil und für eine Erklärung zum KI-Einsatz in der schriftlichen Ausarbeitung. Bei Änderungen bitte hier nachtragen.*

## Entscheidung

In Absprache mit der Betreuerin (Gespräch vom 16.11.2026) werden die im Exposé als menschliche Kodierung geplanten Schritte **automatisiert**, weil der Aufwand für den Kurs zu groß wäre. Seit 18.11.2026 (erneute Absprache, D30) ordnen die Autor:innen **nichts selbst ein und prüfen keine Einordnungen**; den Konsens der beiden Kodiermodelle prüft ein drittes lokales Modell eines anderen Entwicklers (Ministral 3 14B) nach vorab festgelegten Kriterien (D29). Der Aufbau aus dem Exposé (Leitfaden, zwei unabhängige Kodierinstanzen, Cohens Kappa, Prüfung, Gegenproben) bleibt erhalten; die Kodierinstanzen sind zwei lokale Sprachmodelle. Begründung der Modellwahl: [modellwahl.md](modellwahl.md).

## Wer hat was gemacht

| Arbeitsschritt | durchgeführt von | Werkzeug / Modell | Kontrolle |
|---|---|---|---|
| Fragestellung, Exposé, Theorie (Leonardi), Deutung | Autor:innen | – | – |
| Datenerhebung über die Stack Exchange API | Skripte | Python | Abgleich mit Zählabfragen der API |
| Planung der Auswertung, Programmierung aller Skripte | Autor:innen mit KI-Assistenz | Claude Code (Anthropic) | Durchsicht der Pläne und Ergebnisse |
| Kennzahlen, Zeitreihen, Abbildungen | Skripte | Python (Polars, statsmodels, matplotlib) | Durchsicht der Abbildungen |
| Kodierleitfäden (Tags, Fragen) | Autor:innen mit KI-Assistenz | Claude Code (Entwurf) | Durchsicht, Festlegung |
| Anweisungen (Prompts) für die Modelle, Kalibrierung an 10 Übungstags und 30 Kalibrierungsfragen | KI-Assistenz | Claude Code (Prompts aus den Leitfäden, Analyse der Abweichungen) | Durchsicht der Kalibrierungsberichte (`results/llm/bericht_kal-*`) |
| Einordnung der 269 Tags (G/U/K) | zwei lokale Sprachmodelle | Qwen3.5-9B, Phi-4 14B | Prüfmodell Ministral 3 14B: 40 Tags (alle 14 U + 26 zufällige G); keine menschliche Prüfung |
| Einordnung der 630 Fragetexte (G/U/S) | zwei lokale Sprachmodelle | Qwen3.5-9B, Phi-4 14B | Prüfmodell Ministral 3 14B: 100 zufällige Konsensfragen; keine menschliche Prüfung |
| Automatische Einordnung von ~22.800 Fragen | Klassifikator, trainiert auf den Modell-Labels | TF-IDF/SetFit/Zero-Shot (lokal) | Macro-F1 auf 150 Testfragen (Modellkonsens) |
| Themen bilden | Themenmodell | BERTopic bzw. NMF (lokal) | – |
| Themen benennen | lokales Sprachmodell | Qwen3.5-9B | Prüfung durch zwei Modelle (nächste Zeile); keine menschliche Durchsicht |
| Themen prüfen (10 Titel je Thema) | zwei lokale Sprachmodelle | Qwen3.5-9B, Phi-4 14B | – |
| Datenprüfung (20 Fragen gegen die Website) | Skript (erneute API-Abfrage) | Python | Durchsicht der Abweichungen |
| Schreiben der Ausarbeitung | Autor:innen | *bitte selbst ergänzen, falls KI-Werkzeuge genutzt werden* | – |

Alle Sprachmodelle laufen lokal (Ollama), keine Texte wurden an externe KI-Dienste gegeben. Ursprünglich war OLMo-3-7B-Instruct als zweite Kodierinstanz vorgesehen; es schied in der Kalibrierung aus, weil seine Begründungen seinen Einordnungen widersprachen, und wurde durch Phi-4 ersetzt (D24, `docs/modellwahl.md`). Modellversionen, Einstellungen und Rohantworten: `results/llm_modelle.json`, `results/llm/`. Im vollen Lauf erzeugte Qwen bei einer Frage (F306) Endlostext; danach wurde die Antwortlänge auf 512 Token begrenzt (gültige Antworten sind kürzer als 100 Token), F306 bleibt ohne gültige Einordnung.

## Ergebnisse der Prüfung

| Prüfung | Wert |
|---|---|
| Kappa Tags (Qwen ↔ Phi-4) | Runde 1 (Prompt v1): **0,37** [0,28; 0,45], 58 % – Runde 2 (Leitfaden v0.2, Prompt v3, vorab als endgültig festgelegt, D25): **0,22** [0,11; 0,33], 66 %. Kriterium 0,61 in beiden Runden nicht erfüllt. Gruppen (Runde 2, nur übereinstimmende Tags): G 155, U 14, beide K 9. Hauptgrund: Phi-4 hält die Sprachregel oft nicht ein (z. B. javascript, c#, php → G statt K); die geschätzten G-Anteile beider Modelle korrelieren hoch (Spearman 0,81), Phi-4 liegt im Mittel 11 Punkte tiefer. `results/agreement_tags.md`, Runde 1: `results/agreement_tags_v1.md` |
| Prüfung durch dritte Modellfamilie, 40 Tags (Ministral 3 14B, D29/D30: alle 14 U- und 26 zufällige G-Tags; bestätigt bei κ ≥ 0,61 und je Gruppe ≥ 80 % gleich; keine menschliche Prüfung) | **κ = 0,85** [0,67; 1,00], 92 %; G 23/26 gleich (88 %, KI 71–96 %), U 14/14 (100 %, KI 78–100 %) → **Kriterium erfüllt, Gruppen bestätigt.** Beschreibend über alle 169 Gruppen-Tags: κ = 0,76, G 147/155, U 14/14. Mit den einzelnen Kodiermodellen über alle 269 Tags nur κ = 0,46 (Qwen) bzw. 0,59 (Phi-4): Die Prüfinstanz bestätigt die Tags, bei denen sich die beiden einig waren; die strittigen Tags ordnet auch sie uneinheitlich ein. Gegenprobe „pruef“ in AP07 (147 G / 14 U): Abstand 2024 +44,7 statt +44,4. `results/pruefung.md`, `results/groups.md` |
| Kappa Fragen (Qwen ↔ Phi-4) | **0,55** [0,49; 0,61], Übereinstimmung 76 % (599 Fragen; F306 ohne gültige Antwort von Qwen) – Kriterium 0,61 knapp nicht erfüllt. Konsens: 456 Fragen (G 272, U 168, S 16). `results/agreement_questions.md` |
| Prüfung durch dritte Modellfamilie, 100 Fragen (Ministral 3 14B, D29/D30; bestätigt bei κ ≥ 0,61) | **κ = 0,82** [0,70; 0,93], 91 %; G 57/59 (97 %), U 31/38 (82 %, KI 67–91 %), S 3/3 → **Kriterium erfüllt, Referenz für AP10 bestätigt.** Beschreibend über alle 456 Konsensfragen: κ = 0,75, 88 % (U 80 %). Mit den einzelnen Kodiermodellen über alle 600 Fragen κ = 0,52 (Qwen) bzw. 0,63 (Phi-4). 0 ungültige Antworten. `results/pruefung.md` |
| Themen bestanden (beide Modelle ≥ 8/10) | Probelauf (1.008 Titel): BERTopic 1/21, NMF 1/21, unentschieden (κ Prüfung 0,69). Hauptlauf (10.584 Titel, je 30 Themen, Regel D28 vorab): **BERTopic 1/30 (3 %)**, NMF 0/30; mittlere Passung je 22 %; κ der Prüfung 0,60 bzw. 0,50. Gewinner BERTopic; Kriterium ≥ 80 % **nicht erfüllt** → Themenanalyse nur als Hinweis. Ursache laut Prüftiteln: Die Themen sind breit gemischt (typische Titel einheitlich, Zufallstitel nicht); die Urteile der Modelle sind nachvollziehbar. `results/topics/themen.md`, `results/topics/probelauf_bewertung.md` |
| Macro-F1 bestes Klassifikationsverfahren | **SetFit 0,76** [0,56; 0,94], Genauigkeit 88 % (121 Testfragen, je Kandidat einmal ausgewertet); TF-IDF 0,58, Zero-Shot 0,51. Kriterium 0,70 erfüllt, die untere Intervallgrenze liegt aber darunter, weil nur 3 S-Testfragen vorliegen (F1 S 0,50). Nur G/U: 0,89. Angewendet auf 22.829 Fragen. `results/classify/bericht.md`, `results/classify/modell.md` |

## Textbausteine für die Ausarbeitung

*Zahlen in eckigen Klammern nach Abschluss der Auswertung ersetzen. Wortlaut frei anpassen.*

**Methode – Grundlagen- und Umgebungsfragen (3b):**
> Die 269 Tags mit mindestens 150 Fragen im Oktober 2022 wurden nach einem Kodierleitfaden (Anhang A) als Grundlagen-, Umgebungs- oder nicht eindeutige Tags eingeordnet. Die Einordnung übernahmen zwei lokal betriebene Sprachmodelle unterschiedlicher Entwickler (Qwen3.5-9B, Phi-4 14B) unabhängig voneinander, mit identischer Anweisung, Temperatur 0 und festem Seed. In die Gruppen gingen nur Tags ein, die beide Modelle gleich einordneten (Cohens κ = 0,22; 155 Grundlagen- und 14 Umgebungs-Tags). Zur Prüfung ordnete ein drittes Sprachmodell eines anderen Entwicklers (Ministral 3 14B, Mistral AI) mit derselben Anweisung 40 Tags ein (alle 14 Umgebungs-Tags und 26 zufällige Grundlagen-Tags), ohne die Einordnung der beiden anderen Modelle zu kennen (κ = 0,85; gleich eingeordnet: Grundlagen 88 %, Umgebung 100 %). Kriterien und Folgen waren vor der Prüfung festgelegt. Die geringe Übereinstimmung der beiden Kodiermodelle betrifft vor allem die Tags, die nicht in die Gruppen eingingen; diese ordnete auch das dritte Modell uneinheitlich ein. Eine Prüfung durch Menschen fand nicht statt; da Sprachmodelle gemeinsame Verzerrungen haben können, ist das eine Grenze der Arbeit.

**Methode – Einordnung von Fragetexten (3d):**
> Für den Gruppenvergleich ohne Tags wurden 600 Fragen (50 je Oktober 2015–2026) und 30 weitere Fragen nach einem zweiten Leitfaden (Anhang B) von denselben beiden Modellen eingeordnet (κ = 0,55). Übereinstimmend eingeordnete Fragen dienten als Referenz für drei Klassifikationsverfahren. Das Verfahren mit dem besten Macro-F1 (SetFit, 0,76) ordnete anschließend 22.829 Fragen ein. Dasselbe dritte Modell ordnete 100 zufällige Referenzfragen ein (κ = 0,82, Übereinstimmung 91 %); eine Prüfung durch Menschen fand nicht statt.

**Methode – Themen (3d):**
> Die Themen der Fragetitel wurden mit BERTopic und NMF gebildet; ausgewählt wurde nach einer vorab festgelegten Regel BERTopic. Ein lokales Sprachmodell benannte jedes Thema anhand der Schlüsselwörter und fünf typischer Titel; beide Modelle prüften je Thema zehn weitere, zufällig gezogene Titel auf Passung. Ein Thema galt als bestätigt, wenn beide Modelle mindestens acht von zehn Titeln als passend einstuften (1 von 30 Themen). Die Themenanalyse wird deshalb nur als Hinweis gedeutet.

**Evaluation (3e), ein Satz:**
> Weil die Einordnung automatisiert erfolgte, wurde die Übereinstimmung zweier unabhängiger Modelle (Cohens κ) gemessen und ihr Konsens an Stichproben durch ein drittes Modell eines anderen Entwicklers geprüft, nach vorab festgelegten Kriterien; eine Prüfung an menschlichen Urteilen, wie sie Pangakis et al. (2023) empfehlen, fand nicht statt.

**Grenzen (5):**
> Die Einordnungen stammen ausschließlich von Sprachmodellen; keine Person hat sie geprüft (mit der Betreuerin abgesprochen). Sprachmodelle können systematische Fehler teilen; drei Modelle von drei Entwicklern mildern dies, schließen es aber nicht aus. Das dritte Modell bestätigte den Konsens der beiden Kodiermodelle, stimmte mit jedem einzelnen aber nur mäßig überein (κ 0,46–0,63); die Gruppen beruhen daher auf den eindeutigeren Fällen.

**Erklärung zum KI-Einsatz (Vorlage, an die Vorgaben der Hochschule anpassen):**
> Für die Programmierung der Auswertungsskripte und die Planung der Auswertung wurde Claude Code (Anthropic) eingesetzt. Die Einordnung von Tags und Fragetexten sowie die Benennung und Prüfung von Themen erfolgte durch lokal betriebene Sprachmodelle (Qwen3.5-9B, Phi-4 14B); ihr Konsens wurde an Stichproben durch ein drittes lokales Modell (Ministral 3 14B) geprüft. Eine Prüfung durch die Autor:innen fand nicht statt. [Ergänzen: Einsatz von KI beim Schreiben des Textes, falls zutreffend.]

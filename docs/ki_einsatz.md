# KI-Einsatz im Projekt – zentrale Übersicht

*Stand: 16.11.2026. Diese Datei ist die **eine** Stelle, an der festgehalten ist, welche Schritte KI-Werkzeuge übernommen haben und welche die Autor:innen. Sie ist die Grundlage für den Methodenteil und für eine Erklärung zum KI-Einsatz in der schriftlichen Ausarbeitung. Bei Änderungen bitte hier nachtragen.*

## Entscheidung

In Absprache mit der Betreuerin (Gespräch vom 16.11.2026) werden die im Exposé als menschliche Kodierung geplanten Schritte **automatisiert**, weil der Aufwand für den Kurs zu groß wäre. Die Autor:innen **prüfen** die Ergebnisse stichprobenartig. Der Aufbau aus dem Exposé (Leitfaden, zwei unabhängige Kodierinstanzen, Cohens Kappa, Prüfung, Gegenproben) bleibt erhalten; die Kodierinstanzen sind zwei lokale Sprachmodelle. Begründung der Modellwahl: [modellwahl.md](modellwahl.md).

## Wer hat was gemacht

| Arbeitsschritt | durchgeführt von | Werkzeug / Modell | Kontrolle durch die Autor:innen |
|---|---|---|---|
| Fragestellung, Exposé, Theorie (Leonardi), Deutung | Autor:innen | – | – |
| Datenerhebung über die Stack Exchange API | Skripte | Python | Abgleich mit Zählabfragen der API |
| Planung der Auswertung, Programmierung aller Skripte | Autor:innen mit KI-Assistenz | Claude Code (Anthropic) | Durchsicht der Pläne und Ergebnisse |
| Kennzahlen, Zeitreihen, Abbildungen | Skripte | Python (Polars, statsmodels, matplotlib) | Durchsicht der Abbildungen |
| Kodierleitfäden (Tags, Fragen) | Autor:innen mit KI-Assistenz | Claude Code (Entwurf) | Durchsicht, Festlegung |
| Anweisungen (Prompts) für die Modelle, Kalibrierung an 10 Übungstags und 30 Kalibrierungsfragen | KI-Assistenz | Claude Code (Prompts aus den Leitfäden, Analyse der Abweichungen) | Durchsicht der Kalibrierungsberichte (`results/llm/bericht_kal-*`) |
| Einordnung der 269 Tags (G/U/K) | zwei lokale Sprachmodelle | Qwen3.5-9B, Phi-4 14B | Prüfung von 40 zufälligen Tags |
| Einordnung der 630 Fragetexte (G/U/S) | zwei lokale Sprachmodelle | Qwen3.5-9B, Phi-4 14B | Prüfung von 100 zufälligen Fragen |
| Automatische Einordnung von ~22.800 Fragen | Klassifikator, trainiert auf den Modell-Labels | TF-IDF/SetFit/Zero-Shot (lokal) | über die geprüften Fragen |
| Themen bilden | Themenmodell | BERTopic bzw. NMF (lokal) | – |
| Themen benennen | lokales Sprachmodell | Qwen3.5-9B | Durchsicht der Themenliste |
| Themen prüfen (10 Titel je Thema) | zwei lokale Sprachmodelle | Qwen3.5-9B, Phi-4 14B | Durchsicht |
| Datenprüfung (20 Fragen gegen die Website) | Skript (erneute API-Abfrage) | Python | Durchsicht der Abweichungen |
| Schreiben der Ausarbeitung | Autor:innen | *bitte selbst ergänzen, falls KI-Werkzeuge genutzt werden* | – |

Alle Sprachmodelle laufen lokal (Ollama), keine Texte wurden an externe KI-Dienste gegeben. Ursprünglich war OLMo-3-7B-Instruct als zweite Kodierinstanz vorgesehen; es schied in der Kalibrierung aus, weil seine Begründungen seinen Einordnungen widersprachen, und wurde durch Phi-4 ersetzt (D24, `docs/modellwahl.md`). Modellversionen, Einstellungen und Rohantworten: `results/llm_modelle.json`, `results/llm/`. Im vollen Lauf erzeugte Qwen bei einer Frage (F306) Endlostext; danach wurde die Antwortlänge auf 512 Token begrenzt (gültige Antworten sind kürzer als 100 Token), F306 bleibt ohne gültige Einordnung.

## Ergebnisse der Prüfung (werden automatisch bzw. nach der Prüfung eingetragen)

| Prüfung | Wert |
|---|---|
| Kappa Tags (Qwen ↔ Phi-4) | Runde 1 (Prompt v1): **0,37** [0,28; 0,45], 58 % – Runde 2 (Leitfaden v0.2, Prompt v3, vorab als endgültig festgelegt, D25): **0,22** [0,11; 0,33], 66 %. Kriterium 0,61 in beiden Runden nicht erfüllt. Gruppen (Runde 2, nur übereinstimmende Tags): G 155, U 14, beide K 9. Hauptgrund: Phi-4 hält die Sprachregel oft nicht ein (z. B. javascript, c#, php → G statt K); die geschätzten G-Anteile beider Modelle korrelieren hoch (Spearman 0,81), Phi-4 liegt im Mittel 11 Punkte tiefer. `results/agreement_tags.md`, Runde 1: `results/agreement_tags_v1.md` |
| Zustimmung der Autor:innen, 40 Tags | *folgt* |
| Kappa Fragen (Qwen ↔ Phi-4) | **0,55** [0,49; 0,61], Übereinstimmung 76 % (599 Fragen; F306 ohne gültige Antwort von Qwen) – Kriterium 0,61 knapp nicht erfüllt. Konsens: 456 Fragen (G 272, U 168, S 16). `results/agreement_questions.md` |
| Zustimmung der Autor:innen, 100 Fragen | *folgt* |
| Themen bestanden (beide Modelle ≥ 8/10) | *folgt (AP11)* |
| Macro-F1 bestes Klassifikationsverfahren | *folgt (AP10)* |

## Textbausteine für die Ausarbeitung

*Zahlen in eckigen Klammern nach Abschluss der Auswertung ersetzen. Wortlaut frei anpassen.*

**Methode – Grundlagen- und Umgebungsfragen (3b):**
> Die 269 Tags mit mindestens 150 Fragen im Oktober 2022 wurden nach einem Kodierleitfaden (Anhang A) als Grundlagen-, Umgebungs- oder nicht eindeutige Tags eingeordnet. Die Einordnung übernahmen zwei lokal betriebene Sprachmodelle unterschiedlicher Entwickler (Qwen3.5-9B, Phi-4 14B) unabhängig voneinander, mit identischer Anweisung, Temperatur 0 und festem Seed. In die Gruppen gingen nur Tags ein, die beide Modelle gleich einordneten (Cohens κ = [x]). Die Autor:innen prüften eine Zufallsstichprobe von 40 Tags und stimmten in [x] Fällen zu.

**Methode – Einordnung von Fragetexten (3d):**
> Für den Gruppenvergleich ohne Tags wurden 600 Fragen (50 je Oktober 2015–2026) und 30 weitere Fragen nach einem zweiten Leitfaden (Anhang B) von denselben beiden Modellen eingeordnet (κ = [x]). Übereinstimmend eingeordnete Fragen dienten als Referenz für drei Klassifikationsverfahren. Das Verfahren mit dem besten Macro-F1 ([x]) ordnete anschließend [x] Fragen ein. Die Autor:innen prüften 100 zufällige Fragen (Zustimmung [x] %).

**Methode – Themen (3d):**
> Die Themen der Fragetitel wurden mit [BERTopic/NMF] gebildet. Ein lokales Sprachmodell benannte jedes Thema anhand der Schlüsselwörter und fünf typischer Titel; beide Modelle prüften je Thema zehn weitere, zufällig gezogene Titel auf Passung. Ein Thema galt als bestätigt, wenn beide Modelle mindestens acht von zehn Titeln als passend einstuften ([x] von [y] Themen). Die Autor:innen sahen die Themenliste durch.

**Evaluation (3e), ein Satz:**
> Weil die Einordnung automatisiert erfolgte, wurde die Übereinstimmung zweier unabhängiger Modelle (Cohens κ) gemessen und die Einordnung zusätzlich stichprobenartig durch die Autor:innen geprüft (Pangakis et al. 2023).

**Grenzen (5):**
> Die Einordnungen stammen von Sprachmodellen und wurden nur stichprobenartig von Menschen geprüft. Sprachmodelle können systematische Fehler teilen; die Verwendung zweier Modelle unterschiedlicher Entwickler mildert dies, schließt es aber nicht aus.

**Erklärung zum KI-Einsatz (Vorlage, an die Vorgaben der Hochschule anpassen):**
> Für die Programmierung der Auswertungsskripte und die Planung der Auswertung wurde Claude Code (Anthropic) eingesetzt. Die Einordnung von Tags und Fragetexten sowie die Benennung und Prüfung von Themen erfolgte durch lokal betriebene Sprachmodelle (Qwen3.5-9B, Phi-4 14B), deren Ergebnisse die Autor:innen stichprobenartig geprüft haben. [Ergänzen: Einsatz von KI beim Schreiben des Textes, falls zutreffend.]

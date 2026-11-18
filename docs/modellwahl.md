# Modellwahl für die automatische Einordnung (Begründung)

*Stand: 16.11.2026. Grundlage für den Methodenteil (Kapitel 3b, 3d, 3e). Zusammenfassung des KI-Einsatzes: [ki_einsatz.md](ki_einsatz.md).*

## Aufgabe

Ein Sprachmodell soll die Schritte übernehmen, die im Exposé zwei menschliche Kodierende vorsehen:

1. 269 Tags als Grundlagen (G), Umgebung (U) oder keine (K) einordnen (AP05)
2. 630 Fragetexte als G, U oder Sonstige (S) einordnen (AP06/AP09)
3. Themen der Titel benennen und je Thema 10 Titel auf Passung prüfen (AP11)

Grundlage ist jeweils derselbe Kodierleitfaden wie für Menschen (`docs/kodierleitfaden_*.md`).

## Kriterien

| Nr. | Kriterium | Begründung |
|---|---|---|
| K1 | **Lokal ausführbar, offene Gewichte** | Ergebnisse bleiben nachvollziehbar, weil sich ein festes Modell nicht unbemerkt ändert. Keine Weitergabe der Texte, keine Kosten (D10). Offene Modelle werden für Forschung ausdrücklich empfohlen, proprietäre brauchen eine eigene Begründung (Spirling 2023; Palmer, Smith & Spirling 2024). |
| K2 | **Freie Lizenz** | Nutzung und Weitergabe der Ergebnisse ohne Einschränkung, z. B. Apache 2.0. |
| K3 | **Passt auf die Hardware** | Apple M4 mit 24 GB gemeinsamem Speicher: etwa ≤ 10 Mrd. Parameter in 4-Bit-Quantisierung, damit ein Durchlauf über 630 Fragen in unter einer Stunde möglich ist. |
| K4 | **Aktuelle Generation mit dokumentierter Leistung** | Instruktionsmodelle der neuesten Generation folgen Kodieranweisungen deutlich besser als ältere; Leistung ist im Technical Report bzw. der Modellkarte dokumentiert. |
| K5 | **Transparenz der Trainingsdaten** | Je offener das Training, desto besser lässt sich prüfen, ob ein Modell Inhalte kennt, und desto besser ist die Methode nachvollziehbar. |
| K6 | **Unabhängigkeit der zwei Kodierinstanzen** | Zwei Modelle verschiedener Entwickler mit verschiedenen Trainingsdaten machen weniger gleichartige Fehler als zwei Läufe desselben Modells. Ihr Kappa ist damit aussagekräftiger, analog zu zwei unabhängigen Personen. |
| K7 | **Reproduzierbarkeit** | Feste Version (Ollama-Digest), Temperatur 0, fester Seed, strukturierte Ausgabe (JSON-Schema). |

## Kandidaten

| Modell | Entwickler, Jahr | Lizenz | Größe | Bewertung |
|---|---|---|---|---|
| **Qwen3.5-9B** | Alibaba, 2026 | Apache 2.0 | 9 Mrd., dicht | erfüllt K1–K4, K7; neueste Generation, in der Literatur verbreitete Modellfamilie (Qwen3 Technical Report, Yang et al. 2025) → **Primärmodell** |
| OLMo-3-7B-Instruct | Ai2, 2025 | Apache 2.0 | 7 Mrd., dicht | erfüllt K1–K3, K5, K7; vollständig offen; zunächst Zweitmodell, **in der Kalibrierung ausgeschieden** (siehe unten) |
| Llama 3.1 8B | Meta, 2024 | Llama Community License | 8 Mrd. | ältere Generation; Lizenz mit Nutzungsbedingungen → nicht gewählt |
| Gemma 3 12B | Google, 2025 | Gemma Terms of Use | 12 Mrd. | keine freie Lizenz im Sinne von K2 → nicht gewählt |
| **Phi-4 14B** | Microsoft, 2024/25 | MIT | 14 Mrd. | erfüllt K1, K2, K4, K6, K7; größer (9 GB) und langsamer, passt aber noch (K3) → zunächst Reserve, **seit der Kalibrierung Kodierinstanz 2** (D24) |
| Qwen3.5-27B / 35B-A3B | Alibaba, 2026 | Apache 2.0 | 27 bzw. 35 Mrd. | zu groß für 24 GB mit Spielraum (K3) → nicht gewählt |
| **Ministral 3 14B Instruct** | Mistral AI, 2025 | Apache 2.0 | 14 Mrd., dicht (≈ 9 GB) | erfüllt K1–K4, K7; dritter Entwickler (K6) → **Prüfinstanz seit 18.11.2026** (D30) |
| Gemma 4 (E4B / 26B-MoE / 31B) | Google, 2026 | Apache 2.0 | 4 bzw. 26/31 Mrd. | E4B deutlich kleiner als die Kodiermodelle; 26B/31B passen kaum in 24 GB (K3) → nicht gewählt (Stand 18.11.2026) |

Verfügbarkeit geprüft am 16.11.2026: `qwen3.5:9b` und `olmo-3:7b-instruct` in der Ollama-Bibliothek.

## Entscheidung und Design

- **Kodierinstanz 1:** Qwen3.5-9B. **Kodierinstanz 2:** Phi-4 14B (ursprünglich OLMo-3-7B-Instruct, nach der Kalibrierung ersetzt, siehe unten).
- Beide bekommen **dieselbe Anweisung** (Kodierleitfaden mit Ankerbeispielen) und ordnen **unabhängig** ein.
- **Übereinstimmung** zwischen den beiden Modellen: Cohens Kappa (Kriterium ≥ 0,61, Landis & Koch 1977), genau wie im Exposé zwischen zwei Personen.
- **Tags:** In eine Gruppe kommen nur Tags, die beide gleich einordnen (wie im Exposé).
- **Fragen:** Als Referenz („Konsens“) gelten Fragen, die beide gleich einordnen; abweichende Fragen werden gezählt und nicht als Referenz genutzt.
- **Themen:** Qwen3.5 benennt; beide Modelle prüfen je Thema 10 andere Zufallstitel (bestanden, wenn beide ≥ 8/10).
- **Menschliche Prüfung (Validierung):** Die Autor:innen prüfen Zufallsstichproben (40 Tags, 100 Fragen) und sehen die Themenliste durch. Berichtet wird die Übereinstimmung Mensch–Modell. Das folgt der Empfehlung, automatische Annotation immer an menschlichen Urteilen zu validieren (Pangakis, Wolken & Fasching 2023; Törnberg 2024). **Seit 18.11.2026 (D30) entfällt die menschliche Prüfung** (Absprache mit der Betreuerin). Stattdessen ordnet eine dritte Modellfamilie (Ministral 3 14B) blind mit denselben Prompts ein; geprüft wird nach den vorab festgelegten Kriterien aus D29. Das zeigt, ob der Konsens unabhängig von den zwei Kodiermodellen gilt, ersetzt aber keine menschlichen Urteile (gemeinsame Verzerrungen von Sprachmodellen möglich) und wird im Paper als Grenze genannt.
- **Empirische Absicherung der Wahl:** Erreicht ein Modell in der menschlichen Prüfung deutlich schlechtere Werte als das andere, wird das im Paper berichtet. Liegt Kappa unter 0,61, wird der Leitfaden geschärft und ein zweiter Durchlauf dokumentiert (Exposé Abschnitt 6).

## Einstellungen (Reproduzierbarkeit)

| Einstellung | Wert |
|---|---|
| Laufzeitumgebung | Ollama (lokal), Version in `results/llm_modelle.json` |
| Modelle | `qwen3.5:9b`, `phi4:14b` (getestet und verworfen: `olmo-3:7b-instruct`), jeweils mit Digest |
| Temperatur | 0 |
| Seed | 20261116 |
| „Denkmodus“ | aus (kurze, direkte Antwort; schneller und stabiler) |
| Ausgabe | JSON nach festem Schema, z. B. `{"kategorie": "G" \| "U" \| "S", "begruendung": "…"}` |
| Kontext / Antwortlänge | 4096 Token Kontext; Antwort höchstens 512 Token (seit 16.11.2026: Qwen erzeugte bei einer Frage, F306, Endlostext; alle gültigen Antworten sind < 100 Token, daher ändert die Grenze keine gültige Einordnung). Zeitüberschreitung (300 s) gilt als ungültige Antwort |
| Eingabe Fragen | wie bei den Klassifikatoren (Titel, Text, Code-Auszug; ohne Tags, Jahr, Score) |

## Literatur (vor dem Zitieren im Original prüfen)

- Alizadeh, M., Kubli, M., Samei, Z., Dehghani, S., Zahedivafa, M., Bermeo, J. D., Korobeynikova, M., & Gilardi, F. (2023/2025). Open-source LLMs for text annotation: A practical guide for model setting and fine-tuning. arXiv:2307.02179. *(Veröffentlichungsstand prüfen)*
- Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *PNAS, 120*(30), e2305016120.
- Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics, 33*(1), 159–174.
- Palmer, A., Smith, N. A., & Spirling, A. (2024). Using proprietary language models in academic research requires explicit justification. *Nature Computational Science, 4*, 2–3.
- Pangakis, N., Wolken, S., & Fasching, N. (2023). Automated annotation with generative AI requires validation. arXiv:2306.00176.
- Spirling, A. (2023). Why open-source generative AI models are an ethical choice for science. *Nature, 616*, 413.
- Törnberg, P. (2024). Best practices for text annotation with large language models. arXiv:2402.05129.
- Yang, A. et al. (2025). Qwen3 technical report. arXiv:2505.09388. *(für Qwen3.5 zusätzlich die Modellkarte zitieren)*
- Ai2 / OLMo Team (2025). OLMo 3. Technischer Bericht bzw. Modellkarte `allenai/Olmo-3-7B-Instruct`. *(genaue Angabe prüfen)*
- Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., & Yang, D. (2024). Can large language models transform computational social science? *Computational Linguistics, 50*(1), 237–291.

Quellen der Recherche zur Verfügbarkeit (16.11.2026): Hugging Face Blog „Open Source LLM Models to Run Locally in 2026“; Wikipedia „Qwen“; Berichte zu Qwen3.5 (Artificial Analysis, VentureBeat) und OLMo 3 (The Decoder, The New Stack).

## Probelauf (16.11.2026)

Beide Modelle lokal geladen (Digests in `results/llm_modelle.json`; Qwen3.5-9B 7,6 GB, OLMo-3-7B-Instruct 4,5 GB in Q4_K_M). Test an 10 Kalibrierungsfragen mit einem **groben** Test-Prompt, je zwei Durchläufe:

| Modell | Sekunden je Frage | ungültige Antworten | zwei Läufe identisch | Verteilung |
|---|---|---|---|---|
| Qwen3.5-9B | 8,9 | 0 von 20 | ja | 10 × U |
| OLMo-3-7B-Instruct | 4,7 | 0 von 20 | ja | 7 × G, 2 × S, 1 × U |

**Folgerungen:** (1) Reproduzierbarkeit und strukturierte Ausgabe funktionieren. (2) Laufzeit für 630 Fragen × 2 Modelle ≈ 2,5 h, für 269 Tags × 2 deutlich weniger. (3) Mit einer knappen Anweisung zeigen die Modelle starke, gegenläufige Neigungen. Der endgültige Prompt wird deshalb aus dem vollständigen Leitfaden mit Definitionen, Entscheidungsweg und Ankerbeispielen gebaut, die Begründung vor der Kategorie abgefragt, und nur an den 30 Kalibrierungsfragen geschärft. Erreicht das Kappa zwischen den Modellen danach 0,61 nicht, wird das offen berichtet (Exposé Abschnitt 6); als Rückfall ist ein größeres lokales Modell der Qwen3.5-Familie möglich, sofern die Hardware es trägt.

## Kalibrierung und Modellwechsel (16.11.2026, D24)

Vorab festgelegt: Die Prompts werden höchstens zweimal an den Kalibrierungsdaten geschärft (10 Übungstags, 30 Kalibrierungsfragen, nicht Teil der Stichprobe). Ein Modell scheidet aus, wenn seine Begründungen seinen eigenen Einordnungen widersprechen (Kriterium unabhängig von der Übereinstimmung mit dem anderen Modell).

| Lauf | Daten | Prompt | Modelle | Kappa [95-%-KI] | Übereinstimmung |
|---|---|---|---|---|---|
| 1 | 10 Übungstags | Tags v1 | Qwen ↔ OLMo | 0,62 [0,19; 1,00] | 80 % |
| 2 | 30 Kalibrierungsfragen | Fragen v1 | Qwen ↔ OLMo | 0,28 [0,03; 0,52] | 60 % |
| 3 | 30 Kalibrierungsfragen | Fragen v2 | Qwen ↔ OLMo | 0,18 [0,03; 0,40] | 50 % |
| 4 | 30 Kalibrierungsfragen | Fragen v2 | Qwen ↔ Phi-4 | 0,50 [0,21; 0,78] | 80 % |
| 5 | 10 Übungstags | Tags v1 | Qwen ↔ Phi-4 | 0,62 [0,17; 1,00] | 80 % |
| – | *voller Lauf Runde 1: 269 Tags* | *Tags v1* | *Qwen ↔ Phi-4* | *0,37 [0,28; 0,45]* | *58 %* |
| 6 | 40 Nicht-Kandidaten-Tags (D25) | Tags v1 | Qwen ↔ Phi-4 | 0,40 [0,21; 0,61] | 60 % |
| 7 | 40 Nicht-Kandidaten-Tags | Tags v2 | Qwen ↔ Phi-4 | 0,52 [0,14; 0,79] | 85 % (Regeln verletzt) |
| 8 | 40 Nicht-Kandidaten-Tags | Tags v3 | Qwen ↔ Phi-4 | 0,31 [0,05; 0,56] | 70 % |
| – | *voller Lauf Runde 2: 269 Tags (endgültig)* | *Tags v3* | *Qwen ↔ Phi-4* | *0,22 [0,11; 0,33]* | *66 %* |

- **Fragen v2** (nach Lauf 2): allgemeine Regeln ergänzt (Prüfstein für U = fehlende Information über die Umgebung; dokumentiertes Verhalten von Frameworks = G; konkretes „Wie mache ich X?“ ≠ S; Begründung soll die Ursache nennen). Dieselben Regeln stehen im Leitfaden (Version 0.2).
- **OLMo schied aus** (nach Lauf 3): In Lauf 3 ordnete es 18 von 30 Fragen als U ein, oft mit Begründungen, die dem widersprechen (z. B. „not specific environment“ bei U). Ersatz nach den Kriterien oben: Phi-4 14B (anderer Entwickler, MIT-Lizenz). Genau **ein** Ersatzversuch (Lauf 4), danach keine weiteren Wechsel oder Prompt-Runden.
- **Zweite Runde Tags (D25):** Weil Runde 1 über alle 269 Tags nur κ = 0,37 erreichte, wurde – wie im Exposé vorgesehen – der Leitfaden geschärft (v0.2) und eine zweite Runde gerechnet. Die 10 Übungstags reichten als Kalibrierungsdaten nicht, deshalb wurden 30 weitere Tags außerhalb der 269 gezogen (100–149 Fragen im Oktober 2022, Seed + 5). Die Kalibrierungsmenge bildet Runde 1 gut ab (v1: κ 0,40 gegenüber 0,37). v2 erhöhte die Übereinstimmung, weil beide Modelle fast alles als G einordneten, auch ganze Programmiersprachen, entgegen Regel 2 und der Zwei-Drittel-Regel; v3 hält beide Regeln ein. v3 wurde vor dem vollen Lauf als endgültig festgelegt. Die Modelle ordnen die Tags nach dem geschätzten G-Anteil fast gleich (Spearman 0,79 bis 0,88), Phi-4 schätzt aber im Mittel etwa 10 Punkte weniger G – die Abweichungen sind vor allem Schwellenfälle.
- **Stand nach der Kalibrierung:** Kappa 0,50 bei 30 Fragen liegt unter 0,61, das Intervall ist aber sehr breit, und die ungleiche Verteilung (fast nur G) drückt Kappa bei hoher Übereinstimmung (80 %). Maßgeblich ist das Kappa über alle 600 Fragen; wird 0,61 dort nicht erreicht, wird das offen berichtet (Exposé Abschnitt 6).
- Berichte je Lauf: `results/llm/bericht_kal-*.md`.

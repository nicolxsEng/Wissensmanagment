# Prüfung des Modellkonsenses durch eine dritte Modellfamilie (D29, D30)

Erzeugt: 18.11.2026 22:29. Prüfinstanz: ministral-3:14b (unabhängig von den Kodiermodellen qwen3.5:9b, phi4:14b; gleiche Prompts und Einstellungen, ohne Kenntnis von deren Urteil). **Keine menschliche Prüfung** (D30). Kriterien vorab festgelegt (D29): Tags κ ≥ 0,61 und je Gruppe ≥ 80 % gleich eingeordnet; Fragen κ ≥ 0,61. Maßgeblich sind die Stichproben aus D29; die Werte über alle Einträge sind beschreibend.

## Tags

**Stichprobe D29** (40 Tags: U 14, G 26):

- Cohens Kappa Prüfinstanz–Konsens: **0,85** [0,67; 1,00] (fast vollkommen), Übereinstimmung 92 % (n = 40)
- Konsens G: Prüfinstanz gleich bei 23 von 26 (88 %, 95-%-KI 71 %–96 %)
- Konsens U: Prüfinstanz gleich bei 14 von 14 (100 %, 95-%-KI 78 %–100 %)

**Ergebnis Tags: bestätigt.** Die Gruppen gelten als durch eine dritte Modellfamilie bestätigt.

Beschreibend, alle 169 Gruppen-Tags:

- Cohens Kappa Prüfinstanz–Konsens: **0,76** [0,58; 0,90] (substanziell), Übereinstimmung 95 % (n = 169)
- Konsens G: Prüfinstanz gleich bei 147 von 155 (95 %, 95-%-KI 90 %–97 %)
- Konsens U: Prüfinstanz gleich bei 14 von 14 (100 %, 95-%-KI 78 %–100 %)
- ministral-3:14b ↔ qwen3.5:9b: κ = 0,46 [0,34; 0,56], 77 % (n = 269)
- ministral-3:14b ↔ phi4:14b: κ = 0,59 [0,50; 0,68], 79 % (n = 269)
- Von der Prüfinstanz bestätigte Tags (Gegenprobe „pruef“ in AP07): G 147, U 14

## Fragen

**Stichprobe D29** (100 Fragen):

- Cohens Kappa Prüfinstanz–Konsens: **0,82** [0,70; 0,93] (fast vollkommen), Übereinstimmung 91 % (n = 100)
- Konsens G: Prüfinstanz gleich bei 57 von 59 (97 %, 95-%-KI 88 %–99 %)
- Konsens U: Prüfinstanz gleich bei 31 von 38 (82 %, 95-%-KI 67 %–91 %)
- Konsens S: Prüfinstanz gleich bei 3 von 3 (100 %, 95-%-KI 44 %–100 %)

**Ergebnis Fragen: bestätigt.** Die Referenz für AP10 gilt als durch eine dritte Modellfamilie bestätigt.

Beschreibend, alle 456 Konsensfragen:

- Cohens Kappa Prüfinstanz–Konsens: **0,75** [0,69; 0,81] (substanziell), Übereinstimmung 88 % (n = 456)
- Konsens G: Prüfinstanz gleich bei 249 von 272 (92 %, 95-%-KI 88 %–94 %)
- Konsens U: Prüfinstanz gleich bei 135 von 168 (80 %, 95-%-KI 74 %–86 %)
- Konsens S: Prüfinstanz gleich bei 15 von 16 (94 %, 95-%-KI 72 %–99 %)
- ministral-3:14b ↔ qwen3.5:9b: κ = 0,52 [0,45; 0,59], 75 % (n = 599)
- ministral-3:14b ↔ phi4:14b: κ = 0,63 [0,57; 0,69], 81 % (n = 600)

## Einordnung

Die Prüfinstanz zeigt, ob der Konsens auch für ein drittes, unabhängig trainiertes Modell gilt, also nicht an zwei bestimmten Modellen hängt. Sie ersetzt keine menschliche Prüfung: Sprachmodelle können gemeinsame Verzerrungen haben (ähnliche Trainingsdaten). Das wird im Paper als Grenze genannt.

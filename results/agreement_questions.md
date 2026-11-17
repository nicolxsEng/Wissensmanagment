# Einordnung der Fragen – Übereinstimmung (AP09)

Erzeugt: 16.11.2026 14:14. Kodierinstanzen: qwen3.5:9b und phi4:14b (AP16).

- Fragen: 600, davon ohne gültige Antwort eines Modells: 1 (F306; nicht in Kappa und Konsens)
- Cohens Kappa: **0.55** [0.49; 0.61] (mittelmäßig), Übereinstimmung 76%
- Kriterium ≥ 0.61: NICHT erfüllt
- Konsens (Referenz für AP10): 456 Fragen (test: 121, train: 335); Verteilung G 272, S 16, U 168

Kreuztabelle (Zeilen qwen, Spalten phi):

| | G | U | S |
|---|---|---|---|
| G | 272 | 64 | 8 |
| U | 51 | 168 | 0 |
| S | 12 | 8 | 16 |

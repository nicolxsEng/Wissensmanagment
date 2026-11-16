# kal-tags – Übereinstimmung der Modelle

Erzeugt: 16.11.2026 10:33 · Prompt `tags` (602be1b95db9) · Modelle: qwen3.5:9b, olmo-3:7b-instruct

- Einträge: 10 (ungültig: 0)
- Cohens Kappa: **0.62** [0.19; 1.00] (substanziell), Übereinstimmung 80%

Verteilung:

| Kategorie | qwen | olmo |
|---|---|---|
| G | 7 | 6 |
| U | 0 | 2 |
| K | 3 | 2 |

Kreuztabelle (Zeilen qwen, Spalten olmo):

| | G | U | K |
|---|---|---|---|
| G | 6 | 1 | 0 |
| U | 0 | 0 | 0 |
| K | 0 | 1 | 2 |

Abweichungen:

- `mobile` mobile – qwen: K (Mobile covers both API usage (G) and environment/setup (U), fitting neither category clear) / olmo: U (Tag covers devices with varying environments and configurations.)
- `scipy` scipy – qwen: G (Most questions involve using specific functions/algorithms for data processing, fitting ru) / olmo: U (SciPy is a library, so answers depend on usage and environment.)

# kal-tags – Übereinstimmung der Modelle

Erzeugt: 16.11.2026 10:57 · Prompt `tags` (602be1b95db9) · Modelle: qwen3.5:9b, phi4:14b

- Einträge: 10 (ungültig: 0)
- Cohens Kappa: **0.62** [0.17; 1.00] (substanziell), Übereinstimmung 80%

Verteilung:

| Kategorie | qwen | phi |
|---|---|---|
| G | 7 | 5 |
| U | 0 | 1 |
| K | 3 | 4 |

Kreuztabelle (Zeilen qwen, Spalten phi):

| | G | U | K |
|---|---|---|---|
| G | 5 | 1 | 1 |
| U | 0 | 0 | 0 |
| K | 0 | 0 | 3 |

Abweichungen:

- `twitter-bootstrap` twitter-bootstrap – qwen: G (Framework API usage dominates; setup is secondary, leaning towards fundamentals.) / phi: U (Bootstrap involves setup, configuration, and environment specifics.)
- `url` url – qwen: G (URLs are data structures; parsing, validation, and manipulation follow from the string its) / phi: K (URLs involve both fundamental concepts and environment-specific issues.)

# Automatische Einordnung der Fragetexte (AP10)

Erzeugt: 18.11.2026 10:32. Referenz: Fragen, die beide Sprachmodelle gleich einordneten (AP09); Training 335, Test 121 (je Kandidat genau einmal, D06).

## Vergleich auf der Testmenge

| Kandidat | Macro-F1 [95-%-KI] | Genauigkeit | F1 G | F1 U | F1 S |
|---|---|---|---|---|---|
| setfit | 0,76 [0,56; 0,94] | 88 % | 0,91 | 0,87 | 0,50 |
| tfidf_logreg | 0,58 [0,53; 0,61] | 86 % | 0,89 | 0,84 | 0,00 |
| zero_shot | 0,51 [0,22; 0,59] | 44 % | 0,08 | 0,58 | 0,86 |

Gewinner: **setfit**; Kriterium Macro-F1 ≥ 0,70: erfüllt.
Nur G und U (ohne die 3 S-Testfragen): Macro-F1 0,89.

Konfusionsmatrix des Gewinners (Zeilen wahr, Spalten vorhergesagt):

| | G | U | S |
|---|---|---|---|
| G | 64 | 7 | 0 |
| U | 5 | 42 | 0 |
| S | 1 | 1 | 1 |

## Anteile je Jahr (roh und korrigiert)

Korrektur: adjusted classify and count mit der Konfusionsmatrix des Gewinners. Bei S beruht sie auf sehr wenigen Testfragen und ist entsprechend unsicher.

| Jahr | G roh | G korr. | U roh | U korr. | S roh | S korr. |
|---|---|---|---|---|---|---|
| 2015 | 67,9 % | 70,6 % | 30,4 % | 24,4 % | 1,7 % | 5,0 % |
| 2016 | 68,6 % | 71,2 % | 29,4 % | 22,8 % | 2,0 % | 6,0 % |
| 2017 | 68,3 % | 70,9 % | 29,8 % | 23,5 % | 1,8 % | 5,5 % |
| 2018 | 68,8 % | 71,9 % | 29,8 % | 23,9 % | 1,4 % | 4,2 % |
| 2019 | 69,9 % | 73,4 % | 28,8 % | 22,7 % | 1,3 % | 3,9 % |
| 2020 | 69,0 % | 72,1 % | 29,5 % | 23,4 % | 1,5 % | 4,5 % |
| 2021 | 69,2 % | 72,5 % | 29,4 % | 23,3 % | 1,4 % | 4,2 % |
| 2022 | 66,0 % | 68,5 % | 32,7 % | 27,6 % | 1,3 % | 3,9 % |
| 2023 | 56,5 % | 56,2 % | 41,8 % | 38,7 % | 1,7 % | 5,1 % |
| 2024 | 50,0 % | 48,7 % | 49,0 % | 48,5 % | 0,9 % | 2,8 % |
| 2025 | 44,1 % | 41,7 % | 55,4 % | 56,8 % | 0,5 % | 1,5 % |
| 2026 | 48,3 % | 46,0 % | 50,2 % | 49,3 % | 1,6 % | 4,7 % |

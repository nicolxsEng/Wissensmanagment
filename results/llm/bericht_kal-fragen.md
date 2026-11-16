# kal-fragen – Übereinstimmung der Modelle

Erzeugt: 16.11.2026 10:57 · Prompt `fragen` (55a5b12932c1) · Modelle: qwen3.5:9b, phi4:14b

- Einträge: 30 (ungültig: 0)
- Cohens Kappa: **0.50** [0.21; 0.78] (mittelmäßig), Übereinstimmung 80%

Verteilung:

| Kategorie | qwen | phi |
|---|---|---|
| G | 23 | 22 |
| U | 4 | 8 |
| S | 3 | 0 |

Kreuztabelle (Zeilen qwen, Spalten phi):

| | G | U | S |
|---|---|---|---|
| G | 21 | 2 | 0 |
| U | 1 | 3 | 0 |
| S | 0 | 3 | 0 |

Abweichungen:

- `F004` How to automaticaly switch between dashboards? – qwen: S (The question asks for a recommendation on which tool to use for a specific task without pr) / phi: U (The solution depends on Power BI's capabilities and Power Automate's integration, which va)
- `F039` Rspec doesn't clear factory objects after some specs – qwen: G (The problem is a logic/state issue in the test code where objects persist between specs du) / phi: U (The issue is related to the environment setup, specifically how objects are managed and cl)
- `F061` Errors on IBM mobilefirst Mobile browser simulator console – qwen: S (The question lacks specific error messages, code snippets or details about the environment) / phi: U (The solution depends on the specific environment setup and configuration of IBM MobileFirs)
- `F085` Including .aar dependencies using .pom file from local directory – qwen: G (The problem lies in the code configuration; the user needs to know how to correctly refere) / phi: U (The solution depends on the correct configuration of Gradle and the specific setup of the )
- `F185` Convert JSON to Powershell Object prints Strange Output – qwen: U (The problem lies in the asker's environment: the JSON structure shown is malformed (missin) / phi: G (The issue is likely due to how PowerShell handles JSON objects, which is a known behavior )
- `F360` How to serve response in django then down the server – qwen: S (The question asks for an opinion or recommendation on how to implement a feature, without ) / phi: U (The solution depends on the server environment and permissions, which are not specified.)

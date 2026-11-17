# kal-tags – Übereinstimmung der Modelle

Erzeugt: 16.11.2026 14:30 · Prompt `tags` (ec5923beb375) · Modelle: qwen3.5:9b, phi4:14b

- Einträge: 40 (ungültig: 0)
- Cohens Kappa: **0.52** [0.14; 0.79] (mittelmäßig), Übereinstimmung 85%

Verteilung:

| Kategorie | qwen | phi |
|---|---|---|
| G | 33 | 32 |
| U | 6 | 8 |
| K | 1 | 0 |

Kreuztabelle (Zeilen qwen, Spalten phi):

| | G | U | K |
|---|---|---|---|
| G | 30 | 3 | 0 |
| U | 2 | 4 | 0 |
| K | 0 | 1 | 0 |

Abweichungen:

- `data-science` data-science – qwen: K (G~0% U~0%: Tag is deprecated; no typical questions exist to estimate shares.) / phi: U (G~40% U~60%: Data science involves both code/data analysis (G) and environment setup (U) l)
- `azure-data-factory` azure-data-factory – qwen: G (G~70% U~30%: Most questions involve debugging pipeline logic, JSON syntax, or activity con) / phi: U (G~40% U~60%: Questions often involve environment-specific configurations, permissions, and)
- `mariadb` mariadb – qwen: U (G~40% U~60%: Concrete DB tags mix queries (G) with install/config issues (U), where setup ) / phi: G (G~60% U~40%: Questions often involve SQL queries or MariaDB-specific features, but setup a)
- `cmd` cmd – qwen: U (G~30% U~70%: Typical questions involve OS-specific commands, permissions, or environment v) / phi: G (G~60% U~40%: Questions often involve scripting or command syntax (G), but sometimes depend)
- `jenkins-pipeline` jenkins-pipeline – qwen: G (G~85% U~15%: Most questions involve syntax, logic, and API usage of the Pipeline DSL, whic) / phi: U (G~40% U~60%: Questions often involve specific Jenkins configurations, plugins, or environm)
- `x86` x86 – qwen: G (G~60% U~40%: Questions often involve assembly syntax, instruction encoding, or CPU behavio) / phi: U (G~30% U~70%: Questions often involve specific configurations, OS, or hardware details not )

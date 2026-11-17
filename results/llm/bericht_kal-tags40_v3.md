# kal-tags – Übereinstimmung der Modelle

Erzeugt: 16.11.2026 14:37 · Prompt `tags` (73bddd6f8f26) · Modelle: qwen3.5:9b, phi4:14b

- Einträge: 40 (ungültig: 0)
- Cohens Kappa: **0.31** [0.05; 0.56] (ausreichend), Übereinstimmung 70%

Verteilung:

| Kategorie | qwen | phi |
|---|---|---|
| G | 34 | 25 |
| U | 2 | 5 |
| K | 4 | 10 |

Kreuztabelle (Zeilen qwen, Spalten phi):

| | G | U | K |
|---|---|---|---|
| G | 24 | 4 | 6 |
| U | 0 | 1 | 1 |
| K | 1 | 0 | 3 |

Abweichungen:

- `mobile` mobile – qwen: U (G~20% U~80%: Typical questions involve OS-specific configuration, permissions, or environm) / phi: K (G~50% U~50%: Questions often involve code (G) or environment-specific issues like OS, perm)
- `memory` memory – qwen: G (G~70% U~30%: Most questions involve code logic (allocation, leaks, pointers) visible in th) / phi: K (G~60% U~40%: Memory management questions often involve code or data structures, but can al)
- `outlook` outlook – qwen: G (G~70% U~30%: Most questions involve email rules, VBA macros, or API usage visible in the t) / phi: U (G~30% U~70%: Outlook issues often involve configuration, permissions, or environment-speci)
- `selenium-chromedriver` selenium-chromedriver – qwen: G (G~70% U~30%: Most questions involve code usage, debugging, or API logic rather than instal) / phi: K (G~60% U~40%: Questions often involve code usage and API interaction (G), but also setup an)
- `azure-data-factory` azure-data-factory – qwen: G (G~70% U~30%: Most questions involve debugging pipeline logic or JSON syntax visible in the) / phi: U (G~40% U~60%: Questions often involve setup, configuration, and environment-specific issues)
- `http-redirect` http-redirect – qwen: G (G~80% U~20%: Most questions involve implementing or debugging redirect logic (301/302) usi) / phi: K (G~60% U~40%: Questions often involve understanding HTTP status codes and headers, which ar)
- `build` build – qwen: G (G~80% U~20%: Most questions involve fixing build scripts, errors, or configuration logic v) / phi: U (G~30% U~70%: Build processes often involve environment-specific configurations, tools, and)
- `mariadb` mariadb – qwen: G (G~70% U~30%: Most questions involve SQL queries or API usage, which are visible in the que) / phi: K (G~60% U~40%: Questions often involve SQL queries (G), but also installation and configurat)
- `cmd` cmd – qwen: G (G~65% U~35%: Most questions involve writing scripts or using specific commands visible in ) / phi: K (G~60% U~40%: Questions often involve scripting or command syntax (G), but also depend on O)
- `jenkins-pipeline` jenkins-pipeline – qwen: G (G~70% U~30%: Most questions involve writing or debugging pipeline syntax, stages, and agen) / phi: K (G~60% U~40%: Questions often involve writing pipeline scripts (G), but also depend on Jenk)
- `x86` x86 – qwen: G (G~80% U~20%: Questions focus on assembly syntax, instruction encoding, or architecture log) / phi: U (G~30% U~70%: Questions often involve environment-specific configurations, OS, and hardware)
- `sass` sass – qwen: K (language rule: sass is a general-purpose programming/scripting language (preprocessor); pe) / phi: G (G~80% U~20%: Most questions involve syntax, logic, or usage of Sass features, which are vi)

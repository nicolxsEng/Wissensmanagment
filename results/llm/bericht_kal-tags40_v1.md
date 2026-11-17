# kal-tags – Übereinstimmung der Modelle

Erzeugt: 16.11.2026 14:23 · Prompt `tags` (602be1b95db9) · Modelle: qwen3.5:9b, phi4:14b

- Einträge: 40 (ungültig: 0)
- Cohens Kappa: **0.40** [0.21; 0.61] (mittelmäßig), Übereinstimmung 60%

Verteilung:

| Kategorie | qwen | phi |
|---|---|---|
| G | 28 | 13 |
| U | 5 | 14 |
| K | 7 | 13 |

Kreuztabelle (Zeilen qwen, Spalten phi):

| | G | U | K |
|---|---|---|---|
| G | 13 | 8 | 7 |
| U | 0 | 5 | 0 |
| K | 0 | 1 | 6 |

Abweichungen:

- `twitter-bootstrap` twitter-bootstrap – qwen: G (Framework API usage dominates; setup is secondary, leaning towards fundamentals.) / phi: U (Bootstrap involves setup, configuration, and environment specifics.)
- `url` url – qwen: G (URLs are data structures; parsing, validation, and manipulation follow from the string its) / phi: K (URLs involve both fundamental concepts and environment-specific issues.)
- `memory` memory – qwen: G (Memory management and allocation are core programming concepts solvable from code alone.) / phi: U (Memory management questions often involve environment specifics.)
- `visualization` visualization – qwen: G (Fokus auf Diagramm-Typen und Datenverarbeitung, nicht auf spezifische Tools oder Umgebunge) / phi: K (Visualization covers both data processing and environment setup.)
- `asp.net-core-mvc` asp.net-core-mvc – qwen: G (Most questions involve API usage, routing, and model binding rather than environment setup) / phi: K (ASP.NET Core MVC involves both API usage and environment setup.)
- `sequelize.js` sequelize.js – qwen: G (Most questions focus on API usage, model definitions, and query logic rather than installa) / phi: K (Sequelize involves both API usage and environment setup.)
- `google-chrome-extension` google-chrome-extension – qwen: G (Most questions focus on API usage and logic rather than environment setup or configuration) / phi: U (Involves setup, permissions, and environment-specific issues.)
- `build` build – qwen: K (Build tags cover both tool usage (U) and algorithmic logic like dependency resolution or i) / phi: U (Build processes depend on tooling, configurations, and environments.)
- `bootstrap-4` bootstrap-4 – qwen: G (Most questions involve API usage, grid systems, or components, making solutions derivable ) / phi: U (Bootstrap 4 involves setup, configuration, and environment-specific issues.)
- `groovy` groovy – qwen: G (Groovy is a programming language; most questions involve syntax, DSLs, or logic derivable ) / phi: K (Groovy covers both fundamentals and environment aspects.)
- `cmd` cmd – qwen: G (Most questions involve specific command syntax or script logic derivable from the text, no) / phi: U (Questions often involve environment-specific commands and configurations.)
- `jenkins-pipeline` jenkins-pipeline – qwen: G (Focuses on Pipeline syntax, DSL constructs, and logic rather than installation or environm) / phi: U (Typically involves setup, configuration, and environment specifics.)
- `x86` x86 – qwen: G (Questions about CPU architecture, assembly, or low-level details are fundamental to the ha) / phi: U (x86 covers architecture, setup, and environment specifics.)
- `ffmpeg` ffmpeg – qwen: G (Most questions involve API usage, filters, and data processing logic derivable from the qu) / phi: K (FFmpeg involves both API usage and environment-specific configurations.)
- `sass` sass – qwen: G (Sass questions typically involve syntax, nesting, mixins, or variables, which are language) / phi: K (Sass involves both API usage and environment setup.)
- `post` post – qwen: G (HTTP POST usage typically involves API logic and request handling rather than environment-) / phi: U (HTTP POST requests often involve environment-specific configurations.)

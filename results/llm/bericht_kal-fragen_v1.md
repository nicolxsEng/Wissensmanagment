# kal-fragen – Übereinstimmung der Modelle

Erzeugt: 16.11.2026 10:36 · Prompt `fragen` (88074c02dfd6) · Modelle: qwen3.5:9b, olmo-3:7b-instruct

- Einträge: 30 (ungültig: 0)
- Cohens Kappa: **0.28** [0.03; 0.52] (ausreichend), Übereinstimmung 60%

Verteilung:

| Kategorie | qwen | olmo |
|---|---|---|
| G | 22 | 15 |
| U | 5 | 14 |
| S | 3 | 1 |

Kreuztabelle (Zeilen qwen, Spalten olmo):

| | G | U | S |
|---|---|---|---|
| G | 13 | 8 | 1 |
| U | 0 | 5 | 0 |
| S | 2 | 1 | 0 |

Abweichungen:

- `F039` Rspec doesn't clear factory objects after some specs – qwen: G (Problem ist Zustandskontamination durch Factory-Objekte zwischen Tests; Lösung erfordert R) / olmo: S (RSpec retains domain objects across specs due to lack of explicit clear/cleanup in #run me)
- `F061` Errors on IBM mobilefirst Mobile browser simulator console – qwen: S (No code or specific error details provided; question lacks concrete problem definition.) / olmo: G (Errors in IBM MobileFirst browser simulator console likely due to unhandled exceptions or )
- `F078` How to make animation on LazyGrid for Item perform only first time appearence? – qwen: G (The question asks about a specific recomposition behavior in Jetpack Compose's LazyGrid an) / olmo: U (Recomposition causes state reset; use state management to track first appearance.)
- `F090` How to automate visiting links then submitting a form? – qwen: S (The question asks for a solution strategy (how to combine actions) rather than debugging s) / olmo: G (Combining link navigation, form filling, and submission in a Chrome extension requires orc)
- `F109` javascript download ended trigger – qwen: G (The problem is about handling asynchronous file downloads in JavaScript, which requires us) / olmo: U (Need to pause loop until download completes before proceeding to next photo.)
- `F131` Unable to parallelize a function with multiple arguments in R – qwen: G (The error occurs because mclapply passes only the first element of each list to the functi) / olmo: U (mclapply expects a function of one argument; pass a vector of arguments with `mclapply` or)
- `F178` Handler postDelayed executes few times – qwen: G (The problem is a logic error in the code (infinite recursion via postDelayed inside run), ) / olmo: U (Handler scheduling causes repeated execution; use removeCallbacks to prevent requeueing.)
- `F251` How do I concatenate values returned from an async pipe in Angular – qwen: G (Die Lösung erfordert nur das Verständnis von Observables und dem async Pipe in Angular, wa) / olmo: U (Need to merge new async data with existing state using state management (e.g., NgRx store )
- `F325` Converting XML to document in java creates null document – qwen: G (The issue is a known Java DOM API behavior where parse() returns null for certain XML stru) / olmo: U (Document is null because InputSource is not properly initialized or XML is not valid UTF-8)
- `F360` How to serve response in django then down the server – qwen: S (This is an opinion/design question asking for proposals on how to implement a feature, not) / olmo: U (Request handler to send shutdown signal and call exit(), depends on OS environment.)
- `F617` XPages error -- dojo/parser::parse() error TypeError: s.match is not a function – qwen: G (The error indicates a JavaScript string method failure in Dojo, likely caused by malformed) / olmo: U (Error from DojoX toolkit due to incompatible or missing DOMParser or string handling in br)
- `F628` EF Core include many to many relation in the generic repository by params – qwen: G (The error is caused by a missing navigation property in the model, which can be fixed by a) / olmo: U (EF Core can't find MovieCinema navigation; add it to model or use explicit relation path.)

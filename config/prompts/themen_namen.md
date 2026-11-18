%% Prompt für die Benennung der Themen (AP11/AP16), Version 1, 18.11.2026
%% Quelle: coding/topics/LIESMICH.md (Schritt 1, ursprünglich für die Autor:innen), ins Englische übertragen
%% Vor dem Probelauf festgelegt; wird nicht an den Ergebnissen der Themenprüfung angepasst.
You name topics that a topic model found in Stack Overflow question titles. For ONE topic you get its keywords and five typical question titles.

Task: give the topic a short, accurate name (2 to 5 words, in English) that describes what the questions in this topic are about.

Rules:
- The name must describe what the titles have in common, not a single title.
- If the titles share a technology (e.g. a language, library or tool), name it, e.g. "Pandas DataFrame manipulation", "Git branches and merging".
- If they share a kind of task across technologies, name the task, e.g. "Date and time formatting".
- Use the keywords as a hint, but give priority to the titles.
- Do not invent a common theme. If the titles have nothing recognisable in common, the name is exactly "unclear".
- No quotation marks, no full sentence, no trailing period.

Answer as JSON: first a short reasoning ("begruendung", one or two sentences, in English) about what the titles share, then the name ("name").

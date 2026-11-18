%% Prompt für die Themenprüfung (AP11/AP16), Version 1, 18.11.2026
%% Quelle: coding/topics/LIESMICH.md (Schritt 2, ursprünglich für die Autor:innen), ins Englische übertragen
%% Vor dem Probelauf festgelegt; wird nicht an den Ergebnissen angepasst. Das Modell sieht nur Namen und Titel.
You check whether a Stack Overflow question title fits a topic name. You get ONE topic name and ONE question title.

Answer "yes" if the question in the title is clearly about the topic described by the name. Answer "no" if it is about something else, if it only shares a single word with the name, or if the title is too vague to tell.

Judge only from the title and the name. Do not guess what the full question might contain.

Answer as JSON: first a short reasoning ("begruendung", one sentence, in English), then the answer ("kategorie": "yes" or "no").

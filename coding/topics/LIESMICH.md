# Themenprüfung – Probelauf (AP11)

Zwei Verfahren (BERTopic und NMF) haben je 21 Themen aus 1.008 Fragetiteln gebildet. Die 42 Themen sind **gemischt und neutral kodiert** (T01–T42). Ihr wisst also nicht, welches Verfahren welches Thema erzeugt hat.

## Schritt 1: Themen benennen (gemeinsam)

Datei: `themen_benennen_probelauf.csv`

- Je Thema stehen die Schlüsselwörter und 5 typische Titel.
- Tragt in die Spalte `name` einen kurzen, treffenden Namen ein (z. B. 2–5 Wörter). Der Name soll beschreiben, worum es in diesem Thema geht. Ist das nicht möglich, weil die Titel nichts gemeinsam haben, schreibt `unklar`.
- Nichts anderes ändern.

Danach Claude Code bitten: `scripts/11_topics.py pilot-checks` ausführen.

## Schritt 2: Themen prüfen (getrennt)

Dateien: `themen_check_A.csv` (Nicolas), `themen_check_B.csv` (Gentian)

- Je Thema 10 **andere**, zufällige Titel. Spalte `passt`: `j`, wenn der Titel zum Themennamen passt, sonst `n`.
- Keine Absprache, bis beide fertig sind.
- Ein Thema besteht, wenn **beide** mindestens 8 von 10 Titeln als passend markieren.

Danach: `scripts/11_topics.py pilot-eval`. Gewählt wird das Verfahren mit mehr bestandenen Themen. Erst dann `data/processed/topics_pilot_mapping.csv` öffnen (dort steht, welches Thema zu welchem Verfahren gehört).

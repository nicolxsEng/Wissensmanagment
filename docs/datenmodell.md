# Datenmodell (Ausgabe von AP01)

Alle Zeitstempel in UTC. Definitionen der abgeleiteten Felder: `plan.md` Abschnitt 5.

## `data/interim/questions.parquet` – eine Zeile je Frage

| Spalte | Typ | Quelle / Berechnung |
|---|---|---|
| `question_id` | int64 | Rohdaten |
| `year` | int16 | Jahr von `creation_date` |
| `created` | datetime[UTC] | `creation_date` |
| `title` | str | Rohdaten (HTML-Entitäten aufgelöst) |
| `tags` | list[str] | Rohdaten (heutige Tags) |
| `n_tags` | int8 | Länge von `tags` |
| `score` | int32 | heutiger Wert |
| `view_count` | int64 | heutiger Wert |
| `answer_count_now` | int32 | heutiger Wert, nur zur Kontrolle |
| `accepted_answer_id` | int64, null | Rohdaten |
| `is_closed` | bool | `closed_date` vorhanden |
| `closed_reason` | str, null | Rohdaten |
| `is_new_type` | bool | Tag in `config.NEW_TYPE_TAGS` |
| `is_classic` | bool | `not is_new_type` |
| `n_ai_tags` | int8 | Zahl der Tags in `config.AI_TAGS` |
| `body_len_nocode` | int32 | Zeichen im Text ohne `<pre>`-Blöcke, Leerraum zusammengefasst |
| `has_code` | bool | mindestens ein `<pre>`-Block |
| `n_code_blocks` | int16 | Zahl der `<pre>`-Blöcke |
| `code_chars` | int32 | Zeichen in Codeblöcken |
| `n_answers_7d` | int16 | Antworten mit 0 ≤ Abstand ≤ 168 h |
| `first_answer_hours` | float64, null | Abstand zur ersten Antwort (alle Antworten, ≥ 0) |
| `answered_7d` | bool | `n_answers_7d > 0` |
| `answered_24h` | bool | erste Antwort ≤ 24 h |
| `accepted_7d` | bool | akzeptierte Antwort existiert und liegt im Fenster |
| `owner_user_id` | int64, null | nur für Erweiterung E1, nie ausgeben |

## `data/interim/answers.parquet` – eine Zeile je Antwort

| Spalte | Typ | Berechnung |
|---|---|---|
| `answer_id` | int64 | |
| `question_id` | int64 | |
| `year` | int16 | Jahr der Frage |
| `created` | datetime[UTC] | |
| `delay_hours` | float64 | Antwort − Frage in Stunden (kann negativ sein) |
| `in_window` | bool | 0 ≤ `delay_hours` ≤ 168 |
| `score` | int32 | heutiger Wert |
| `is_accepted` | bool | |
| `owner_user_id` | int64, null | nur für E1 |

## `data/interim/texts.parquet` – Texte für Klassifikation und Themen

| Spalte | Typ | Berechnung |
|---|---|---|
| `question_id` | int64 | |
| `year` | int16 | |
| `title` | str | |
| `body_text` | str | Text ohne HTML; Codeblöcke durch `[CODE]` ersetzt |
| `body_code` | str | Inhalt der Codeblöcke, mit Leerzeile getrennt |

## Datenprotokoll (`results/logs/build_dataset.md`)

Je Jahr: Fragen, Antworten, Abgleich mit `_progress.json`, Antworten ohne Frage, Antworten mit negativem Abstand, Fragen ohne Text, Laufzeit.

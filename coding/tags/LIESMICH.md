# Tag-Kodierung (AP04/AP05)

1. Leitfaden lesen: [docs/kodierleitfaden_tags.md](../../docs/kodierleitfaden_tags.md).
2. **Übung gemeinsam:** `uebung_10.csv` beide getrennt ausfüllen, dann vergleichen und besprechen. Diese Tags gehören nicht zu den 269 und zählen nicht.
3. **Kodierung getrennt:** Nicolas füllt `tags_kodierer_A.csv`, Gentian `tags_kodierer_B.csv`. Keine Absprache, bis beide fertig sind.
   - Spalte `kategorie`: `G` (Grundlagen), `U` (Umgebung) oder `K` (keine eindeutige)
   - Spalte `unsicher`: `x`, wenn unsicher
   - Spalte `notiz`: optional, kurz
   - Nichts sonst ändern (keine Zeilen sortieren, löschen oder hinzufügen).
4. **Nicht öffnen, bevor beide fertig sind:** `data/processed/tags_candidates*.csv`, `tag_breaks*.csv`, `top_tags_yearly.csv`, `ai_tags_yearly.csv`, `results/logs/tag_audit.md`. Sie enthalten Fragezahlen je Tag.
5. Danach `make agreement-tags` (AP05) ausführen lassen.

Die Dateien sind CSV mit Semikolon und lassen sich direkt in Excel oder Numbers öffnen. Beim Speichern das Format „CSV (Semikolon getrennt), UTF-8“ beibehalten.

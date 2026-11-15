# Sichtbares Wissen auf Stack Overflow vor und nach ChatGPT

Forschungsprojekt im Kurs „Studien zu Wissen in Organisationen“ (TH Nürnberg, WS 2026/27), Nicolas Engelmann und Gentian Jetullahu.

- **Plan und alle Definitionen:** [plan.md](plan.md)
- **Regeln für Claude Code:** [CLAUDE.md](CLAUDE.md)
- **Entscheidungsprotokoll:** [docs/entscheidungen.md](docs/entscheidungen.md)
- **Kodierleitfäden:** [Tags](docs/kodierleitfaden_tags.md), [Fragen](docs/kodierleitfaden_fragen.md)

## Einrichtung

Voraussetzung: [`uv`](https://docs.astral.sh/uv/) und die Rohdaten in `../Datentest` (anderer Ort: Umgebungsvariable `SOV_RAW_DIR`).

```bash
uv sync
```

```bash
uv run pytest -q
```

Für Themenanalyse und SetFit (erst ab AP10/AP11, lädt PyTorch):

```bash
uv sync --group topics --group ml
```

Achtung: Ein späteres `uv sync` ohne `--group` entfernt diese Pakete wieder. Für die Kodier-App reicht `uv sync`.

## Arbeiten mit Claude Code

Ein Arbeitspaket aus `plan.md` umsetzen lassen:

```text
/ap AP01
```

Reihenfolge und Zeitplan: `plan.md` Abschnitt 10. Was schon erledigt ist: Abschnitt 15.

## Pipeline

```bash
make help
```

`make all` erzeugt alles, was ohne menschliche Kodierung läuft. Abbildungen landen in `figures/` (PDF + PNG), Tabellen in `tables/`, alle Zahlen fürs Paper in `results/kennzahlen.json`.

## Daten und Lizenz

Stack-Overflow-Inhalte stehen unter CC BY-SA 4.0; zitierte Beiträge werden mit Link angegeben. Rohdaten, abgeleitete Daten und API-Keys werden nicht versioniert.

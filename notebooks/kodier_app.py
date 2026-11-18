"""Prüf-App für die Einordnung der Fragetexte (blind, D29). Start:

    uv run marimo run notebooks/kodier_app.py

Zeigt je Stichprobenfrage Titel und Text (ohne Jahr, Tags, Score, ohne Urteil der Modelle).
Die Autor:innen ordnen selbst ein: G, U oder S, optional „unsicher“ und eine Notiz; jedes Urteil
wird sofort in coding/pruefung/fragen_100.csv gespeichert. Unterbrechen ist jederzeit möglich.
Verglichen mit den Modellen wird erst danach (`scripts/17_pruefung.py auswerten`).
Leitfaden: docs/kodierleitfaden_fragen.md
"""

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Prüfung Fragen")


@app.cell
def _():
    import html
    import os
    from pathlib import Path

    import marimo as mo
    import polars as pl

    from sov.coding import read_sheet, save_entry

    _root = Path(mo.notebook_dir()).parent / "coding"
    QDIR = Path(os.environ.get("SOV_CODING_QDIR", _root / "questions"))
    PATH = Path(os.environ.get("SOV_PRUEF_FILE", _root / "pruefung" / "fragen_100.csv"))
    NAMES = {"G": "Grundlagen", "U": "Umgebung", "S": "Sonstige"}
    return NAMES, PATH, QDIR, html, mo, pl, read_sheet, save_entry


@app.cell
def _(QDIR, pl):
    view = {r["code"]: r for r in pl.read_parquet(QDIR / "ansicht.parquet").to_dicts()}
    return (view,)


@app.cell
def _(mo):
    get_pos, set_pos = mo.state(None)
    get_rev, set_rev = mo.state(0)
    return get_pos, get_rev, set_pos, set_rev


@app.cell
def _(PATH, get_pos, get_rev, mo, read_sheet):
    get_rev()  # nach jedem Speichern neu laden
    mo.stop(
        not PATH.exists(),
        mo.callout(
            mo.md(f"`{PATH.name}` gibt es noch nicht – zuerst `scripts/17_pruefung.py boegen`."),
            kind="warn",
        ),
    )
    _df = read_sheet(PATH)
    mo.stop(
        "stimmt" in _df.columns,
        mo.callout(
            mo.md("Alter Bogen (nicht blind) – `scripts/17_pruefung.py boegen`."), kind="warn"
        ),  # fmt: skip
    )
    rows = _df.sort("nr").to_dicts()
    open_idx = [i for i, r in enumerate(rows) if not r["kategorie"]]
    pos = get_pos()
    if pos is None:
        pos = open_idx[0] if open_idx else len(rows) - 1
    row = rows[pos]
    n_done = len(rows) - len(open_idx)
    return n_done, open_idx, pos, row, rows


@app.cell
def _(mo, row):
    unsicher = mo.ui.checkbox(value=bool(row["unsicher"]), label="unsicher")
    notiz = mo.ui.text(value=row["notiz"] or "", placeholder="Notiz (optional)", full_width=True)
    return notiz, unsicher


@app.cell
def _(NAMES, PATH, mo, notiz, open_idx, pos, row, rows, save_entry, set_pos, set_rev, unsicher):
    def _save(cat):
        save_entry(PATH, row["code"], cat, unsicher=unsicher.value, notiz=notiz.value)
        set_rev(lambda v: v + 1)
        nxt = next((i for i in open_idx if i > pos), None)
        set_pos(nxt if nxt is not None else min(pos + 1, len(rows) - 1))

    buttons = [
        mo.ui.button(label=f"{c} · {n}", on_click=lambda _, c=c: _save(c)) for c, n in NAMES.items()
    ]
    b_prev = mo.ui.button(label="← zurück", on_click=lambda _: set_pos(max(pos - 1, 0)))
    b_next = mo.ui.button(label="weiter →", on_click=lambda _: set_pos(min(pos + 1, len(rows) - 1)))
    return b_next, b_prev, buttons


@app.cell
def _(NAMES, b_next, b_prev, buttons, html, mo, n_done, notiz, pos, row, rows, unsicher, view):
    _q = view[row["code"]]
    _status = f"Frage {pos + 1} von {len(rows)} · {n_done} eingeordnet · Code {row['code']}"
    if row["kategorie"]:
        _status += f" · bisher: <b>{row['kategorie']} · {NAMES[row['kategorie']]}</b>"
    if n_done == len(rows):
        _status += " · <b>Prüfung vollständig</b>"
    _body = mo.Html(
        '<div style="max-height:55vh;overflow:auto;padding:0.75rem 1rem;'
        'border:1px solid #e1e0d9;border-radius:6px">' + _q["body_html"] + "</div>"
    )
    mo.vstack(
        [
            mo.Html(f'<div style="color:#52514e;font-size:0.9rem">{_status}</div>'),
            mo.Html(f'<h3 style="margin:0.4rem 0">{html.escape(_q["title"])}</h3>'),
            _body,
            mo.hstack([*buttons, unsicher], justify="start", gap=1),
            notiz,
            mo.hstack([b_prev, b_next], justify="start", gap=1),
        ],
        gap=0.75,
    )
    return


@app.cell
def _(mo):
    mo.accordion(
        {
            "Leitfaden (Kurzfassung)": mo.md(
                """
- **G · Grundlagen:** Die Lösung lässt sich aus der Frage selbst ableiten (Code, Daten,
  Fehlermeldung, allgemeines Programmierwissen). Auch Frameworks, wenn der Fehler im Code liegt.
- **U · Umgebung:** Die Lösung braucht Informationen über die Umgebung der fragenden Person
  (installierte Versionen, Betriebssystem, Konfiguration, Build/Deploy, Server, Cloud,
  externe Dienste).
- **S · Sonstige:** kein konkretes Problem (Meinung, Empfehlung, rein konzeptionell, unklar).

Zuerst einordnen, Zweifel als „unsicher“ markieren. Vollständig:
`docs/kodierleitfaden_fragen.md`
"""
            )
        }
    )
    return


if __name__ == "__main__":
    app.run()

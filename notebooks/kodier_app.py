"""Prüf-App für die Einordnung der Fragetexte (AP09, D23). Start:

    uv run marimo run notebooks/kodier_app.py

Zeigt je Stichprobenfrage Titel und Text (ohne Jahr, Tags, Score) und die Einordnung der beiden
Modelle mit Begründung. Die Autor:innen entscheiden „stimmt“ oder „stimmt nicht“; jedes Urteil
wird sofort in coding/pruefung/fragen_100.csv gespeichert. Unterbrechen ist jederzeit möglich.
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

    from sov.coding import read_sheet, save_check

    _root = Path(mo.notebook_dir()).parent / "coding"
    QDIR = Path(os.environ.get("SOV_CODING_QDIR", _root / "questions"))
    PATH = Path(os.environ.get("SOV_PRUEF_FILE", _root / "pruefung" / "fragen_100.csv"))
    NAMES = {"G": "Grundlagen", "U": "Umgebung", "S": "Sonstige"}
    return NAMES, PATH, QDIR, html, mo, pl, read_sheet, save_check


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
            mo.md(f"`{PATH.name}` gibt es noch nicht – zuerst AP09 ausführen."), kind="warn"
        ),
    )
    rows = read_sheet(PATH).sort("nr").to_dicts()
    open_idx = [i for i, r in enumerate(rows) if not r["stimmt"]]
    pos = get_pos()
    if pos is None:
        pos = open_idx[0] if open_idx else len(rows) - 1
    row = rows[pos]
    n_done = len(rows) - len(open_idx)
    return n_done, open_idx, pos, row, rows


@app.cell
def _(mo, row):
    notiz = mo.ui.text(
        value=row["notiz"] or "", placeholder="Notiz (optional, z. B. richtige Kategorie)",
        full_width=True,
    )  # fmt: skip
    return (notiz,)


@app.cell
def _(PATH, mo, notiz, open_idx, pos, row, rows, save_check, set_pos, set_rev):
    def _save(ok):
        save_check(PATH, "code", row["code"], stimmt=ok, notiz=notiz.value)
        set_rev(lambda v: v + 1)
        nxt = next((i for i in open_idx if i > pos), None)
        set_pos(nxt if nxt is not None else min(pos + 1, len(rows) - 1))

    b_ok = mo.ui.button(label="✓ stimmt", kind="success", on_click=lambda _: _save(True))
    b_no = mo.ui.button(label="✗ stimmt nicht", kind="danger", on_click=lambda _: _save(False))
    b_prev = mo.ui.button(label="← zurück", on_click=lambda _: set_pos(max(pos - 1, 0)))
    b_next = mo.ui.button(label="weiter →", on_click=lambda _: set_pos(min(pos + 1, len(rows) - 1)))
    return b_next, b_no, b_ok, b_prev


@app.cell
def _(NAMES, b_next, b_no, b_ok, b_prev, html, mo, n_done, notiz, pos, row, rows, view):
    _q = view[row["code"]]
    _status = f"Frage {pos + 1} von {len(rows)} · {n_done} geprüft · Code {row['code']}"
    if row["stimmt"]:
        _status += f" · bisher: <b>{'stimmt' if row['stimmt'] == 'j' else 'stimmt nicht'}</b>"
    if n_done == len(rows):
        _status += " · <b>Prüfung vollständig</b>"
    _label = (
        f'<div style="padding:0.6rem 0.9rem;border-radius:6px;background:rgba(42,120,214,0.08)">'
        f"Einordnung der Modelle: <b>{row['kategorie']} · {NAMES[row['kategorie']]}</b><br>"
        f'<span style="color:#52514e">Begründung: {html.escape(row["begruendung"] or "")}</span>'
        f"</div>"
    )
    _body = mo.Html(
        '<div style="max-height:50vh;overflow:auto;padding:0.75rem 1rem;'
        'border:1px solid #e1e0d9;border-radius:6px">' + _q["body_html"] + "</div>"
    )
    mo.vstack(
        [
            mo.Html(f'<div style="color:#52514e;font-size:0.9rem">{_status}</div>'),
            mo.Html(f'<h3 style="margin:0.4rem 0">{html.escape(_q["title"])}</h3>'),
            _body,
            mo.Html(_label),
            mo.hstack([b_ok, b_no], justify="start", gap=1),
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

„Stimmt“ heißt: Ihr würdet die Frage genauso einordnen. Vollständig:
`docs/kodierleitfaden_fragen.md`
"""
            )
        }
    )
    return


if __name__ == "__main__":
    app.run()

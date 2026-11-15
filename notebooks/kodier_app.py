"""Kodier-App für die Fragetexte (AP06). Start:

    uv run marimo run notebooks/kodier_app.py

Zeigt je Frage nur Titel und Text – ohne Jahr, Tags oder Score (blinde Kodierung). Jede
Einordnung wird sofort in den Bogen (coding/questions/*.csv) geschrieben; Unterbrechen und
Weitermachen ist jederzeit möglich. Leitfaden: docs/kodierleitfaden_fragen.md
"""

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Kodierung Fragen")


@app.cell
def _():
    import html
    import os
    from pathlib import Path

    import marimo as mo
    import polars as pl

    from sov.coding import read_sheet, save_entry

    _default = Path(mo.notebook_dir()).parent / "coding" / "questions"
    QDIR = Path(os.environ.get("SOV_CODING_QDIR", _default))
    return QDIR, html, mo, pl, read_sheet, save_entry


@app.cell
def _(mo):
    coder = mo.ui.dropdown(
        {"Nicolas (A)": "A", "Gentian (B)": "B"}, value="Nicolas (A)", label="Kodierer:in"
    )
    menge = mo.ui.dropdown(
        {"Kalibrierung (30 Fragen)": "kalibrierung", "Stichprobe": "kodierer"},
        value="Kalibrierung (30 Fragen)",
        label="Bogen",
    )
    mo.hstack([coder, menge], justify="start", gap=2)
    return coder, menge


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
def _(QDIR, coder, menge, set_pos):
    path = QDIR / f"{menge.value}_{coder.value}.csv"
    set_pos(None)  # beim Wechsel des Bogens zur ersten offenen Frage springen
    return (path,)


@app.cell
def _(get_pos, get_rev, mo, path, read_sheet):
    get_rev()  # nach jedem Speichern neu laden
    mo.stop(
        not path.exists(),
        mo.callout(mo.md(f"Bogen `{path.name}` gibt es nicht."), kind="danger"),
    )
    rows = read_sheet(path).sort("nr").to_dicts()
    open_idx = [i for i, r in enumerate(rows) if not r["kategorie"]]
    pos = get_pos()
    if pos is None:
        pos = open_idx[0] if open_idx else len(rows) - 1
    row = rows[pos]
    n_done = len(rows) - len(open_idx)
    return n_done, open_idx, pos, row, rows


@app.cell
def _(mo, row):
    unsicher = mo.ui.checkbox(value=row["unsicher"] == "x", label="unsicher")
    notiz = mo.ui.text(value=row["notiz"] or "", placeholder="Notiz (optional)", full_width=True)
    return notiz, unsicher


@app.cell
def _(mo, notiz, open_idx, path, pos, row, rows, save_entry, set_pos, set_rev, unsicher):
    def _save(kat):
        save_entry(path, row["code"], kat, unsicher=unsicher.value, notiz=notiz.value)
        set_rev(lambda v: v + 1)
        nxt = next((i for i in open_idx if i > pos), None)
        set_pos(nxt if nxt is not None else min(pos + 1, len(rows) - 1))

    b_g = mo.ui.button(label="G · Grundlagen", on_click=lambda _: _save("G"))
    b_u = mo.ui.button(label="U · Umgebung", on_click=lambda _: _save("U"))
    b_s = mo.ui.button(label="S · Sonstige", on_click=lambda _: _save("S"))
    b_prev = mo.ui.button(label="← zurück", on_click=lambda _: set_pos(max(pos - 1, 0)))
    b_next = mo.ui.button(label="weiter →", on_click=lambda _: set_pos(min(pos + 1, len(rows) - 1)))
    b_open = mo.ui.button(
        label="zur nächsten offenen", on_click=lambda _: set_pos(open_idx[0] if open_idx else pos)
    )
    return b_g, b_next, b_open, b_prev, b_s, b_u


@app.cell
def _(
    b_g, b_next, b_open, b_prev, b_s, b_u, html, mo, n_done, notiz, pos, row, rows, unsicher, view
):
    _q = view[row["code"]]
    _status = f"Frage {pos + 1} von {len(rows)} · {n_done} kodiert · Code {row['code']}"
    if row["kategorie"]:
        _status += f" · bisher: <b>{row['kategorie']}</b>"
    if n_done == len(rows):
        _status += " · <b>Bogen vollständig</b>"
    _body = mo.Html(
        '<div style="max-height:55vh;overflow:auto;padding:0.75rem 1rem;'
        'border:1px solid #e1e0d9;border-radius:6px">' + _q["body_html"] + "</div>"
    )
    mo.vstack(
        [
            mo.Html(f'<div style="color:#52514e;font-size:0.9rem">{_status}</div>'),
            mo.Html(f'<h3 style="margin:0.4rem 0">{html.escape(_q["title"])}</h3>'),
            _body,
            mo.hstack([b_g, b_u, b_s, unsicher], justify="start", gap=1),
            notiz,
            mo.hstack([b_prev, b_next, b_open], justify="start", gap=1),
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
1. **Gibt es ein konkretes Programmier- oder Technikproblem?** Nein → **S**
2. **Lässt sich die Lösung allein aus dem Text ableiten** (Code, Daten, Fehlermeldung),
   ohne Zugriff auf Rechner, Konfiguration oder genaue Versionen? Ja → **G**
3. **Hängt die Lösung an der Umgebung** (Betriebssystem, Versionen, Konfiguration,
   Build/Deploy, IDE, Container, Server, Netzwerk, Rechte, Cloud, externe Dienste)? → **U**
4. Unklar: Kategorie nach der Ursache wählen und **unsicher** ankreuzen.

Vollständig: `docs/kodierleitfaden_fragen.md`
"""
            )
        }
    )
    return


if __name__ == "__main__":
    app.run()

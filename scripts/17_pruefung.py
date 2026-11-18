"""Menschliche Prüfung der Modell-Kodierung (D29): blinde Bögen erzeugen und auswerten.

uv run python scripts/17_pruefung.py boegen      # leere Bögen (nie über Einträge schreiben)
uv run python scripts/17_pruefung.py auswerten   # nachdem die Autor:innen fertig sind

Bögen (coding/pruefung/, füllen nur die Autor:innen aus):
  tags_40_A.csv, tags_40_B.csv  dieselben 40 Tags in verschiedener Reihenfolge, je Person ein
                                Bogen; alle U-Tags + zufällige G-Tags (D29), ohne Modell-Urteil
  fragen_100.csv                100 zufällige Konsensfragen (dieselben wie bisher), Einordnung
                                in der Kodier-App, ohne Modell-Urteil
Auswertung: results/pruefung.md; data/processed/groups_mensch.json (Tags, die alle Prüfenden
wie die Modelle einordnen; Gegenprobe in AP07)
"""

import json
import sys
from datetime import datetime

import polars as pl

from sov import config
from sov.agreement import kappa_ci, landis_koch
from sov.coding import (
    build_question_sheet,
    build_tag_sheet,
    read_sheet,
    sheet_has_entries,
    write_sheet,
)
from sov.pruefung import compare, questions_confirmed, stratified_tags, tags_confirmed

D = config.CODING_DIR / "pruefung"
P = config.PROCESSED_DIR
PERSONS = ("A", "B")
OLD_CHECK_COLS = ("stimmt", "notiz")  # Form vor D29 (Zustimmung j/n, nicht blind)


def tag_path(p: str):
    return D / f"tags_{config.PRUEF_TAGS_N}_{p}.csv"


def question_path():
    return D / f"fragen_{config.PRUEF_FRAGEN_N}.csv"


def question_codes() -> list[str]:
    """Dieselbe Ziehung wie bisher (Seed + 60 auf den nach Code sortierten Konsensfragen)."""
    lab = pl.read_csv(config.CODING_DIR / "questions" / "labels_600.csv").sort("code")
    s = lab.sample(min(config.PRUEF_FRAGEN_N, lab.height), seed=config.SEED + 60, shuffle=True)
    return s["code"].to_list()


def drop_old(path) -> None:
    """Entfernt einen Bogen in der alten Form, solange niemand etwas eingetragen hat."""
    if not path.exists() or "stimmt" not in read_sheet(path).columns:
        return
    if sheet_has_entries(path, OLD_CHECK_COLS):
        raise FileExistsError(f"{path} enthält bereits Prüfurteile und bleibt unverändert.")
    path.unlink()
    print(f"alter Bogen ohne Einträge entfernt: {path.name}")


def boegen() -> None:
    groups = json.loads((P / "groups.json").read_text())
    tags = stratified_tags(groups, config.PRUEF_TAGS_N, config.SEED + 70)
    wiki = pl.read_csv(P / "tag_wiki.csv").filter(pl.col("tag").is_in(tags))
    assert wiki.height == len(tags), "Wiki-Auszug fehlt für einzelne Tags"
    old_q = question_path()
    if old_q.exists() and "stimmt" in read_sheet(old_q).columns:
        assert set(read_sheet(old_q)["code"]) == set(question_codes()), "andere Stichprobe"
    drop_old(D / f"tags_{config.PRUEF_TAGS_N}.csv")
    drop_old(old_q)
    for i, p in enumerate(PERSONS):
        write_sheet(build_tag_sheet(wiki, config.SEED + 71 + i), tag_path(p))
    write_sheet(build_question_sheet(question_codes(), config.SEED + 61), old_q)
    n_u = len(set(tags) & set(groups["U"]))
    print(f"Tags: {len(tags)} (U {n_u}, G {len(tags) - n_u}) → {', '.join(PERSONS)}")
    print(f"Fragen: {config.PRUEF_FRAGEN_N} → {old_q.name}")


# ----------------------------------------------------------------------------- Auswertung
def de(x: float, d: int = 2) -> str:
    return f"{x:.{d}f}".replace(".", ",")


def pct(x: float) -> str:
    return f"{100 * x:.0f} %"


def filled(path) -> pl.DataFrame | None:
    """Bogen, falls vollständig ausgefüllt; sonst None (Stand wird ausgegeben)."""
    if not path.exists():
        return None
    df = read_sheet(path)
    n = df.filter(pl.col("kategorie").fill_null("").str.strip_chars() != "").height
    if n < df.height:
        print(f"{path.name}: {n} von {df.height} eingeordnet – noch nicht vollständig")
        return None
    return df.with_columns(pl.col("kategorie").str.strip_chars().str.to_uppercase())


def result_lines(res: dict, labels: list[str]) -> list[str]:
    out = [
        f"- Cohens Kappa Mensch–Modelle: **{de(res['kappa'])}** [{de(res['ci_low'])}; "
        f"{de(res['ci_high'])}] ({landis_koch(res['kappa'])}), Übereinstimmung "
        f"{pct(res['uebereinstimmung'])} (n = {res['n']})",
    ]
    for lab in labels:
        r = res["je_klasse"].get(lab)
        if r:
            out.append(
                f"- Modelle {lab}: Mensch gleich bei {r['k']} von {r['n']} ({pct(r['anteil'])}, "
                f"95-%-KI {pct(r['ci_low'])}–{pct(r['ci_high'])})"
            )
    return out


def auswerten() -> None:
    groups = json.loads((P / "groups.json").read_text())
    ref_tag = {t: g for g in ("G", "U") for t in groups[g]}
    L = [
        "# Menschliche Prüfung der Modell-Kodierung (D29)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Die Autor:innen ordneten blind ein (ohne "
        "Urteil der Modelle); Vergleich mit dem Konsens beider Modelle. Kriterien vorab "
        f"festgelegt (D29): Tags κ ≥ {de(config.KAPPA_MIN)} und je Gruppe ≥ "
        f"{pct(config.PRUEF_GRUPPE_MIN)} gleich eingeordnet; Fragen κ ≥ {de(config.KAPPA_MIN)}.",
        "",
        "## Tags",
        "",
    ]
    sheets = {p: filled(tag_path(p)) for p in PERSONS}
    done = {p: s for p, s in sheets.items() if s is not None}
    oks = []
    for p, s in done.items():
        tags = s["tag"].to_list()
        res = compare(s["kategorie"].to_list(), [ref_tag[t] for t in tags],
                      list(config.TAG_CATEGORIES))  # fmt: skip
        ok = tags_confirmed(res)
        oks.append(ok)
        n_uns = s.filter(pl.col("unsicher").fill_null("") != "").height
        L += [f"**Person {p}** ({n_uns} als unsicher markiert):", "",
              *result_lines(res, ["G", "U"]),
              f"- Kriterium: {'erfüllt' if ok else 'NICHT erfüllt'}", ""]  # fmt: skip
    if len(done) == 2:
        a, b = (done[p].sort("tag") for p in PERSONS)
        hh = kappa_ci(a["kategorie"].to_list(), b["kategorie"].to_list(),
                      list(config.TAG_CATEGORIES))  # fmt: skip
        L += [
            f"Übereinstimmung der Autor:innen untereinander: κ = {de(hh['kappa'])} "
            f"[{de(hh['ci_low'])}; {de(hh['ci_high'])}], {pct(hh['uebereinstimmung'])} "
            "(zeigt, wie eindeutig die Aufgabe für Menschen ist).",
            "",
        ]
    if done:
        conf = {
            g: sorted(
                t
                for t in groups[g]
                if t in set(next(iter(done.values()))["tag"])
                and all(
                    s.filter(pl.col("tag") == t)["kategorie"].item() == g for s in done.values()
                )
            )  # fmt: skip
            for g in ("G", "U")
        }
        (P / "groups_mensch.json").write_text(json.dumps(
            {**conf, "_meta": {"erzeugt": datetime.now().isoformat(timespec="seconds"),
                               "personen": sorted(done), "regel": "D29"}},
            indent=2, ensure_ascii=False))  # fmt: skip
        verdict = all(oks)
        L += [
            f"**Ergebnis Tags: {'bestätigt' if verdict else 'NICHT bestätigt'}** "
            f"(Kriterium bei {sum(oks)} von {len(oks)} Prüfenden erfüllt; nötig: bei allen). "
            + (
                "Die Gruppen gelten als bestätigt."
                if verdict
                else "Nach D29 bleibt die Hauptauswertung (Runde 2) unverändert; das Tag-Ergebnis "
                "zu TF2 wird nur gemeinsam mit der Textanalyse und den Gegenproben gedeutet und "
                "die Grenze im Paper offengelegt."
            ),
            f"Von Menschen bestätigte Tags (Gegenprobe „mensch“ in AP07): G {len(conf['G'])}, "
            f"U {len(conf['U'])}.",
            "",
        ]
    else:
        L += ["*Noch kein Tag-Bogen vollständig.*", ""]

    L += ["## Fragen", ""]
    q = filled(question_path())
    if q is not None:
        ref = dict(pl.read_csv(config.CODING_DIR / "questions" / "labels_600.csv")
                   .select("code", "label").iter_rows())  # fmt: skip
        res = compare(q["kategorie"].to_list(), [ref[c] for c in q["code"]],
                      list(config.QUESTION_CATEGORIES))  # fmt: skip
        ok = questions_confirmed(res)
        n_uns = q.filter(pl.col("unsicher").fill_null("") != "").height
        L += [
            f"{n_uns} Fragen als unsicher markiert.",
            "",
            *result_lines(res, list(config.QUESTION_CATEGORIES)),
            "",
            f"**Ergebnis Fragen: {'bestätigt' if ok else 'NICHT bestätigt'}.** "
            + (
                "Die Referenz für AP10 gilt als bestätigt."
                if ok
                else "Nach D29 misst der Macro-F1 aus AP10 nur die Übereinstimmung mit dem "
                "Modellkonsens; die Textanalyse wird im Paper nur als Hinweis gedeutet."
            ),
            "",
        ]
    else:
        L += ["*Fragebogen noch nicht vollständig.*", ""]
    (config.RESULTS_DIR / "pruefung.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "boegen":
        boegen()
    elif cmd == "auswerten":
        auswerten()
    else:
        sys.exit(__doc__)

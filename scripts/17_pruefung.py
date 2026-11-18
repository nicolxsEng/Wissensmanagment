"""Prüfung des Modellkonsenses durch eine dritte Modellfamilie (D29, D30).

uv run python scripts/16_llm_coding.py pruef-tags     # Prüfinstanz ordnet alle 269 Tags ein
uv run python scripts/16_llm_coding.py pruef-fragen   # ... und die 600 Stichprobenfragen
uv run python scripts/17_pruefung.py                  # Auswertung

Kriterien (vorab festgelegt, D29; Prüfinstanz statt Autor:innen seit D30) gelten auf den
Stichproben aus D29: 40 Tags (alle 14 U + 26 zufällige G, Seed + 70) und 100 zufällige
Konsensfragen (Seed + 60). Zusätzlich beschreibend: alle Konsens-Tags bzw. -Fragen und Kappa der
Prüfinstanz mit jedem der beiden Kodiermodelle.
Ausgaben: results/pruefung.md; data/processed/groups_pruef.json (Tags, die die Prüfinstanz wie
der Konsens einordnet; Gegenprobe „pruef“ in AP07)
"""

import json
from datetime import datetime

import polars as pl

from sov import config
from sov.agreement import kappa_ci, landis_koch
from sov.coding import read_sheet
from sov.pruefung import compare, questions_confirmed, stratified_tags, tags_confirmed

P = config.PROCESSED_DIR
K = config.LLM_CHECKER
CODERS = list(config.LLM_CODERS)


def question_codes() -> list[str]:
    """Ziehung aus D29 (Seed + 60 auf den nach Code sortierten Konsensfragen)."""
    lab = pl.read_csv(config.CODING_DIR / "questions" / "labels_600.csv").sort("code")
    s = lab.sample(min(config.PRUEF_FRAGEN_N, lab.height), seed=config.SEED + 60, shuffle=True)
    return s["code"].to_list()


def labels(path, idcol: str) -> dict[str, str | None]:
    df = read_sheet(path)
    return dict(zip(df[idcol], df["kategorie"], strict=True))


def de(x: float, d: int = 2) -> str:
    return f"{x:.{d}f}".replace(".", ",")


def pct(x: float) -> str:
    return f"{100 * x:.0f} %"


def result_lines(res: dict, cats: list[str]) -> list[str]:
    out = [
        f"- Cohens Kappa Prüfinstanz–Konsens: **{de(res['kappa'])}** [{de(res['ci_low'])}; "
        f"{de(res['ci_high'])}] ({landis_koch(res['kappa'])}), Übereinstimmung "
        f"{pct(res['uebereinstimmung'])} (n = {res['n']})",
    ]
    for c in cats:
        r = res["je_klasse"].get(c)
        if r:
            out.append(
                f"- Konsens {c}: Prüfinstanz gleich bei {r['k']} von {r['n']} "
                f"({pct(r['anteil'])}, 95-%-KI {pct(r['ci_low'])}–{pct(r['ci_high'])})"
            )
    return out


def pairwise(folder: str, prefix: str, idcol: str, cats: list[str]) -> list[str]:
    """Kappa der Prüfinstanz mit jedem Kodiermodell über alle Einträge (beschreibend)."""
    chk = labels(config.CODING_DIR / folder / f"llm_{prefix}_{K}.csv", idcol)
    out = []
    for m in CODERS:
        other = labels(config.CODING_DIR / folder / f"llm_{prefix}_{m}.csv", idcol)
        ids = [i for i in chk if chk[i] and other.get(i)]
        ka = kappa_ci([chk[i] for i in ids], [other[i] for i in ids], cats)
        out.append(
            f"- {config.LLM_MODELS[K]} ↔ {config.LLM_MODELS[m]}: κ = {de(ka['kappa'])} "
            f"[{de(ka['ci_low'])}; {de(ka['ci_high'])}], {pct(ka['uebereinstimmung'])} "
            f"(n = {ka['n']})"
        )
    return out


def main() -> None:
    model = config.LLM_MODELS[K]
    L = [
        "# Prüfung des Modellkonsenses durch eine dritte Modellfamilie (D29, D30)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. Prüfinstanz: {model} (unabhängig von den "
        f"Kodiermodellen {', '.join(config.LLM_MODELS[m] for m in CODERS)}; gleiche Prompts und "
        "Einstellungen, ohne Kenntnis von deren Urteil). **Keine menschliche Prüfung** (D30). "
        f"Kriterien vorab festgelegt (D29): Tags κ ≥ {de(config.KAPPA_MIN)} und je Gruppe ≥ "
        f"{pct(config.PRUEF_GRUPPE_MIN)} gleich eingeordnet; Fragen κ ≥ {de(config.KAPPA_MIN)}. "
        "Maßgeblich sind die Stichproben aus D29; die Werte über alle Einträge sind beschreibend.",
        "",
        "## Tags",
        "",
    ]
    groups = json.loads((P / "groups.json").read_text())
    ref_tag = {t: g for g in ("G", "U") for t in groups[g]}
    tcats = list(config.TAG_CATEGORIES)
    chk_t = labels(config.CODING_DIR / "tags" / f"llm_tags_{K}.csv", "tag")
    sample = stratified_tags(groups, config.PRUEF_TAGS_N, config.SEED + 70)
    bad = [t for t in sample if not chk_t.get(t)]
    assert not bad, f"keine gültige Einordnung der Prüfinstanz für {bad}"
    res = compare([chk_t[t] for t in sample], [ref_tag[t] for t in sample], tcats)
    ok_t = tags_confirmed(res)
    allg = [t for t in ref_tag if chk_t.get(t)]
    res_all = compare([chk_t[t] for t in allg], [ref_tag[t] for t in allg], tcats)
    conf = {g: sorted(t for t in groups[g] if chk_t.get(t) == g) for g in ("G", "U")}
    (P / "groups_pruef.json").write_text(
        json.dumps(
            {**conf, "_meta": {"erzeugt": datetime.now().isoformat(timespec="seconds"),
                               "pruefinstanz": model, "regel": "D30"}},
            indent=2, ensure_ascii=False,
        )
    )  # fmt: skip
    L += [
        f"**Stichprobe D29** ({len(sample)} Tags: U {sum(ref_tag[t] == 'U' for t in sample)}, "
        f"G {sum(ref_tag[t] == 'G' for t in sample)}):",
        "",
        *result_lines(res, ["G", "U"]),
        "",
        f"**Ergebnis Tags: {'bestätigt' if ok_t else 'NICHT bestätigt'}.** "
        + (
            "Die Gruppen gelten als durch eine dritte Modellfamilie bestätigt."
            if ok_t
            else "Nach D29/D30 bleibt die Hauptauswertung (Runde 2) unverändert; das Tag-Ergebnis "
            "zu TF2 wird nur gemeinsam mit der Textanalyse und den Gegenproben gedeutet und die "
            "Grenze im Paper offengelegt."
        ),
        "",
        f"Beschreibend, alle {len(allg)} Gruppen-Tags:",
        "",
        *result_lines(res_all, ["G", "U"]),
        *pairwise("tags", "tags", "tag", tcats),
        f"- Von der Prüfinstanz bestätigte Tags (Gegenprobe „pruef“ in AP07): "
        f"G {len(conf['G'])}, U {len(conf['U'])}",
        "",
        "## Fragen",
        "",
    ]
    qcats = list(config.QUESTION_CATEGORIES)
    ref_q = dict(
        pl.read_csv(config.CODING_DIR / "questions" / "labels_600.csv")
        .select("code", "label")
        .iter_rows()
    )
    chk_q = labels(config.CODING_DIR / "questions" / f"llm_fragen_{K}.csv", "code")
    codes = [c for c in question_codes() if chk_q.get(c)]
    n_bad = config.PRUEF_FRAGEN_N - len(codes)
    res_q = compare([chk_q[c] for c in codes], [ref_q[c] for c in codes], qcats)
    ok_q = questions_confirmed(res_q)
    allq = [c for c in ref_q if chk_q.get(c)]
    res_qall = compare([chk_q[c] for c in allq], [ref_q[c] for c in allq], qcats)
    L += [
        f"**Stichprobe D29** ({config.PRUEF_FRAGEN_N} Fragen"
        + (f", davon {n_bad} ohne gültige Antwort der Prüfinstanz" if n_bad else "")
        + "):",
        "",
        *result_lines(res_q, qcats),
        "",
        f"**Ergebnis Fragen: {'bestätigt' if ok_q else 'NICHT bestätigt'}.** "
        + (
            "Die Referenz für AP10 gilt als durch eine dritte Modellfamilie bestätigt."
            if ok_q
            else "Nach D29/D30 misst der Macro-F1 aus AP10 nur die Übereinstimmung mit dem "
            "Modellkonsens; die Textanalyse wird im Paper nur als Hinweis gedeutet."
        ),
        "",
        f"Beschreibend, alle {len(allq)} Konsensfragen:",
        "",
        *result_lines(res_qall, qcats),
        *pairwise("questions", "fragen", "code", qcats),
        "",
        "## Einordnung",
        "",
        "Die Prüfinstanz zeigt, ob der Konsens auch für ein drittes, unabhängig trainiertes Modell "
        "gilt, also nicht an zwei bestimmten Modellen hängt. Sie ersetzt keine menschliche "
        "Prüfung: Sprachmodelle können gemeinsame Verzerrungen haben (ähnliche Trainingsdaten). "
        "Das wird im Paper als Grenze genannt.",
    ]
    (config.RESULTS_DIR / "pruefung.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()

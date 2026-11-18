"""AP12: Datenprüfung (20 Fragen erneut über die API) und Literaturabgleich.

uv run python scripts/12_checks.py

Stichprobe (D31): je Oktober 2008–2026 eine zufällige Frage und eine Frage eines neuen Fragetyps
(Seed + 120); für AP14 zusätzlich 10 zufällige Antworten aus dem 7-Tage-Fenster (Seed + 121), das
Konto wird nur als Hash verglichen. Die API-Antworten werden in data/interim/api_cache/
zwischengespeichert (ohne Nutzer-IDs), ein erneuter Lauf fragt nicht noch einmal ab.
Ausgaben: coding/checks/datenpruefung_20.csv, coding/checks/antworten_10.csv, results/checks.md
"""

import os
from datetime import UTC, datetime
from statistics import median

import polars as pl

from sov import config
from sov.checks import (
    FIELDS,
    api_features,
    compare_answer,
    compare_question,
    draw_check_answers,
    draw_check_questions,
    fetch,
    fetch_answers,
    owner_hash,
)
from sov.io import load_answers, load_questions, raw_year_dir

P = config.PROCESSED_DIR
OUT_CSV = config.CODING_DIR / "checks" / "datenpruefung_20.csv"
KEY_FIELDS = {
    "Erstellzeit",
    "Tags",
    "Antworten im Fenster",
    "Zeit bis zur ersten Antwort (h)",
    "akzeptiert im Fenster",
}

# Literatur (aus den Originalquellen gelesen am 18.11.2026, Abschnitt in Klammern)
RIO = (
    "del Rio-Chanona, Laurentsyeva & Wachs (2024), *PNAS Nexus* 3(9), pgae400, "
    "doi:10.1093/pnasnexus/pgae400"
)
BURTCH = "Burtch, Lee & Chen (2024), *Scientific Reports* 14, 10413, doi:10.1038/s41598-024-61221-0"
BURTCH_STRONG = ["python", "css", "flutter", "reactjs", "django", "sql", "arrays", "pandas"]
BURTCH_WEAK = ["spring", "spring-boot", "amazon-web-services", "firebase", "docker",
               "sql-server", "azure"]  # fmt: skip


def de(x: float, d: int = 1) -> str:
    s = f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


def download_date(year: int) -> str:
    ts = os.stat(raw_year_dir(year) / "questions.jsonl.gz").st_mtime
    return datetime.fromtimestamp(ts, UTC).strftime("%d.%m.%Y")


def stored_records(ids: list[int]) -> dict[int, dict]:
    q = load_questions(canonical_tags=False).filter(pl.col("question_id").is_in(ids))
    a = load_answers(["question_id", "answer_id", "in_window"]).filter(
        pl.col("question_id").is_in(ids) & pl.col("in_window")
    )
    win = {}
    for qid, aid in a.select("question_id", "answer_id").iter_rows():
        win.setdefault(qid, set()).add(aid)
    out = {}
    for r in q.iter_rows(named=True):
        out[r["question_id"]] = {
            "year": r["year"],
            "is_new_type": r["is_new_type"],
            "created": r["created"],
            "tags": sorted(r["tags"]),
            "n_answers_7d": r["n_answers_7d"],
            "first_answer_hours": r["first_answer_hours"],
            "accepted_7d": r["accepted_7d"],
            "answer_count_now": r["answer_count_now"],
            "answer_ids_7d": win.get(r["question_id"], set()),
        }
    return out


def literature(lines: list[str]) -> None:
    m = pl.read_csv(P / "metrics_yearly.csv").filter(
        (pl.col("population") == "alle") & (pl.col("metric") == "n_questions")
    )
    n = dict(zip(m["year"], m["value"], strict=True))
    its = pl.read_csv(P / "its_fit.csv").filter(
        (pl.col("population") == "klassisch") & (pl.col("metric") == "n_questions")
    )
    dev = dict(zip(its["year"], its["deviation_pct"], strict=True))
    shift = pl.read_csv(P / "tag_shift.csv")
    keep = dict(zip(shift["tag"], shift["behalten"], strict=True))
    grp = dict(zip(shift["tag"], shift["gruppe_runde2"].fill_null(""), strict=True))
    strong = [keep[t] for t in BURTCH_STRONG if t in keep]
    weak = [keep[t] for t in BURTCH_WEAK if t in keep]

    def tag_list(tags):
        return ", ".join(f"{t} {de(keep[t], 2)}" + (f" ({grp[t]})" if grp[t] else "")
                         for t in tags if t in keep)  # fmt: skip

    lines += [
        "## Literaturabgleich",
        "",
        "Nur Richtung und Größenordnung sind vergleichbar: Die Studien schätzen den Unterschied "
        "zu Vergleichsplattformen bzw. zum Vorjahr in den ersten Monaten nach dem 30.11.2022; "
        "dieses Projekt vergleicht Oktober-Monate und die Fortschreibung des Trends 2015–2022, "
        "ohne Vergleichsplattform.",
        "",
        "| | Daten und Vergleich | Zeitraum | Ergebnis |",
        "|---|---|---|---|",
        f"| dieses Projekt | Fragen je Oktober; Vorher-nachher und Abweichung vom Trend "
        f"2015–2022 (keine Vergleichsplattform) | Okt. 2022 → Okt. 2023 / 2024 | Fragen "
        f"{de(n[2022], 0)} → {de(n[2023], 0)} (**{de(100 * (n[2023] / n[2022] - 1))} %**), "
        f"2024: {de(n[2024], 0)} ({de(100 * (n[2024] / n[2022] - 1))} %); Abweichung vom Trend "
        f"{de(dev[2023])} % (2023) bzw. {de(dev[2024])} % (2024) |",
        f"| {RIO} | Beiträge (Fragen und Antworten) je Woche; Differenz-in-Differenzen gegen "
        "russisches Stack Overflow, Segmentfault, Mathematics, MathOverflow | Jan. 2022 – Mai "
        "2023 | Mittel der ersten 6 Monate: Beiträge −15 %, Fragen −10 % (Tab. 1); bis Ende "
        "April 2023 ≈ −25 %, von den Autor:innen als Untergrenze bezeichnet; roh: ≈ 60.000 → "
        "40.000 Beiträge je Woche in 6 Monaten, 60.000 → 30.000 von Mai 2022 bis Mai 2024 |",
        f"| {BURTCH} | Besuche je Tag (synthetische Kontrolle); Fragen je Thema, 50 häufigste "
        "Tags (Differenz-in-Differenzen gegen dasselbe Zeitfenster ein Jahr früher); "
        "Reddit-Entwicklerforen als Gegenprobe | Okt. 2022 – Mitte März 2023 | Besuche ≈ −12 % "
        "(≈ 1 Mio. je Tag); Fragen deutlich gesunken (im Haupttext keine Prozentzahl); Reddit "
        "ohne Veränderung |",
        "",
        "**Richtung:** gleich (Rückgang der Fragen nach November 2022). **Größenordnung:** Der "
        "Rückgang hier ist größer als die geschätzten −10 % bis −25 %. Das passt zu den "
        "unterschiedlichen Vergleichen: Die Studien ziehen die Entwicklung auf "
        "Vergleichsplattformen ab und betrachten nur die ersten 4–6 Monate; der rohe Rückgang "
        "bei del Rio-Chanona et al. (≈ −33 % in 6 Monaten, −50 % in zwei Jahren) liegt nahe an "
        "den Werten hier.",
        "",
        "**Unterschiede zwischen Themen (Bezug zu TF2):** Burtch et al. (Abschnitt "
        "„Heterogeneity … by topic“) finden die stärksten Rückgänge bei Themen der konkreten, "
        "abgeschlossenen Programmierarbeit und kaum Veränderung bei Spring, AWS, Firebase, "
        "Docker, SQL Server und Azure. del Rio-Chanona et al. nennen Python und JavaScript unter "
        "den am stärksten betroffenen Sprachen. Behaltensquote (Anteil 2024 / Anteil 2022, "
        "1 = wie Stack Overflow insgesamt; Gruppe der Hauptauswertung in Klammern) für die von "
        "Burtch et al. genannten Tags:",
        "",
        f"- stark betroffen laut Burtch et al.: {tag_list(BURTCH_STRONG)} – Median "
        f"**{de(median(strong), 2)}**",
        f"- kaum betroffen laut Burtch et al.: {tag_list(BURTCH_WEAK)} – Median "
        f"**{de(median(weak), 2)}**",
        "",
        "Die Richtung stimmt mit dem Gruppenvergleich hier überein (Umgebungs-Tags behalten "
        "ihren Anteil eher). Burtch et al. betrachten einen kürzeren Zeitraum und andere "
        "Vergleiche; die Übereinstimmung ist ein Hinweis, keine Bestätigung.",
        "",
    ]


def new_types(lines: list[str]) -> None:
    nt = pl.read_csv(P / "new_types.csv")
    lines += [
        "## Neue Fragetypen (aus den Daten, AP02/T9)",
        "",
        "| Jahr | Typ | Fragen | Anteil Score 0 | Antworten je Frage | unbeantwortet | "
        "akzeptiert | geschlossen |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in nt.iter_rows(named=True):
        lines.append(
            f"| {r['year']} | {r['typ']} | {r['n_questions']} | {de(100 * r['score_zero_share'], 0)} % "  # noqa: E501
            f"| {de(r['answers_per_q_mean'], 2)} | {de(100 * r['unanswered_share'], 0)} % "
            f"| {de(100 * r['accepted_share'], 0)} % | {de(100 * r['closed_share'], 0)} % |"
        )
    lines += [
        "",
        "2025 erhielten die neuen Typen kaum Votes (74–89 % mit Score 0) und fast keine "
        "akzeptierte Antwort; 2026 tragen sie Votes und häufiger eine akzeptierte Antwort. Das "
        "stützt die getrennte Behandlung (plan.md 5.1). Die Durchsicht auf der Website (5 + 5 "
        "Fragen) war optional und entfällt.",
        "",
    ]


def answer_check(lines: list[str]) -> None:
    """Prüfung zu AP14: 10 Antworten erneut abfragen; Anteil ohne Konto je Jahr."""
    cols = ["answer_id", "question_id", "year", "created", "is_accepted", "owner_user_id",
            "in_window"]  # fmt: skip
    a = load_answers(cols)
    ids = draw_check_answers(a, 10, config.SEED + 121)
    st = {r["answer_id"]: r for r in a.filter(pl.col("answer_id").is_in(ids)).iter_rows(named=True)}
    raw = fetch_answers(ids)
    api = {x["answer_id"]: x for x in raw["answers"]}
    rows = []
    for nr, aid in enumerate(ids, 1):
        s = st[aid]
        stored = {
            "question_id": s["question_id"],
            "created": s["created"],
            "is_accepted": s["is_accepted"],
            "owner": owner_hash(s["owner_user_id"]),
        }
        c = compare_answer(stored, api.get(aid))
        rows.append({"nr": nr, "link": f"https://stackoverflow.com/a/{aid}", "jahr": s["year"],
                     "mit_konto": stored["owner"] is not None, **c})  # fmt: skip
    out = config.CODING_DIR / "checks" / "antworten_10.csv"
    out.write_text(pl.DataFrame(rows).write_csv(separator=";"), encoding="utf-8-sig")
    yn = {True: "ja", False: "nein"}
    lines += [
        "## Antwortende: 10 Antworten mit der API abgeglichen (Prüfung zu AP14)",
        "",
        "Zufällige Antworten aus dem 7-Tage-Fenster aller Jahre (Seed + 121). Verglichen werden "
        "Frage, Erstellzeit, Konto (nur als Hash, keine Nutzer-IDs) und Akzeptanz. Einzelwerte: "
        "`coding/checks/antworten_10.csv`.",
        "",
        "| Nr. | Antwort | Jahr | mit Konto | Frage | Zeit | Konto | akzeptiert | Erklärung |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['nr']} | [{r['link'].rsplit('/', 1)[1]}]({r['link']}) | {r['jahr']} "
            f"| {yn[r['mit_konto']]} | {yn[r['frage_gleich']]} | {yn[r['zeit_gleich']]} "
            f"| {yn[r['konto_gleich']]} | {yn[r['akzeptiert_gleich']]} | {r['erklaerung'] or '–'} |"
        )
    n_ok = sum(r["gleich"] for r in rows)
    lines += ["", f"**Ergebnis:** {n_ok} von {len(rows)} Antworten stimmen in allen Feldern "
              "mit der Website überein.", ""]  # fmt: skip
    classic = load_questions(["question_id", "is_classic"]).filter(pl.col("is_classic"))
    share = (
        a.filter(pl.col("in_window"))
        .join(classic.select("question_id"), on="question_id")
        .group_by("year")
        .agg(n=pl.len(), ohne=pl.col("owner_user_id").is_null().sum())
        .sort("year")
    )
    lines += [
        "Anteil der Antworten ohne Konto (gelöschte Konten; im Fenster, klassische Fragen), "
        "in AP14 nicht gezählt (D17):",
        "",
        "| Jahr | " + " | ".join(str(y) for y in share["year"]) + " |",
        "|---|" + "---|" * share.height,
        "| ohne Konto | "
        + " | ".join(f"{de(100 * o / n)} %" for n, o in share.select("n", "ohne").iter_rows())
        + " |",
        "",
    ]


def main() -> None:
    q = load_questions(["question_id", "year", "is_new_type"])
    sample = draw_check_questions(q, config.SEED + 120)
    ids = sample["question_id"].to_list()
    stored = stored_records(ids)
    raw = fetch(ids)
    api_q = {it["question_id"]: it for it in raw["questions"]}
    api_a: dict[int, list[dict]] = {}
    for a in raw["answers"]:
        api_a.setdefault(a["question_id"], []).append(a)

    rows, devs = [], []
    for nr, r in enumerate(sample.iter_rows(named=True), 1):
        qid = r["question_id"]
        st = stored[qid]
        api = api_features(api_q[qid], api_a.get(qid, [])) if qid in api_q else None
        cmp = compare_question(st, api)
        for c in cmp:
            if not c["gleich"]:
                devs.append({"nr": nr, "question_id": qid, **c})
        val = {c["feld"]: c for c in cmp}
        rows.append({
            "nr": nr,
            "link": f"https://stackoverflow.com/q/{qid}",
            "jahr": r["year"],
            "typ": "neuer Fragetyp" if st["is_new_type"] else "klassisch",
            "erstellzeit_utc": val["Erstellzeit"]["gespeichert"],
            "tags": val["Tags"]["gespeichert"],
            "antworten_fenster": val["Antworten im Fenster"]["gespeichert"],
            "erste_antwort_h": val["Zeit bis zur ersten Antwort (h)"]["gespeichert"],
            "akzeptiert_fenster": val["akzeptiert im Fenster"]["gespeichert"],
            "api_antworten_fenster": val["Antworten im Fenster"]["api"],
            "api_erste_antwort_h": val["Zeit bis zur ersten Antwort (h)"]["api"],
            "api_akzeptiert_fenster": val["akzeptiert im Fenster"]["api"],
            "abweichende_felder": ", ".join(c["feld"] for c in cmp if not c["gleich"]),
        })  # fmt: skip
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.write_text(pl.DataFrame(rows).write_csv(separator=";"), encoding="utf-8-sig")

    years = sorted(sample["year"].unique().to_list())
    dl = sorted({download_date(y) for y in years})
    n_q = len(ids)
    L = [
        "# Datenprüfung und Literaturabgleich (AP12)",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M}. API-Abfrage: "
        f"{datetime.fromisoformat(raw['abgerufen']):%d.%m.%Y %H:%M} UTC; Download der Rohdaten "
        f"{dl[0]}–{dl[-1]}.",
        "",
        "## Abgleich von 20 Fragen mit der API",
        "",
        f"Stichprobe (D31): je Oktober 2008–2026 eine zufällige Frage und eine Frage eines "
        f"neuen Fragetyps (Seed + 120), zusammen {n_q}. Die gespeicherten Werte (AP01) werden "
        "mit einer erneuten Abfrage verglichen; Antworten im Fenster nach plan.md 5.2. "
        "Einzelwerte: `coding/checks/datenpruefung_20.csv`.",
        "",
        "| Feld | gleich | abweichend, erklärt | abweichend, nicht erklärt |",
        "|---|---|---|---|",
    ]
    for f in FIELDS:
        d = [x for x in devs if x["feld"] == f]
        unexplained = sum(x["erklaerung"] in ("", "nicht erklärbar") for x in d)
        L.append(f"| {f} | {n_q - len(d)} | {len(d) - unexplained} | {unexplained} |")
    key_bad = [x for x in devs if x["feld"] in KEY_FIELDS]
    key_unexpl = [x for x in key_bad if x["erklaerung"] in ("", "nicht erklärbar")]
    L += ["", "Abweichungen im Einzelnen:", ""]
    if devs:
        L += ["| Nr. | Frage | Feld | gespeichert | heute (API) | Erklärung |",
              "|---|---|---|---|---|---|"]  # fmt: skip
        for x in devs:
            L.append(
                f"| {x['nr']} | [{x['question_id']}](https://stackoverflow.com/q/{x['question_id']}) "  # noqa: E501
                f"| {x['feld']} | {x['gespeichert']} | {x['api']} | {x['erklaerung']} |"
            )
    else:
        L.append("keine")
    L += [
        "",
        f"**Ergebnis:** In den Feldern, aus denen die Kennzahlen entstehen, gibt es "
        f"{len(key_bad)} Abweichungen bei {len({x['question_id'] for x in key_bad})} von {n_q} "
        f"Fragen, davon {len(key_unexpl)} nicht erklärt. "
        + (
            "Die Datenbasis stimmt mit der Website überein; Abweichungen entstehen nur durch "
            "spätere Änderungen auf der Website."
            if not key_unexpl
            else "Die nicht erklärten Abweichungen müssen geprüft werden."
        )
        + " Der heutige `answer_count` geht in keine Kennzahl ein (plan.md 5.2).",
        "",
    ]
    answer_check(L)
    new_types(L)
    literature(L)
    (config.RESULTS_DIR / "checks.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()

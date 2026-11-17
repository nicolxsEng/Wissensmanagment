"""AP16: Einordnung durch zwei lokale Sprachmodelle (Qwen3.5-9B, Phi-4 14B; D22, D24).

uv run python scripts/16_llm_coding.py kal-tags     # Kalibrierung: 40 Nicht-Kandidaten-Tags
uv run python scripts/16_llm_coding.py kal-fragen   # Kalibrierung: 30 Kalibrierungsfragen
uv run python scripts/16_llm_coding.py tags         # alle Kandidaten-Tags (269)
uv run python scripts/16_llm_coding.py fragen       # 600 Stichprobenfragen

Die Modelle laufen nacheinander (SOV_LLM_PARALLEL=1: parallel). Antworten werden gespeichert
(results/llm/*.jsonl) und bei einem erneuten Lauf mit gleichem Prompt und Modell wiederverwendet.
"""

import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import polars as pl

from sov import config
from sov.agreement import crosstab, kappa_ci, landis_koch
from sov.coding import read_sheet
from sov.llm import load_prompt, model_digests, run_task

KEYS = list(config.LLM_CODERS)  # die zwei Kodierinstanzen


def tag_items(df: pl.DataFrame) -> list[tuple[str, str]]:
    return [
        (t, f"Tag: {t}\nTag wiki excerpt: {w or '(no wiki)'}")
        for t, w in zip(df["tag"], df["wiki_auszug"], strict=True)
    ]


def question_items(set_name: str) -> list[tuple[str, str]]:
    df = pl.read_parquet(config.PROCESSED_DIR / "classify_coded_inputs.parquet")
    df = df.filter(pl.col("set") == set_name).sort("code")
    return [(c, t[: config.LLM_INPUT_MAX_CHARS]) for c, t in zip(df["code"], df["text"],
                                                                 strict=True)]  # fmt: skip


def run_both(task: str, items, prompt: str, cats) -> dict[str, pl.DataFrame]:
    digests = model_digests()
    with ThreadPoolExecutor(max_workers=len(KEYS) if config.LLM_PARALLEL else 1) as ex:
        futs = {
            k: ex.submit(run_task, task, k, items, prompt, cats,
                         digest=digests.get(config.LLM_MODELS[k], "unbekannt"))
            for k in KEYS
        }  # fmt: skip
        return {k: f.result() for k, f in futs.items()}


def report(task: str, res: dict[str, pl.DataFrame], cats, prompt: str, titles=None) -> str:
    a, b = res[KEYS[0]], res[KEYS[1]]
    ok = a["kategorie"].is_not_null() & b["kategorie"].is_not_null()
    ka = kappa_ci(a.filter(ok)["kategorie"].to_list(), b.filter(ok)["kategorie"].to_list(),
                  list(cats))  # fmt: skip
    _, phash = load_prompt(prompt)
    lines = [
        f"# {task} – Übereinstimmung der Modelle",
        "",
        f"Erzeugt: {datetime.now():%d.%m.%Y %H:%M} · Prompt `{prompt}` ({phash}) · "
        f"Modelle: {', '.join(config.LLM_MODELS[k] for k in KEYS)}",
        "",
        f"- Einträge: {len(a)} (ungültig: {int((~ok).sum())})",
        f"- Cohens Kappa: **{ka['kappa']:.2f}** [{ka['ci_low']:.2f}; {ka['ci_high']:.2f}] "
        f"({landis_koch(ka['kappa'])}), Übereinstimmung {ka['uebereinstimmung']:.0%}",
        "",
        "Verteilung:",
        "",
        "| Kategorie | " + " | ".join(KEYS) + " |",
        "|---|" + "---|" * len(KEYS),
    ]
    for c in cats:
        lines.append(f"| {c} | " + " | ".join(str((res[k]["kategorie"] == c).sum()) for k in KEYS)
                     + " |")  # fmt: skip
    ct = crosstab(a.filter(ok)["kategorie"].to_list(), b.filter(ok)["kategorie"].to_list(),
                  list(cats), KEYS[0], KEYS[1])  # fmt: skip
    lines += ["", f"Kreuztabelle (Zeilen {KEYS[0]}, Spalten {KEYS[1]}):", "",
              "| | " + " | ".join(cats) + " |", "|---|" + "---|" * len(cats)]  # fmt: skip
    for r in ct.to_dicts():
        lines.append(f"| {r[KEYS[0]]} | " + " | ".join(str(r[c]) for c in cats) + " |")
    if titles is not None:
        diff = a.join(b, on="id", suffix="_b").filter(pl.col("kategorie") != pl.col("kategorie_b"))
        lines += ["", "Abweichungen:", ""]
        for r in diff.to_dicts():
            lines.append(f"- `{r['id']}` {titles.get(r['id'], '')[:80]} – {KEYS[0]}: "
                         f"{r['kategorie']} ({r['begruendung'][:90]}) / {KEYS[1]}: "
                         f"{r['kategorie_b']} ({r['begruendung_b'][:90]})")  # fmt: skip
    return "\n".join(lines) + "\n", ka


def main() -> None:
    step = sys.argv[1] if len(sys.argv) > 1 else "kal-tags"
    config.LLM_DIR.mkdir(parents=True, exist_ok=True)
    if step in ("kal-tags", "tags"):
        cats = config.TAG_CATEGORIES
        if step == "kal-tags":
            df = pl.concat([read_sheet(config.CODING_DIR / "tags" / f).select("tag", "wiki_auszug")
                            for f in ("uebung_10.csv", "kalibrierung_30.csv")])  # fmt: skip
            cand = set(pl.read_csv(config.PROCESSED_DIR / "tag_wiki.csv")["tag"])
            assert not set(df["tag"]) & cand, "Kalibrierungstags dürfen keine Kandidaten sein"
        else:
            df = pl.read_csv(config.PROCESSED_DIR / "tag_wiki.csv")
        res = run_both(step, tag_items(df), "tags", cats)
        titles = {t: t for t in df["tag"]} if step == "kal-tags" else None
    else:
        cats = config.QUESTION_CATEGORIES
        set_name = "kalibrierung" if step == "kal-fragen" else "stichprobe"
        items = question_items(set_name)
        res = run_both(step, items, "fragen", cats)
        titles = None
        if step == "kal-fragen":
            v = pl.read_parquet(config.CODING_DIR / "questions" / "ansicht.parquet")
            titles = dict(zip(v["code"], v["title"], strict=True))
    text, ka = report(step, res, cats, "tags" if "tags" in step else "fragen", titles)
    _, phash = load_prompt("tags" if "tags" in step else "fragen")
    (config.LLM_DIR / f"bericht_{step}.md").write_text(text, encoding="utf-8")
    (config.LLM_DIR / f"bericht_{step}_{phash}.md").write_text(text, encoding="utf-8")
    if step in ("tags", "fragen"):
        folder = "tags" if step == "tags" else "questions"
        idcol = "tag" if step == "tags" else "code"
        for k, df in res.items():
            df.rename({"id": idcol}).write_csv(
                config.CODING_DIR / folder / f"llm_{step}_{k}.csv", separator=";", include_bom=True
            )
    print(text)


if __name__ == "__main__":
    main()

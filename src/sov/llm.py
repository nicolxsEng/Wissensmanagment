"""AP16: Einordnung durch lokale Sprachmodelle über Ollama (D22, docs/modellwahl.md).

- feste Einstellungen: Temperatur 0, Seed, Denkmodus aus, Ausgabe als JSON nach Schema
- jede Antwort wird als Zeile in results/llm/<aufgabe>_<modell>.jsonl gespeichert; ein erneuter
  Lauf überspringt Einträge mit gleichem Modell-Digest und gleichem Prompt (Prompt-Hash)
- nur lokale Modelle, keine Texte an externe Dienste
"""

import hashlib
import json
import time
import urllib.request
from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path

import polars as pl

from sov import config


def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def load_prompt(name: str) -> tuple[str, str]:
    """System-Prompt aus config/prompts/<name>.md (ohne Kopfzeilen mit '%%'). -> (text, hash)"""
    raw = (config.PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
    text = "\n".join(line for line in raw.splitlines() if not line.startswith("%%")).strip()
    return text, prompt_hash(text)


def label_schema(categories: Iterable[str]) -> dict:
    """Begründung VOR der Kategorie: das Modell legt sich erst nach der Begründung fest."""
    return {
        "type": "object",
        "properties": {
            "begruendung": {"type": "string"},
            "kategorie": {"type": "string", "enum": list(categories)},
        },
        "required": ["begruendung", "kategorie"],
    }


def _post(path: str, body: dict, timeout: int = 300) -> dict:
    req = urllib.request.Request(
        f"{config.OLLAMA_URL}{path}",
        json.dumps(body).encode("utf-8"),
        {"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def model_digests() -> dict[str, str]:
    with urllib.request.urlopen(f"{config.OLLAMA_URL}/api/tags", timeout=30) as r:
        tags = json.loads(r.read())
    return {m["name"]: m["digest"] for m in tags["models"]}


def ask(
    model: str,
    system: str,
    user: str,
    schema: dict,
    accept: Callable[[dict], str | None],
    post: Callable[[str, dict], dict] = _post,
    retries: int = 2,
) -> dict:
    """Eine Anfrage mit JSON-Schema; `accept` prüft die Antwort und liefert den Wert (oder None).

    Bei ungültiger Antwort bis zu `retries` Wiederholungen. Der Wert steht unter "kategorie"
    (bei der Benennung: der Name), damit Speicher und Auswertung für alle Aufgaben gleich sind.
    """
    body = {
        "model": model,
        "stream": False,
        "think": False,
        "format": schema,
        "options": {"temperature": 0, "seed": config.SEED, "num_ctx": config.LLM_NUM_CTX,
                    "num_predict": config.LLM_NUM_PREDICT},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }  # fmt: skip
    last = ""
    for attempt in range(retries + 1):
        t0 = time.perf_counter()
        try:
            resp = post("/api/chat", body)
        except (TimeoutError, OSError) as e:  # Zeitüberschreitung: als ungültig werten
            last = f"Fehler: {e}"
            continue
        last = resp.get("message", {}).get("content", "")
        try:
            data = json.loads(last)
        except json.JSONDecodeError:
            continue
        value = accept(data) if isinstance(data, dict) else None
        if value:
            return {
                "kategorie": value,
                "begruendung": str(data.get("begruendung", "")).strip(),
                "dauer_s": round(time.perf_counter() - t0, 2),
                "versuche": attempt + 1,
            }
    return {"kategorie": None, "begruendung": f"UNGÜLTIG: {last[:200]}", "dauer_s": None,
            "versuche": retries + 1}  # fmt: skip


def classify_one(
    model: str,
    system: str,
    user: str,
    categories: Iterable[str],
    post: Callable[[str, dict], dict] = _post,
    retries: int = 2,
) -> dict:
    """Eine Einordnung in eine der Kategorien."""
    cats = list(categories)
    return ask(model, system, user, label_schema(cats),
               lambda d: d.get("kategorie") if d.get("kategorie") in cats else None,
               post=post, retries=retries)  # fmt: skip


NAME_SCHEMA = {
    "type": "object",
    "properties": {"begruendung": {"type": "string"}, "name": {"type": "string"}},
    "required": ["begruendung", "name"],
}
NAME_MAX_CHARS = 60


def _accept_name(d: dict) -> str | None:
    name = " ".join(str(d.get("name", "")).split()).strip(" .\"'")
    return name if 0 < len(name) <= NAME_MAX_CHARS else None


def name_one(
    model: str,
    system: str,
    user: str,
    post: Callable[[str, dict], dict] = _post,
    retries: int = 2,
) -> dict:
    """Ein kurzer Name (Themenbenennung, AP11); Wert unter "kategorie"."""
    return ask(model, system, user, NAME_SCHEMA, _accept_name, post=post, retries=retries)


def run_task(
    task: str,
    model_key: str,
    items: list[tuple[str, str]],
    prompt_name: str,
    categories: Iterable[str],
    out_dir: Path | None = None,
    post: Callable[[str, dict], dict] = _post,
    digest: str | None = None,
    progress: bool = True,
    call: Callable[..., dict] | None = None,
) -> pl.DataFrame:
    """Ordnet alle (id, text) ein; bereits gespeicherte Antworten werden wiederverwendet.

    `call(model, system, text, post=...)` ersetzt die Einordnung (z. B. `name_one`).
    """
    out_dir = out_dir or config.LLM_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    model = config.LLM_MODELS[model_key]
    system, phash = load_prompt(prompt_name)
    digest = digest or model_digests().get(model, "unbekannt")
    path = out_dir / f"{task}_{model_key}.jsonl"
    done: dict[str, dict] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r["prompt_hash"] == phash and r["digest"] == digest and r["kategorie"]:
                done[r["id"]] = r
    todo = [(i, t) for i, t in items if i not in done]
    t0 = time.perf_counter()
    with path.open("a", encoding="utf-8") as f:
        for n, (item_id, text) in enumerate(todo, 1):
            res = (
                call(model, system, text, post=post)
                if call
                else classify_one(model, system, text, categories, post=post)
            )
            rec = {"id": item_id, "task": task, "model": model, "digest": digest,
                   "prompt": prompt_name, "prompt_hash": phash,
                   "zeit": datetime.now().isoformat(timespec="seconds"), **res}  # fmt: skip
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            done[item_id] = rec
            if progress and (n % 25 == 0 or n == len(todo)):
                el = time.perf_counter() - t0
                print(f"  {task}/{model_key}: {n}/{len(todo)} ({el / n:.1f} s je Eintrag)",
                      flush=True)  # fmt: skip
    rows = [done[i] for i, _ in items]
    return pl.DataFrame(
        [{"id": r["id"], "kategorie": r["kategorie"], "begruendung": r["begruendung"]}
         for r in rows],
        schema={"id": pl.String, "kategorie": pl.String, "begruendung": pl.String},
    )  # fmt: skip

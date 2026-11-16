"""AP16: LLM-Baustein ohne echtes Modell (Ollama wird durch eine Attrappe ersetzt)."""

import json

from sov import config
from sov.llm import classify_one, label_schema, prompt_hash, run_task


def fake_post_factory(answers):
    calls = []

    def post(path, body):
        calls.append(body)
        return {"message": {"content": answers[min(len(calls) - 1, len(answers) - 1)]}}

    return post, calls


def test_schema_and_settings():
    s = label_schema(["G", "U", "S"])
    assert list(s["properties"]) == ["begruendung", "kategorie"]
    post, calls = fake_post_factory(['{"begruendung": "x", "kategorie": "G"}'])
    res = classify_one("m", "sys", "frage", ["G", "U", "S"], post=post)
    assert res["kategorie"] == "G"
    opts = calls[0]["options"]
    assert opts["temperature"] == 0 and opts["seed"] == config.SEED
    assert calls[0]["think"] is False


def test_retry_on_invalid_then_give_up():
    post, calls = fake_post_factory(
        ["kein json", '{"kategorie": "X"}', '{"begruendung": "b", "kategorie": "U"}']
    )
    assert classify_one("m", "s", "q", ["G", "U"], post=post)["kategorie"] == "U"
    post, calls = fake_post_factory(["kaputt"])
    res = classify_one("m", "s", "q", ["G", "U"], post=post, retries=2)
    assert res["kategorie"] is None and len(calls) == 3


def test_run_task_caches(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PROMPT_DIR", tmp_path)
    (tmp_path / "p.md").write_text("%% Kopf\nAnweisung", encoding="utf-8")
    post, calls = fake_post_factory(['{"begruendung": "b", "kategorie": "G"}'])
    items = [("a", "t1"), ("b", "t2")]
    df = run_task("t", "qwen", items, "p", ["G", "U"], out_dir=tmp_path, post=post, digest="d1",
                  progress=False)  # fmt: skip
    assert df["kategorie"].to_list() == ["G", "G"] and len(calls) == 2
    run_task("t", "qwen", items, "p", ["G", "U"], out_dir=tmp_path, post=post, digest="d1",
             progress=False)  # fmt: skip
    assert len(calls) == 2  # aus dem Speicher
    run_task("t", "qwen", items, "p", ["G", "U"], out_dir=tmp_path, post=post, digest="d2",
             progress=False)  # fmt: skip
    assert len(calls) == 4  # anderes Modell-Digest -> neu
    rec = json.loads((tmp_path / "t_qwen.jsonl").read_text().splitlines()[0])
    assert rec["prompt_hash"] == prompt_hash("Anweisung")

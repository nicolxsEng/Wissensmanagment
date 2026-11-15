"""Rauchtest für AP00: Konfiguration, Rohdaten-Pfad, Stil."""

import matplotlib

matplotlib.use("Agg")

from sov import config
from sov.plotting import style


def test_config_constants():
    assert len(config.YEARS) == 19
    assert list(range(2015, 2023)) == config.PRE_YEARS
    assert config.POST_YEARS == [2023, 2024, 2025, 2026]
    assert len(config.AI_TAGS) == 26
    assert config.SAMPLE_PER_YEAR * len(config.SAMPLE_YEARS) == 600


def test_raw_data_present():
    for year in config.YEARS:
        d = config.RAW_DIR / str(year)
        assert (d / "questions.jsonl.gz").exists(), d
        assert (d / "answers.jsonl.gz").exists(), d


def test_de_formatter():
    f = style.de_formatter(1, " %")
    assert f(12345.67, 0) == "12.345,7 %"

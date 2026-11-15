"""Alle Konstanten und Pfade des Projekts (Definitionen siehe plan.md, Abschnitt 5).

Änderungen hier verändern Ergebnisse -> immer in docs/entscheidungen.md protokollieren.
"""

import os
from datetime import UTC, datetime
from pathlib import Path

# --- Pfade
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = Path(os.environ.get("SOV_RAW_DIR", PROJECT_ROOT.parent / "Datentest")).resolve()
SE_API_SCRIPTS = RAW_DIR / "scripts"  # se_api.py (Stack-Exchange-Key bleibt in RAW_DIR/.env)

DATA_DIR = PROJECT_ROOT / "data"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
CODING_DIR = PROJECT_ROOT / "coding"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "figures"
TABLES_DIR = PROJECT_ROOT / "tables"
CONFIG_DIR = PROJECT_ROOT / "config"

QUESTIONS_PARQUET = INTERIM_DIR / "questions.parquet"
ANSWERS_PARQUET = INTERIM_DIR / "answers.parquet"
TEXTS_PARQUET = INTERIM_DIR / "texts.parquet"

# --- Zeitraum (plan.md 5.1, Exposé 4.2)
MONTH = 10
YEARS = list(range(2008, 2027))  # 19 Oktober-Monate
TREND_START = 2015  # Trendvergleich ab 2015
BASE_YEAR = 2022  # letzter voller Monat vor ChatGPT, Index = 100
MAIN_POST_YEAR = 2024  # Hauptvergleichsjahr nach ChatGPT
CONFIRM_YEARS = (2025, 2026)  # nur Bestätigung (kleine Fallzahlen)
PRE_YEARS = [y for y in YEARS if TREND_START <= y <= BASE_YEAR]  # 2015–2022
POST_YEARS = [y for y in YEARS if y > BASE_YEAR]  # 2023–2026
CHATGPT_RELEASE = datetime(2022, 11, 30, tzinfo=UTC)

# --- Antwortverhalten (plan.md 5.2)
ANSWER_WINDOW_HOURS = 7 * 24
FAST_ANSWER_HOURS = 24

# --- Fragetypen und Tags
NEW_TYPE_TAGS = frozenset({"advice", "best-practices"})  # neue Fragetypen ab Okt. 2025
AI_TAGS = frozenset(
    line.strip()
    for line in (CONFIG_DIR / "ai_tags.txt").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
)
MIN_TAG_COUNT = 150  # Kandidaten-Tags: >= 150 klassische Fragen im Oktober 2022
N_TAGS_EXPECTED = 272

# --- Kodierung und Stichproben
SEED = 20261116
TAG_CATEGORIES = ("G", "U", "K")  # Grundlagen, Umgebung, keine
QUESTION_CATEGORIES = ("G", "U", "S")  # Grundlagen, Umgebung, Sonstige
CALIBRATION_N = 30
SAMPLE_YEARS = list(range(2015, 2027))
SAMPLE_PER_YEAR = 50  # 600 Fragen
DOUBLE_CODED_N = 150
CODING_VIEW_MAX_CHARS = 4000
KAPPA_MIN = 0.61  # Landis & Koch (1977): substanziell
MACRO_F1_MIN = 0.70

# --- Gruppenvergleich (AP07)
N_PERMUTATIONS = 10_000
PLACEBO_BASE_YEAR = 2019
PLACEBO_COMPARE_YEAR = 2021

# --- Klassifikation und Themen (AP10, AP11)
CLASSIFY_PER_YEAR = 2000  # 2026: alle klassischen Fragen
TOPIC_PILOT_N = 1000
TOPIC_YEARS = list(range(2015, 2027))  # Titel je Jahr = Anzahl klassischer Fragen 2026
TOPIC_CHECK_TITLES = 10
TOPIC_CHECK_MIN_FIT = 8

# Nur lokale Modelle (D10). Einmal von Hugging Face laden, danach offline. Vor dem ersten
# echten Lauf die Revision (Commit-Hash) eintragen, damit Ergebnisse wiederholbar bleiben.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # BERTopic (AP11)
EMBEDDING_MODEL_ALT = "sentence-transformers/all-mpnet-base-v2"
SETFIT_BASE_MODEL = "sentence-transformers/all-mpnet-base-v2"  # SetFit (AP10)
ZERO_SHOT_MODEL = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"  # Zero-Shot (AP10)
ZERO_SHOT_MODEL_ALT = "MoritzLaurer/deberta-v3-base-zeroshot-v2.0"  # kleiner, schneller
MODEL_REVISIONS: dict[str, str] = {}  # Modellname -> Commit-Hash, beim ersten Lauf füllen
TOPIC_N_RANGE = (20, 40)

# --- Sichtbare Antwortende (AP14)
EXPERT_MIN_ANSWERS = 3  # erkennbare Expert:innen: >= 3 Antworten je Gruppe und Oktober
EXPERT_MIN_ANSWERS_ROBUST = (2, 5)  # Gegenproben
TOP_ANSWERER_SHARE = 0.10  # Konzentration: Anteil der Antworten der aktivsten 10 %

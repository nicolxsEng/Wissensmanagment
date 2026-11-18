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
# Neue Fragetypen: Tag UND gestellt ab Oktober 2025. Beide Tags kommen vorher vereinzelt als
# normale Tags vor (13 Fragen 2008–2020), die bleiben klassisch (D02, Datenprotokoll AP01).
NEW_TYPE_TAGS = frozenset({"advice", "best-practices"})
NEW_TYPE_START = datetime(2025, 10, 1, tzinfo=UTC)
AI_TAGS = frozenset(
    line.strip()
    for line in (CONFIG_DIR / "ai_tags.txt").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
)
MIN_TAG_COUNT = 150  # Kandidaten-Tags: >= 150 klassische Fragen im Oktober 2022
N_TAGS_EXPECTED_RAW = 272  # Exposé, rohe Tags
N_TAGS_EXPECTED = 269  # nach Zusammenführen der Synonyme (D15)

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
# Menschliche Prüfung (D29): Stichproben und Kriterium je Gruppe
PRUEF_TAGS_N = 40
PRUEF_FRAGEN_N = 100
PRUEF_GRUPPE_MIN = 0.80  # Anteil der Gruppen-Tags, die ein Mensch genauso einordnet

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

# --- Lokale Sprachmodelle als Kodierinstanzen (AP16, D22; Begründung docs/modellwahl.md)
OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LLM_MODELS = {
    "qwen": "qwen3.5:9b",
    "olmo": "olmo-3:7b-instruct",  # in der Kalibrierung ausgeschieden (D24), nur dokumentiert
    "phi": "phi4:14b",  # Kodierinstanz 2 seit 16.11.2026 (D24)
}
# Die zwei Kodierinstanzen (Schlüssel aus LLM_MODELS); per Umgebungsvariable überschreibbar
LLM_CODERS = tuple(os.environ.get("SOV_LLM_CODERS", "qwen,phi").split(","))
LLM_PARALLEL = os.environ.get("SOV_LLM_PARALLEL", "0") == "1"  # beide Modelle gleichzeitig?
LLM_NUM_CTX = 4096
LLM_NUM_PREDICT = 512  # Obergrenze der Antwortlänge (Schutz vor Endlosschleifen, 16.11.2026)
LLM_INPUT_MAX_CHARS = 3000  # Fragetext für die Modelle (Titel, Text, Code-Auszug)
PROMPT_DIR = CONFIG_DIR / "prompts"
LLM_DIR = RESULTS_DIR / "llm"

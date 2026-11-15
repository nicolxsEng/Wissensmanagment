# Pipeline. Jedes Ziel entspricht einem Arbeitspaket in plan.md.
# Skripte, die noch nicht existieren, legt Claude Code mit /ap APxx an.
PY := uv run python

.PHONY: help setup test lint data metrics tags coding-tags agreement-tags samples groups its \
        agreement-questions classify topics checks answerers ai-mentions figures tables report all

help:
	@grep -E '^[a-z-]+:.*## ' Makefile | awk 'BEGIN{FS=":.*## "}{printf "  %-20s %s\n", $$1, $$2}'

setup: ## AP00 Abhängigkeiten installieren
	uv sync

test: ## Tests ausführen
	uv run pytest -q

lint: ## Stil prüfen und formatieren
	uv run ruff check . --fix && uv run ruff format .

data: ## AP01 Rohdaten -> data/interim/*.parquet
	$(PY) scripts/01_build_dataset.py

metrics: ## AP02 Kennzahlen TF1/TF3
	$(PY) scripts/02_metrics.py

tags: ## AP03 Kandidaten-Tags, Wiki-Auszüge, Synonyme, Brüche
	$(PY) scripts/03_tag_audit.py

coding-tags: ## AP04 Kodierbögen für Tags erzeugen
	$(PY) scripts/04_tag_sheets.py

agreement-tags: ## AP05 Kappa Tags, Gruppen festlegen
	$(PY) scripts/05_tag_agreement.py

samples: ## AP06 Stichproben für Kalibrierung und Kodierung
	$(PY) scripts/06_samples.py

groups: ## AP07 Gruppenindex, Permutation, Weglassen, Placebo
	$(PY) scripts/07_group_compare.py

its: ## AP08 Unterbrochene Zeitreihe
	$(PY) scripts/08_its.py

agreement-questions: ## AP09 Kappa Doppelkodierung, Labels
	$(PY) scripts/09_question_agreement.py

classify: ## AP10 Klassifikation (lokal; Zero-Shot läuft länger)
	$(PY) scripts/10_classify.py

topics: ## AP11 Themenanalyse
	$(PY) scripts/11_topics.py

checks: ## AP12 Datenprüfung und Literaturabgleich
	$(PY) scripts/12_checks.py

answerers: ## AP14 sichtbare Antwortende
	$(PY) scripts/14_answerers.py

ai-mentions: ## AP15 KI-Erwähnungen im Fragetext (optional)
	$(PY) scripts/15_ai_mentions.py

figures: ## AP13 alle Abbildungen -> figures/
	$(PY) scripts/13_figures.py

tables: ## AP13 alle Tabellen -> tables/
	$(PY) scripts/13_tables.py

report: ## AP13 results/kennzahlen.json und results/ergebnisse.md
	$(PY) scripts/13_report.py

all: data metrics tags groups its answerers figures tables report ## alles, was ohne menschliche Kodierung läuft

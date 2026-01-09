.PHONY: setup chat live
setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
chat:
	. .venv/bin/activate && python iris_cli.py chat "$(PROMPT)"
live:
	. .venv/bin/activate && python iris_cli.py live
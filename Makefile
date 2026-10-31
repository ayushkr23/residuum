.PHONY: install test reproduce demo live

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

reproduce:
	python -m residuum.experiment

reproduce-quick:
	python -m residuum.experiment --quick

demo:
	python -m residuum.server --port 8765

live:
	python -m residuum.server --live --port 8765

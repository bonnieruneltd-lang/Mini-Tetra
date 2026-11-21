PY ?= python3

.PHONY: evaluate variants fast test head-check clean

evaluate:
	$(PY) -m minitetra.cli evaluate --json out/report.json --markdown reports/best3.md

variants:
	$(PY) -m minitetra.cli evaluate --variants

fast:
	$(PY) -m minitetra.cli evaluate --fast

test:
	$(PY) -m unittest discover -s tests -v

head-check:
	$(PY) -m minitetra.cli head-check --platform itx_sff --gpu rtx5060ti_16

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +

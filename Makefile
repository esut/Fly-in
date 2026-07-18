PYTHON = python3
PIP = pip
MAIN = src/main.py

install:
	$(PIP) install mypy flake8

run:
	python -m src.main maps/easy/01_linear_path.txt

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -r {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run debug clean lint lint-strict
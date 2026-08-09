
PYTHON = python3
UV = uv
SRC = main.py
MAP_FILE = maps/easy/01_linear_path.txt


install:
	$(UV) sync

run:
	$(UV) run $(PYTHON)  $(SRC) $(MAP_FILE)

debug:
	$(UV) $(PYTHON)  pdb $(MAIN_SCRIPT) $(MAP_FILE)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	flake8 src
	mypy src --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 src
	mypy src --strict

.PHONY: install run debug clean lint lint-strict

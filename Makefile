.PHONY: install lint format test ci

install:
	python -m pip install --upgrade pip
	pip install ruff black pytest
	if [ -f backend/requirements.txt ]; then pip install -r backend/requirements.txt; fi

lint:
	ruff check .

format:
	black .

test:
	pytest

ci: install lint format test

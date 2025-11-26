.PHONY: install test lint format build publish

install:
	pip install -e .
	pip install -r dev-requirements.txt

test:
	pytest -vv

lint:
	ruff check .

format:
	black .

build:
	python -m build

publish:
	twine upload dist/*

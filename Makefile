.PHONY: install test run

install:
	pip install -e .

test:
	pytest tests/

run:
	python -m kevin_toolbox.main

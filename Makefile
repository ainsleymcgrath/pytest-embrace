local-docs-server:
	poetry run mkdocs serve

test-latest-python:
	tox -e py310

type-check:
	tox -e mypy

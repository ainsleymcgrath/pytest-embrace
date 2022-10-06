local-docs-server:
	poetry run mkdocs serve -a localhost:9988

test-latest-python:
	tox -e py310

type-check:
	tox -e mypy

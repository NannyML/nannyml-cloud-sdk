SOURCES = nannyml_cloud_sdk
TESTS = tests

clean:
	rm -fR dist/ site/

src-build:
	poetry run flake8 $(SOURCES) $(TESTS)
	poetry run mypy $(SOURCES)
	poetry build

src-test:
	poetry run pytest

src: src-build src-test

test: src-build src-test

build: clean src-build

build-docs:
	poetry run mkdocs build --strict

serve-docs:
	poetry run mkdocs serve

publish-docs:
	poetry run mkdocs gh-deploy --strict

all: build

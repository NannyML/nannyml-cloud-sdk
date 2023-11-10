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
	poetry run mkdocs build

serve-docs:
	poetry run mkdocs serve

all: build

SOURCES = nannyml_cloud_sdk
TESTS = tests

clean:
	rm -fR dist/

src-build:
	poetry run flake8 $(SOURCES) $(TESTS)
	poetry run mypy $(SOURCES)
	poetry build

src-test:
	poetry run pytest

src: src-build src-test

test: src-build src-test

build: clean src-build

graphql-cg:
	rm -r nannyml_cloud_sdk/graphql_client
	poetry run ariadne-codegen

all: build

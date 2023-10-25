SOURCES = nannyml_cloud_sdk
TESTS = tests

lint:
	poetry run flake8 $(SOURCES) $(TESTS)
	poetry run mypy $(SOURCES)

run:
	docker-compose up -d
	open http://localhost/graphql

run-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	open http://localhost/graphql

run-db:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d db

run-python: run-db
	DB_URL=postgresql+asyncpg://nml:C43pPMZrWZha2u5i86aF@localhost poetry run python -m server


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

all: build publish

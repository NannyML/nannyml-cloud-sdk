alias b := build

old_version := `awk -F' = ' '/^version/ { gsub(/"/, "", $2); print $2 }' pyproject.toml`
new_version := `bump2version --dry-run --list patch | grep new_version | sed -r 's/^.*=//g'`

clean:
    rm -fR dist/ site/

install:
    uv sync --all-extras --dev

bump version="patch":
    uv run --frozen bump2version {{version}}
    uv lock --upgrade-package nannyml-cloud-sdk
    git add .
    git commit -m "Bump version: {{old_version}} → {{new_version}}"
    git tag v{{new_version}}

test:
    uv run pytest tests

build: clean
    uv run ruff check 
    uv build

build-docs:
	uv run mkdocs build --strict

serve-docs:
	uv run mkdocs serve

publish-docs:
	uv run mkdocs gh-deploy --strict
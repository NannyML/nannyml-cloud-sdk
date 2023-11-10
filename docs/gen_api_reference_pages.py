"""Generate the API reference pages."""

from pathlib import Path

import mkdocs_gen_files

ROOT_PATH = "nannyml_cloud_sdk"

nav = mkdocs_gen_files.Nav()


for path in sorted(Path(ROOT_PATH).rglob("*.py")):
    module_path = path.relative_to(ROOT_PATH).with_suffix("")
    doc_path = path.relative_to(ROOT_PATH).with_suffix(".md")
    full_doc_path = Path("api_reference", doc_path)

    parts = tuple(module_path.parts)

    # Skip `__init__` and ` __main__` files
    if parts[-1] in ("__init__", "__main__"):
        continue
    # Skip internal modules (starting with `_`)
    elif parts[-1].startswith("_"):
        continue

    # Add entry to navigation per file
    nav[parts] = doc_path.as_posix()

    # Add the file to mkdocs (it won't actually be written to the file system)
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print(f"::: {ROOT_PATH}.{identifier}", file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)


# Write the nav to a file
with mkdocs_gen_files.open("api_reference/summary.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())

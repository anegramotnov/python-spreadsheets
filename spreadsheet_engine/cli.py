from pathlib import Path

from spreadsheet_engine.main import root_schema


def update_schema():
    schema_path = Path("schema.graphql")

    old_schema = ""
    if schema_path.exists():
        with schema_path.open("r") as schema_file:
            old_schema = schema_file.read()

    new_schema = str(root_schema)

    if new_schema != old_schema:
        with schema_path.open("w") as schema_file:
            schema_file.write(new_schema)
        exit(1)


def print_schema():
    print(root_schema)

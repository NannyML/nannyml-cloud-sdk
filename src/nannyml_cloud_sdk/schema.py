from typing import List

from gql import gql

from ._typing import TypedDict
from .data import COLUMN_DETAILS_FRAGMENT, ColumnDetails
from .enums import ColumnType


class BaseSchema(TypedDict):
    columns: List[ColumnDetails]


def normalize(column_name: str) -> str:
    """Normalize a column name."""
    return column_name.casefold()


def _override_column_in_schema(
        column_name: str,
        column_type: ColumnType,
        schema: BaseSchema,
        is_exclusive_type: bool = True,
        overridden_type: ColumnType = 'IGNORED'
):
    """Updates the Schema given that a certain column was marked as having a certain column type."""

    column_name = normalize(column_name)
    for column in schema['columns']:
        if column['name'] == column_name:
            column['columnType'] = column_type
        elif column['columnType'] == column_type and is_exclusive_type:
            column['columnType'] = overridden_type

    return schema


INSPECT_SCHEMA = gql("""
    query inspectSchema($input: InspectDataSourceInput!) {
        inspect_dataset(input: $input) {
            columns {
                ...ColumnDetails
            }
        }
    }
""" + COLUMN_DETAILS_FRAGMENT)

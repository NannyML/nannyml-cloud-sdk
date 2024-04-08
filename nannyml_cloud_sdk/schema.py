from gql import gql

from nannyml_cloud_sdk.data import COLUMN_DETAILS_FRAGMENT


def normalize(column_name: str) -> str:
    """Normalize a column name."""
    return column_name.casefold()


INSPECT_SCHEMA = gql("""
    query inspectSchema($input: InspectDataSourceInput!) {
        inspect_dataset(input: $input) {
            columns {
                ...ColumnDetails
            }
        }
    }
""" + COLUMN_DETAILS_FRAGMENT)

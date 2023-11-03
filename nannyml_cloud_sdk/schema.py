from collections.abc import Collection
from typing import List, Optional, TypedDict, Union

from gql import gql
import pandas as pd

from .client import get_client
from .data import Data
from .enums import ColumnType, FeatureType, ProblemType

_INSPECT_SCHEMA = gql("""
    query InspectSchema($input: InspectDataSourceInput!) {
        inspect_dataset(input: $input) {
            columns {
                name
                columnType
                dataType
                className
            }
        }
    }
""")


class ModelSchemaColumn(TypedDict):
    name: str
    columnType: ColumnType
    dataType: str
    className: Optional[str]
    """Class name for prediction columns in a multiclass classification problem"""


class ModelSchema(TypedDict):
    problemType: ProblemType
    columns: List[ModelSchemaColumn]


class Schema:
    """Operations for working with machine learning model schemas"""

    INSPECT_DATA_FRAME_NR_ROWS = 100
    CATEGORICAL_DTYPES = ('object', 'str', 'category', 'bool')

    @classmethod
    def from_df(
        cls,
        problem_type: ProblemType,
        df: pd.DataFrame,
        target_column_name: Optional[str] = None,
        identifier_column_name: Optional[str] = None,
        feature_columns: dict[str, FeatureType] = {},
        ignore_column_names: Union[str, Collection[str]] = (),
    ) -> ModelSchema:
        """Create a schema from a pandas dataframe"""
        # Upload head of dataset than use API to inspect schema
        upload_id = Data.upload(df.head(cls.INSPECT_DATA_FRAME_NR_ROWS))
        schema = get_client().execute(_INSPECT_SCHEMA, variable_values={
            "input": {
                "problemType": problem_type,
                "storageInfo": {
                    "cache": {
                        "id": upload_id
                    },
                },
            },
        })['inspect_dataset']

        # Problem type isn't included in API output, so we add it here
        schema['problemType'] = problem_type

        # Apply overrides
        if target_column_name is not None:
            schema = cls.set_target(schema, target_column_name)
        if identifier_column_name is not None:
            schema = cls.set_identifier(schema, identifier_column_name)
        for column_name, feature_type in feature_columns.items():
            schema = cls.set_feature(schema, column_name, feature_type)
        schema = cls.set_ignored(schema, ignore_column_names)

        return schema

    @classmethod
    def set_target(cls, schema: ModelSchema, column_name: str) -> ModelSchema:
        """Set the target column in a schema"""
        for column in schema['columns']:
            if column['name'] == column_name:
                column['columnType'] = 'TARGET'
            elif column['columnType'] == 'TARGET':
                column['columnType'] = cls._guess_feature_type(column)

        return schema

    @classmethod
    def set_feature(cls, schema: ModelSchema, column_name: str, feature_type: FeatureType) -> ModelSchema:
        """Set a feature column in a schema"""
        for column in schema['columns']:
            if column['name'] == column_name:
                column['columnType'] = 'CATEGORICAL_FEATURE' if feature_type == 'CATEGORY' else 'CONTINUOUS_FEATURE'
                break

        return schema

    @classmethod
    def set_ignored(cls, schema: ModelSchema, column_names: Union[str, Collection[str]]) -> ModelSchema:
        """Set one or more columns to be ignored"""
        if isinstance(column_names, str):
            column_names = (column_names,)

        for column in schema['columns']:
            if column['name'] in column_names:
                column['columnType'] = 'IGNORED'

        return schema

    @classmethod
    def set_identifier(cls, schema: ModelSchema, column_name: str) -> ModelSchema:
        """Set the identifier column in a schema"""
        for column in schema['columns']:
            if column['name'] == column_name:
                column['columnType'] = 'JOIN'
            elif column['columnType'] == 'JOIN':
                column['columnType'] = cls._guess_feature_type(column)

        return schema

    @classmethod
    def _guess_feature_type(cls, column: ModelSchemaColumn) -> ColumnType:
        return (
            'CATEGORICAL_FEATURE' if column['dataType'] in cls.CATEGORICAL_DTYPES
            else 'CONTINUOUS_FEATURE'
        )

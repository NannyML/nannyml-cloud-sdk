from collections.abc import Collection
from typing import Dict, List, Literal, Optional, TypedDict, Union, cast, overload

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

    @overload
    @classmethod
    def from_df(
        cls,
        problem_type: Literal['BINARY_CLASSIFICATION', 'REGRESSION'],
        df: pd.DataFrame,
        target_column_name: Optional[str] = ...,
        timestamp_column_name: Optional[str] = ...,
        prediction_column_name: Optional[str] = ...,
        prediction_score_column_name_or_mapping: Optional[str] = ...,
        identifier_column_name: Optional[str] = ...,
        feature_columns: Dict[str, FeatureType] = ...,
        ignore_column_names: Union[str, Collection[str]] = ...,
    ) -> ModelSchema:
        pass

    @overload
    @classmethod
    def from_df(
        cls,
        problem_type: Literal['MULTICLASS_CLASSIFICATION'],
        df: pd.DataFrame,
        target_column_name: Optional[str] = ...,
        timestamp_column_name: Optional[str] = ...,
        prediction_column_name: Optional[str] = ...,
        prediction_score_column_name_or_mapping: Dict[str, str] = ...,
        identifier_column_name: Optional[str] = ...,
        feature_columns: Dict[str, FeatureType] = ...,
        ignore_column_names: Union[str, Collection[str]] = ...,
    ) -> ModelSchema:
        pass

    @classmethod
    def from_df(
        cls,
        problem_type,
        df,
        target_column_name=None,
        timestamp_column_name=None,
        prediction_column_name=None,
        prediction_score_column_name_or_mapping=None,
        identifier_column_name=None,
        feature_columns={},
        ignore_column_names=(),
    ) -> ModelSchema:
        """Create a schema from a pandas dataframe"""
        # Upload head of dataset than use API to inspect schema
        upload = Data.upload(df.head(cls.INSPECT_DATA_FRAME_NR_ROWS))
        schema = get_client().execute(_INSPECT_SCHEMA, variable_values={
            "input": {
                "problemType": problem_type,
                "storageInfo": upload,
            },
        })['inspect_dataset']

        # Problem type isn't included in API output, so we add it here
        schema['problemType'] = problem_type

        # Apply overrides
        if target_column_name is not None:
            schema = cls.set_target(schema, target_column_name)
        if timestamp_column_name is not None:
            schema = cls.set_timestamp(schema, timestamp_column_name)
        if prediction_column_name is not None:
            schema = cls.set_prediction(schema, prediction_column_name)
        if prediction_score_column_name_or_mapping is not None:
            schema = cls.set_prediction_score(schema, prediction_score_column_name_or_mapping)
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
    def set_timestamp(cls, schema: ModelSchema, column_name: str) -> ModelSchema:
        """Set the timestamp column in a schema"""
        for column in schema['columns']:
            if column['name'] == column_name:
                column['columnType'] = 'TIMESTAMP'
            elif column['columnType'] == 'TIMESTAMP':
                column['columnType'] = cls._guess_feature_type(column)

        return schema

    @classmethod
    def set_prediction(cls, schema: ModelSchema, column_name: str) -> ModelSchema:
        """Set the prediction column in a schema"""
        for column in schema['columns']:
            if column['name'] == column_name:
                column['columnType'] = 'PREDICTION'
            elif column['columnType'] == 'PREDICTION':
                column['columnType'] = cls._guess_feature_type(column)

        return schema

    @classmethod
    def set_prediction_score(
        cls, schema: ModelSchema, column_name_or_mapping: Union[str, Dict[str, str]]
    ) -> ModelSchema:
        """Set the prediction score column(s) in a schema

        Binary classification and regression problems require a single prediction score column.
        Multiclass classification problems require a dictionary mapping prediction score columns to class names.
        """
        if isinstance(column_name_or_mapping, str):
            if schema['problemType'] == 'MULTICLASS_CLASSIFICATION':
                raise ValueError('Must specify a dictionary of prediction score columns for multiclass classification')
            column_name_or_mapping = {column_name_or_mapping: cast(str, None)}
        elif schema['problemType'] != 'MULTICLASS_CLASSIFICATION':
            raise ValueError(
                'Must specify a single prediction score column name for binary classification and regression'
            )

        for column in schema['columns']:
            if column['name'] in column_name_or_mapping:
                column['columnType'] = 'PREDICTION_SCORE'
                column['className'] = column_name_or_mapping[column['name']]
            elif column['columnType'] == 'PREDICTION_SCORE':
                column['columnType'] = cls._guess_feature_type(column)
                column['className'] = None

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
                column['columnType'] = 'IDENTIFIER'
            elif column['columnType'] == 'IDENTIFIER':
                column['columnType'] = cls._guess_feature_type(column)

        return schema

    @classmethod
    def _guess_feature_type(cls, column: ModelSchemaColumn) -> ColumnType:
        return (
            'CATEGORICAL_FEATURE' if column['dataType'] in cls.CATEGORICAL_DTYPES
            else 'CONTINUOUS_FEATURE'
        )

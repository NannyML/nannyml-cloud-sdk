from collections.abc import Collection
from typing import Dict, List, Literal, Optional, TypedDict, Union, cast, overload

from gql import gql
import pandas as pd

from .client import execute
from .data import COLUMN_DETAILS_FRAGMENT, ColumnDetails, Data
from .enums import ColumnType, FeatureType, ProblemType


def normalize(column_name: str) -> str:
    """Normalize a column name."""
    return column_name.casefold()


class ModelSchema(TypedDict):
    """Schema for a machine learning model."""
    problemType: ProblemType
    columns: List[ColumnDetails]


_INSPECT_SCHEMA = gql("""
    query inspectSchema($input: InspectDataSourceInput!) {
        inspect_dataset(input: $input) {
            columns {
                ...ColumnDetails
            }
        }
    }
""" + COLUMN_DETAILS_FRAGMENT)


class Schema:
    """Operations for working with machine learning model schemas."""

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
        """First"""
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
        """Create a schema from a pandas dataframe.

        Sends a sample of the dataframe to the NannyML Cloud API to inspect the schema. Heuristics are used to identify
        what each column represents. The schema is then modified according to the provided arguments.
        """
        pass

    @classmethod
    def from_df(
        cls,
        problem_type: ProblemType,
        df: pd.DataFrame,
        target_column_name: Optional[str] = None,
        timestamp_column_name: Optional[str] = None,
        prediction_column_name: Optional[str] = None,
        prediction_score_column_name_or_mapping: Optional[Union[str, Dict[str, str]]] = None,
        identifier_column_name: Optional[str] = None,
        feature_columns: Dict[str, FeatureType] = {},
        ignore_column_names: Union[str, Collection[str]] = (),
    ) -> ModelSchema:
        """Create a schema from a pandas dataframe.

        Sends a sample of the dataframe to the NannyML Cloud API to inspect the schema. Heuristics are used to identify
        what each column represents. The schema is then modified according to the provided arguments.

        Args:
            problem_type: The problem type of the model.
            df: The pandas dataframe to create a schema from.
            target_column_name: The name of the target column. Any column that heuristics identified as target will be
                changed to a feature column.
            timestamp_column_name: The name of the timestamp column. Any column that heuristics identified as timestamp
                will be changed to a feature column.
            prediction_column_name: The name of the prediction column. Any column that heuristics identified as
                prediction will be changed to a feature column.
            prediction_score_column_name_or_mapping: This parameter accepts two formats depending on problem type.

                - For binary classification and regression, this should be the name of the prediction score column.
                - For multiclass classification, it should be a dict mapping prediction score column names to class
                  names, e.g. `{'prediction_score_1': 'class_1', 'prediction_score_2': 'class_2'}`.

            identifier_column_name: The name of the identifier column. Any column that heuristics identified as
                identifier will be changed to a feature column.
            feature_columns: A dictionary specifying whether features are `CATEGORICAL` or `CONTINUOUS`. Feature columns
                that are not specified will retain their original [type][nannyml_cloud_sdk.enums.FeatureType].
            ignore_column_names: The names of columns to ignore.

        Returns:
            The inspected schema with any modifications applied.
        """
        # Upload head of dataset than use API to inspect schema
        upload = Data.upload(df.head(cls.INSPECT_DATA_FRAME_NR_ROWS))
        schema = execute(_INSPECT_SCHEMA, variable_values={
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
        """Set the target column in a schema.

        Args:
            schema: The schema to modify.
            column_name: The name of the target column. Any column that was previously set as target will be changed to
                a feature column.

        Returns:
            The modified schema.
        """
        column_name = normalize(column_name)
        for column in schema['columns']:
            if column['name'] == column_name:
                column['columnType'] = 'TARGET'
            elif column['columnType'] == 'TARGET':
                column['columnType'] = cls._guess_feature_type(column)

        return schema

    @classmethod
    def set_timestamp(cls, schema: ModelSchema, column_name: str) -> ModelSchema:
        """Set the timestamp column in a schema.

        Note:
            The timestamp column will be coerced to a datetime data type.

        Args:
            schema: The schema to modify.
            column_name: The name of the timestamp column. Any column that was previously set as timestamp will be
                changed to a feature column.

        Returns:
            The modified schema.
        """
        column_name = normalize(column_name)
        for column in schema['columns']:
            if column['name'] == column_name:
                column['columnType'] = 'TIMESTAMP'

                # Set appropriate datetime data type if not already set
                if 'datetime' not in column['dataType']:
                    column['dataType'] = 'datetime64[ns]'
            elif column['columnType'] == 'TIMESTAMP':
                column['columnType'] = cls._guess_feature_type(column)

        return schema

    @classmethod
    def set_prediction(cls, schema: ModelSchema, column_name: str) -> ModelSchema:
        """Set the prediction column in a schema.

        Args:
            schema: The schema to modify.
            column_name: The name of the prediction column. Any column that was previously set as prediction will be
                changed to a feature column.

        Returns:
            The modified schema.
        """
        column_name = normalize(column_name)
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
        """Set the prediction score column(s) in a schema.

        Binary classification and regression problems require a single prediction score column.
        Multiclass classification problems require a dictionary mapping prediction score columns to class names, e.g.
        `{'prediction_score_1': 'class_1', 'prediction_score_2': 'class_2'}`.

        Args:
            schema: The schema to modify.
            column_name_or_mapping: The name of the prediction score column or a dictionary mapping prediction score
                column names to class names. Any existing prediction score columns will be changed to feature columns.

        Returns:
            The modified schema.
        """
        if isinstance(column_name_or_mapping, str):
            if schema['problemType'] == 'MULTICLASS_CLASSIFICATION':
                raise ValueError('Must specify a dictionary of prediction score columns for multiclass classification')
            column_name_or_mapping = {normalize(column_name_or_mapping): cast(str, None)}
        elif schema['problemType'] != 'MULTICLASS_CLASSIFICATION':
            raise ValueError(
                'Must specify a single prediction score column name for binary classification and regression'
            )
        else:
            column_name_or_mapping = {normalize(key): value for (key, value) in column_name_or_mapping.items()}

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
        """Set a feature column in a schema.

        Args:
            schema: The schema to modify.
            column_name: The name of the feature column.
            feature_type: Whether the feature is `CATEGORICAL` or `CONTINUOUS`.

        Returns:
            The modified schema.
        """
        column_name = normalize(column_name)
        for column in schema['columns']:
            if column['name'] == column_name:
                column['columnType'] = 'CATEGORICAL_FEATURE' if feature_type == 'CATEGORY' else 'CONTINUOUS_FEATURE'
                break

        return schema

    @classmethod
    def set_ignored(cls, schema: ModelSchema, column_names: Union[str, Collection[str]]) -> ModelSchema:
        """Set one or more columns to be ignored.

        Args:
            schema: The schema to modify.
            column_names: The name of the column or columns to ignore.

        Returns:
            The modified schema.
        """
        if isinstance(column_names, str):
            column_names = (column_names,)
        column_names = {normalize(column_name) for column_name in column_names}

        for column in schema['columns']:
            if column['name'] in column_names:
                column['columnType'] = 'IGNORED'

        return schema

    @classmethod
    def set_identifier(cls, schema: ModelSchema, column_name: str) -> ModelSchema:
        """Set the identifier column in a schema.

        Args:
            schema: The schema to modify.
            column_name: The name of the identifier column. Any column that was previously set as identifier will be
                changed to a feature column.

        Returns:
            The modified schema.
        """
        column_name = normalize(column_name)
        for column in schema['columns']:
            if column['name'] == column_name:
                column['columnType'] = 'IDENTIFIER'
            elif column['columnType'] == 'IDENTIFIER':
                column['columnType'] = cls._guess_feature_type(column)

        return schema

    @classmethod
    def _guess_feature_type(cls, column: ColumnDetails) -> ColumnType:
        """Guess feature type from column details."""
        return (
            'CATEGORICAL_FEATURE' if column['dataType'] in cls.CATEGORICAL_DTYPES
            else 'CONTINUOUS_FEATURE'
        )

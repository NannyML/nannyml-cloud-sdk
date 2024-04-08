from typing import Optional, Dict, Union, Collection, cast

import pandas as pd

from ..client import execute
from ..data import Data
from ..enums import ProblemType
from ..schema import INSPECT_SCHEMA, normalize, BaseSchema, _override_column_in_schema


class ModelSchema(BaseSchema):
    """Schema for a machine learning model."""
    problemType: ProblemType


class Schema:
    """Operations for working with machine learning model schemas."""

    INSPECT_DATA_FRAME_NR_ROWS = 100
    CATEGORICAL_DTYPES = ('object', 'str', 'category', 'bool')

    @classmethod
    def from_df(
        cls,
        problem_type: ProblemType,
        df: pd.DataFrame,
        target_column_name: Optional[str] = None,
        prediction_score_column_name_or_mapping: Optional[Union[str, Dict[str, str]]] = None,
        identifier_column_name: Optional[str] = None,
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
            prediction_score_column_name_or_mapping: This parameter accepts two formats depending on problem type.

                - For binary classification and regression, this should be the name of the prediction score column.
                - For multiclass classification, it should be a dict mapping prediction score column names to class
                  names, e.g. `{'prediction_score_1': 'class_1', 'prediction_score_2': 'class_2'}`.

            identifier_column_name: The name of the identifier column. Any column that heuristics identified as
                identifier will be changed to a feature column.
            ignore_column_names: The names of columns to ignore.

        Returns:
            The inspected schema with any modifications applied.
        """
        if problem_type in ('MULTICLASS_CLASSIFICATION', 'REGRESSION'):
            raise NotImplementedError(f"problem_type '{problem_type}' is not supported yet.")

        # Upload head of dataset than use API to inspect schema
        upload = Data.upload(df.head(cls.INSPECT_DATA_FRAME_NR_ROWS))
        schema = execute(INSPECT_SCHEMA, variable_values={
            "input": {
                "productType": 'EVALUATION',
                "problemType": problem_type,
                "storageInfo": upload,
            },
        })['inspect_dataset']

        # Problem type isn't included in API output, so we add it here
        schema['problemType'] = problem_type

        # Apply overrides
        if target_column_name is not None:
            schema = cls.set_target(schema, target_column_name)
        if prediction_score_column_name_or_mapping is not None:
            schema = cls.set_prediction_score(schema, prediction_score_column_name_or_mapping)
        if identifier_column_name is not None:
            schema = cls.set_identifier(schema, identifier_column_name)
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

        return _override_column_in_schema(column_name, 'TARGET', schema)

    @classmethod
    def set_prediction_score(
        cls, schema: ModelSchema, column_name_or_mapping: Union[str, Dict[str, str]]
    ) -> ModelSchema:
        """Set the prediction score column(s) in a schema.

        Binary classification and regression problems require a single prediction score column.
        Multiclass classification problems require a dictionary mapping class names to prediction score columns, e.g.
        `{'class_1': 'prediction_score_1', 'class_2': 'prediction_score_2'}`.

        Args:
            schema: The schema to modify.
            column_name_or_mapping: The name of the prediction score column or a dictionary mapping class names to
                prediction score column names. Any existing prediction score columns will be changed to feature columns.

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
            column_name_or_mapping = {
                normalize(column_name): class_name for (class_name, column_name) in column_name_or_mapping.items()
            }

        for column in schema['columns']:
            if column['name'] in column_name_or_mapping:
                column['columnType'] = 'PREDICTION_SCORE'
                column['className'] = column_name_or_mapping[column['name']]
            elif column['columnType'] == 'PREDICTION_SCORE':
                column['columnType'] = 'IGNORED'
                column['className'] = None

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
        return _override_column_in_schema(column_name, 'IDENTIFIER', schema)

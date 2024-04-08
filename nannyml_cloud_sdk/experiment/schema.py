from typing import Optional, Union, Collection

import pandas as pd

from ..client import execute
from ..data import ColumnDetails, Data
from ..enums import ColumnType
from ..schema import INSPECT_SCHEMA, normalize, BaseSchema, _override_column_in_schema


class ExperimentSchema(BaseSchema):
    """Schema for a machine learning experiment."""


class Schema:
    """Operations for working with machine learning experiment schemas."""

    INSPECT_DATA_FRAME_NR_ROWS = 100
    CATEGORICAL_DTYPES = ('object', 'str', 'category', 'bool')

    @classmethod
    def from_df(
        cls,
        df: pd.DataFrame,
        metric_column_name: Optional[str] = None,
        group_column_name: Optional[str] = None,
        success_count_column_name: Optional[str] = None,
        fail_count_column_name: Optional[str] = None,
        identifier_column_name: Optional[str] = None,
        ignore_column_names: Union[str, Collection[str]] = (),
    ) -> ExperimentSchema:
        """Create a schema from a pandas dataframe.

        Sends a sample of the dataframe to the NannyML Cloud API to inspect the schema. Heuristics are used to identify
        what each column represents. The schema is then modified according to the provided arguments.

        Args:
            df: The pandas dataframe to create a schema from.
            metric_column_name: The name of the column containing the metric names.
            group_column_name: The name of the column containing the group names for each group.
            success_count_column_name: The name of the column containing the success count for a metric and group.
            fail_count_column_name: The name of the column containing the fail count for a metric and group.
            identifier_column_name: The name of the identifier column. Any column that heuristics identified as
                identifier will be changed to a feature column.
            ignore_column_names: The names of columns to ignore.

        Returns:
            The inspected schema with any modifications applied.
        """
        # Upload head of dataset than use API to inspect schema
        upload = Data.upload(df.head(cls.INSPECT_DATA_FRAME_NR_ROWS))
        schema = execute(INSPECT_SCHEMA, variable_values={
            "input": {
                "productType": 'EXPERIMENT',
                "storageInfo": upload,
            },
        })['inspect_dataset']

        # Apply overrides

        if metric_column_name is not None:
            schema = cls.set_metric_name(schema, metric_column_name)
        if group_column_name is not None:
            schema = cls.set_group_name(schema, group_column_name)
        if success_count_column_name is not None:
            schema = cls.set_success_count(schema, success_count_column_name)
        if fail_count_column_name is not None:
            schema = cls.set_fail_count(schema, fail_count_column_name)
        if identifier_column_name is not None:
            schema = cls.set_identifier(schema, identifier_column_name)
        schema = cls.set_ignored(schema, ignore_column_names)

        return schema

    @classmethod
    def set_metric_name(cls, schema: ExperimentSchema, column_name: str) -> ExperimentSchema:
        """Set the metric name column in a schema.

        Args:
            schema: The schema to modify.
            column_name: The name of the metric name column. Any column that was previously set as the metric column
                will be changed to an ignored column.
        """
        return _override_column_in_schema(column_name, 'METRIC_NAME', schema)

    @classmethod
    def set_group_name(cls, schema: ExperimentSchema, column_name: str) -> ExperimentSchema:
        """Set the group name column in a schema.

        Args:
            schema: The schema to modify.
            column_name: The name of the group name column. Any column that was previously set as the metric column
                will be changed to an ignored column.
        """
        return _override_column_in_schema(column_name, 'GROUP_NAME', schema)

    @classmethod
    def set_success_count(cls, schema: ExperimentSchema, column_name: str) -> ExperimentSchema:
        """Set the success count column in a schema.

        Args:
            schema: The schema to modify.
            column_name: The name of the success column. Any column that was previously set as the metric column
                will be changed to an ignored column.
        """
        return _override_column_in_schema(column_name, 'SUCCESS_COUNT', schema)

    @classmethod
    def set_fail_count(cls, schema: ExperimentSchema, column_name: str) -> ExperimentSchema:
        """Set the fail count column in a schema.

        Args:
            schema: The schema to modify.
            column_name: The name of the fail count column. Any column that was previously set as the metric column
                will be changed to an ignored column.
        """
        return _override_column_in_schema(column_name, 'FAIL_COUNT', schema)

    @classmethod
    def set_ignored(cls, schema: ExperimentSchema, column_names: Union[str, Collection[str]]) -> ExperimentSchema:
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
    def set_identifier(cls, schema: ExperimentSchema, column_name: str) -> ExperimentSchema:
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
        return 'IGNORED'

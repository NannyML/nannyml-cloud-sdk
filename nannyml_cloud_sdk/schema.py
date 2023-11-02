from collections.abc import Collection
from typing import Literal, Optional, Union
import io

import pandas as pd

from .client import get_client
from .graphql_client import (
    CacheStorageInput, ColumnType, InspectDataSourceInput, InspectSchemaInspectDatasetColumns, ProblemType,
    StorageInput, Upload
)


class Schema:
    """Represents the schema of a machine learning model"""

    INSPECT_DATA_FRAME_NR_ROWS = 100
    CATEGORICAL_DTYPES = ('object', 'str', 'category', 'bool')

    def __init__(self, problem_type: ProblemType, columns: Collection[InspectSchemaInspectDatasetColumns]):
        self._problem_type = problem_type
        self._columns = columns

    def __repr__(self) -> str:
        return "\n".join((
            f"<Schema for {self._problem_type.name} problem:",
            *(f"  {column.name}: {column.column_type.name}" for column in self._columns),
            ">",
        ))

    @classmethod
    def from_df(
        cls,
        problem_type: ProblemType,
        df: pd.DataFrame,
        target_column_name: Optional[str] = None,
        identifier_column_name: Optional[str] = None,
        feature_columns: dict[str, Literal['CONTINUOUS', 'CATEGORY']] = {},
        ignore_column_names: Union[str, Collection[str]] = (),
    ) -> 'Schema':
        """Create a schema from a pandas dataframe and apply overrides"""
        upload_id = cls._upload_data_frame(df.head(cls.INSPECT_DATA_FRAME_NR_ROWS))
        inspect_data = get_client().inspect_schema(InspectDataSourceInput(
            problemType=problem_type,
            storageInfo=StorageInput(cache=CacheStorageInput(id=upload_id))
        ))

        schema = Schema(problem_type, inspect_data.inspect_dataset.columns)
        if target_column_name is not None:
            schema.set_target(target_column_name)
        if identifier_column_name is not None:
            schema.set_identifier(identifier_column_name)
        for column_name, feature_type in feature_columns.items():
            schema.set_feature(column_name, feature_type)
        schema.set_ignored(ignore_column_names)
        return schema

    def set_target(self, column_name: str):
        """Set the target column"""
        for column in self._columns:
            if column.name == column_name:
                column.column_type = ColumnType.TARGET
            elif column.column_type is ColumnType.TARGET:
                column.column_type = self._guess_feature_type(column)

    def set_feature(self, column_name: str, feature_type: Literal['CONTINUOUS', 'CATEGORY']):
        """Set a feature column"""
        for column in self._columns:
            if column.name == column_name:
                column.column_type = \
                    ColumnType.CATEGORICAL_FEATURE if feature_type == 'CATEGORY' else ColumnType.CONTINUOUS_FEATURE
                break

    def set_ignored(self, column_names: Union[str, Collection[str]]):
        """Set one or more columns to be ignored"""
        if isinstance(column_names, str):
            column_names = (column_names,)

        for column in self._columns:
            if column.name in column_names:
                column.column_type = ColumnType.IGNORED

    def set_identifier(self, column_name: str):
        """Set the identifier column"""
        for column in self._columns:
            if column.name == column_name:
                column.column_type = ColumnType.JOIN
            elif column.column_type is ColumnType.JOIN:
                column.column_type = self._guess_feature_type(column)

    @classmethod
    def _guess_feature_type(cls, column: InspectSchemaInspectDatasetColumns) -> ColumnType:
        """Helper method to guess feature type for a column"""
        return (
            ColumnType.CATEGORICAL_FEATURE if column.data_type in cls.CATEGORICAL_DTYPES
            else ColumnType.CONTINUOUS_FEATURE
        )

    @classmethod
    def _upload_data_frame(cls, df: pd.DataFrame) -> str:
        """Upload a dataset and return the ID"""
        with io.BytesIO() as buffer:
            df.to_parquet(buffer)
            buffer.seek(0)
            return get_client().upload_dataset(Upload(
                'data.parquet', buffer, 'application/vnd.apache.parquet'
            )).upload_dataset.id

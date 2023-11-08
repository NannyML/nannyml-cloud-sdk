import datetime
import functools
from typing import Collection, Container, Iterable, List, Optional

import pandas as pd
from frozendict import frozendict
from gql import gql

from .client import execute
from .data import Data
from .enums import ChunkPeriod, PerformanceMetric, ProblemType
from .errors import InvalidOperationError
from .run import RUN_SUMMARY_FRAGMENT, RunSummary
from .schema import COLUMN_DETAILS_FRAGMENT, ColumnDetails, ModelSchema
from ._typing import TypedDict


class ModelSummary(TypedDict):
    id: str
    name: str
    problemType: ProblemType
    createdAt: datetime.datetime


class ModelDetails(ModelSummary):
    latestRun: Optional[RunSummary]
    nextRun: Optional[RunSummary]


class DataSourceSummary(TypedDict):
    id: str
    name: str
    hasReferenceData: bool
    hasAnalysisData: bool
    nrRows: int


class DataSourceDetails(DataSourceSummary):
    columns: list[ColumnDetails]


class DataSourceFilter(TypedDict, total=False):
    name: str
    hasReferenceData: bool
    hasAnalysisData: bool


_MODEL_SUMMARY_FRAGMENT = f"""
    fragment ModelSummary on Model {{
        {' '.join(ModelSummary.__required_keys__)}
    }}
"""

_MODEL_DETAILS_FRAGMENT = """
    fragment ModelDetails on Model {
        ...ModelSummary
        latestRun {
            ...RunSummary
        }
        nextRun {
            ...RunSummary
        }
    }
""" + _MODEL_SUMMARY_FRAGMENT + RUN_SUMMARY_FRAGMENT

_LIST_MODELS = gql("""
    query listModels($filter: ModelsFilter) {
        models(filter: $filter) {
            ...ModelSummary
        }
    }
""" + _MODEL_SUMMARY_FRAGMENT)

_READ_MODEL = gql("""
    query readModel($id: Int!) {
        model(id: $id) {
            ...ModelDetails
        }
    }
""" + _MODEL_DETAILS_FRAGMENT)

_DATA_SOURCE_SUMMARY_FRAGMENT = f"""
    fragment DataSourceSummary on DataSource {{
        {' '.join(DataSourceSummary.__required_keys__)}
    }}
"""

_GET_MODEL_DATA_SOURCES = gql("""
    query getModelDataSources($modelId: Int!, $filter: DataSourcesFilter) {
        model(id: $modelId) {
            dataSources(filter: $filter) {
                ...DataSourceSummary
                columns {
                    ...ColumnDetails
                }
            }
        }
    }
""" + _DATA_SOURCE_SUMMARY_FRAGMENT + COLUMN_DETAILS_FRAGMENT)

_CREATE_MODEL = gql("""
    mutation createModel($input: CreateModelInput!) {
        create_model(model: $input) {
            ...ModelDetails
        }
    }
""" + _MODEL_DETAILS_FRAGMENT)

_DELETE_MODEL = gql("""
    mutation deleteModel($id: Int!) {
        delete_model(modelId: $id) {
            id
        }
    }
""")

_ADD_DATA_TO_DATA_SOURCE = gql("""
    mutation addDataToDataSource($input: DataSourceDataInput!) {
        add_data_to_data_source(input: $input) {
            id
        }
    }
""")

_UPDATE_DATA_IN_DATA_SOURCE = gql("""
    mutation updateDataInDataSource($input: DataSourceDataInput!) {
        update_data_in_data_source(input: $input) {
            id
        }
    }
""")


class Model:
    """Operations for working with machine learning models"""

    @classmethod
    def list(cls, name: Optional[str] = None, problem_type: Optional[ProblemType] = None) -> List[ModelSummary]:
        """List defined models"""
        return execute(_LIST_MODELS, {
            'filter': {
                'name': name,
                'problemType': problem_type,
            }
        })['models']

    @classmethod
    def get(cls, model_id: str) -> ModelDetails:
        """Get details for a model"""
        return execute(_READ_MODEL, {'id': int(model_id)})['model']

    @classmethod
    def create(
        cls,
        schema: ModelSchema,
        chunk_period: ChunkPeriod,
        reference_data: pd.DataFrame,
        analysis_data: pd.DataFrame,
        target_data: Optional[pd.DataFrame] = None,
        name: Optional[str] = None,
        main_performance_metric: Optional[PerformanceMetric] = None,
    ) -> ModelDetails:
        """Create a new model"""
        data_sources = [
            {
                'name': 'reference',
                'hasReferenceData': True,
                'hasAnalysisData': False,
                'columns': schema['columns'],
                'storageInfo': Data.upload(reference_data),
            },
            {
                'name': 'analysis',
                'hasReferenceData': False,
                'hasAnalysisData': True,
                'columns': cls.__select_schema_subset(schema['columns'], analysis_data.columns),
                'storageInfo': Data.upload(analysis_data),
            },
        ]
        if target_data is not None:
            data_sources.append({
                'name': 'target',
                'hasReferenceData': False,
                'hasAnalysisData': True,
                'columns': cls.__select_schema_subset(schema['columns'], target_data.columns),
                'storageInfo': Data.upload(target_data),
            })

        return execute(_CREATE_MODEL, {
            'input': {
                'name': name,
                'problemType': schema['problemType'],
                'chunkAggregation': chunk_period,
                'dataSources': data_sources,
                'mainPerformanceMetric': main_performance_metric,
            },
        })['create_model']

    @classmethod
    def delete(cls, model_id: str):
        """Delete a model"""
        return execute(_DELETE_MODEL, {'id': int(model_id)})

    @classmethod
    def add_analysis_data(cls, model_id: str, data: pd.DataFrame) -> None:
        """Add analysis data to a model

        .. note::
            This method does not update existing data. It only adds new data. If you want to update existing data,
            use :meth:`update_analysis_data` instead.
        """
        data_sources = cls.__get_model_data_sources(model_id, frozendict({'name': 'analysis'}))
        upload_dict = cls.__allocate_data_to_data_sources(data_sources, data)
        for data_source_id, column_names in upload_dict.items():
            execute(_ADD_DATA_TO_DATA_SOURCE, {
                'input': {
                    'id': int(data_source_id),
                    'storageInfo': Data.upload(data[column_names]),
                },
            })

    @classmethod
    def add_analysis_target_data(cls, model_id: str, data: pd.DataFrame) -> None:
        """Add (delayed) target data to a model

        .. note::
            This method can only be used if the model has a target data source. If you want to add analysis data to a
            model without a target data source, use :meth:`add_analysis_data` instead.

        .. note::
            This method does not update existing data. It only adds new data. If you want to update existing data,
            use :meth:`update_analysis_target_data` instead.
        """
        data_sources = cls.__get_model_data_sources(model_id, frozendict({'name': 'target'}))
        if not data_sources:
            raise InvalidOperationError(
                f"Model '{model_id}' has no target data source. If targets are present, they are stored in the "
                "analysis data source. Use `add_analysis_data` instead."
            )

        upload_dict = cls.__allocate_data_to_data_sources(data_sources, data)
        for data_source_id, column_names in upload_dict.items():
            execute(_ADD_DATA_TO_DATA_SOURCE, {
                'input': {
                    'id': int(data_source_id),
                    'storageInfo': Data.upload(data[column_names]),
                },
            })

    @classmethod
    def update_analysis_data(cls, model_id: str, data: pd.DataFrame) -> None:
        """Add or update analysis data for a model

        .. note::
            This method compares existing data with the new data to determine which rows to update and which to add.
            If you are certain you are only adding new data, it is recommended to use :meth:`add_analysis_data` instead
            for better performance.
        """
        data_sources = cls.__get_model_data_sources(model_id, frozendict({'name': 'analysis'}))
        upload_dict = cls.__allocate_data_to_data_sources(data_sources, data)
        for data_source_id, column_names in upload_dict.items():
            execute(_UPDATE_DATA_IN_DATA_SOURCE, {
                'input': {
                    'id': int(data_source_id),
                    'storageInfo': Data.upload(data[column_names]),
                },
            })

    @classmethod
    def update_analysis_target_data(cls, model_id: str, data: pd.DataFrame) -> None:
        """Add or update (delayed) target data to a model

        .. note::
            This method can only be used if the model has a target data source. If you want to update analysis data in a
            model without a target data source, use :meth:`update_analysis_data` instead.

        .. note::
            This method compares existing data with the new data to determine which rows to update and which to add.
            If you are certain you are only adding new data, it is recommended to use :meth:`add_analysis_target_data`
            instead for better performance.
        """
        data_sources = cls.__get_model_data_sources(model_id, frozendict({'name': 'target'}))
        if not data_sources:
            raise InvalidOperationError(
                f"Model '{model_id}' has no target data source. If targets are present, they are stored in the "
                "analysis data source. Use `update_analysis_data` instead."
            )

        upload_dict = cls.__allocate_data_to_data_sources(data_sources, data)
        for data_source_id, column_names in upload_dict.items():
            execute(_UPDATE_DATA_IN_DATA_SOURCE, {
                'input': {
                    'id': int(data_source_id),
                    'storageInfo': Data.upload(data[column_names]),
                },
            })

    @classmethod
    def __allocate_data_to_data_sources(
        cls, data_sources: Collection[DataSourceDetails], data: pd.DataFrame,
    ) -> dict[str, List[str]]:
        """Allocate data columns to model data sources based on schema

        A model supports multiple data sources, e.g. analysis and targets. This method allocates columns in the data
        to the data sources based on the schema. If there is a mismatch, i.e. columns for which there is no schema
        defined, we generate an error.

        Returns:
            A dictionary mapping data source IDs to column names

        Raises:
            ValueError: If there is a mismatch between the schema and the columns present in the data
        """
        remaining_columns, upload_dict = set(data.columns), {}
        for data_source in data_sources:
            # Find columns in the data source that are also in the data
            columns = cls.__select_schema_subset(data_source['columns'], data.columns)
            if all(col['columnType'] in ('IDENTIFIER', 'TIMESTAMP') for col in columns):
                # Identifier and timestamp columns are shared across data sources. If there's no other columns, we can
                # skip this data source.
                continue

            # Store column information per data source for upload
            column_names = [column['name'] for column in columns]
            upload_dict[data_source['id']] = column_names

            # Remove uploaded columns from the list of columns to process
            remaining_columns.difference_update(column_names)
            if not remaining_columns:
                return upload_dict
        else:
            raise InvalidOperationError(
                f"Data source(s) {', '.join(repr(ds['name']) for ds in data_sources)} has no schema defined for "
                f"columns: {remaining_columns}."
            )

    @functools.lru_cache(maxsize=128)
    @staticmethod
    def __get_model_data_sources(model_id: str, filter: Optional[DataSourceFilter] = None) -> List[DataSourceDetails]:
        """Get data sources for a model"""
        # There is a bug in gql that prevents correctly parsing results. Working around it here by disabling result
        # parsing. There are no custom scalars in the response payload, so this is safe (for now).
        return execute(_GET_MODEL_DATA_SOURCES, {
            'modelId': int(model_id),
            'filter': filter,
        }, parse_result=False)['model']['dataSources']

    @staticmethod
    def __select_schema_subset(
        columns: Iterable[ColumnDetails], column_names: Container[str]
    ) -> List[ColumnDetails]:
        return [column for column in columns if column['name'] in column_names]

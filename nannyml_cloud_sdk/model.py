import datetime
import functools
from typing import Container, Iterable, List, Optional

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
        analysis_data_source, = cls.__get_model_data_sources(model_id, frozendict({'name': 'analysis'}))
        execute(_ADD_DATA_TO_DATA_SOURCE, {
            'input': {
                'id': int(analysis_data_source['id']),
                'storageInfo': Data.upload(data),
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
        try:
            target_data_source = data_sources[0]
        except IndexError:
            raise InvalidOperationError(
                f"Model '{model_id}' has no target data source. If targets are present, they are stored in the "
                "analysis data source. Use `add_analysis_data` instead."
            )

        execute(_ADD_DATA_TO_DATA_SOURCE, {
            'input': {
                'id': int(target_data_source['id']),
                'storageInfo': Data.upload(data),
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
        analysis_data_source, = cls.__get_model_data_sources(model_id, frozendict({'name': 'analysis'}))
        execute(_UPDATE_DATA_IN_DATA_SOURCE, {
            'input': {
                'id': int(analysis_data_source['id']),
                'storageInfo': Data.upload(data),
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
        try:
            target_data_source = data_sources[0]
        except IndexError:
            raise InvalidOperationError(
                f"Model '{model_id}' has no target data source. If targets are present, they are stored in the "
                "analysis data source. Use `update_analysis_data` instead."
            )

        execute(_UPDATE_DATA_IN_DATA_SOURCE, {
            'input': {
                'id': int(target_data_source['id']),
                'storageInfo': Data.upload(data),
            },
        })

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

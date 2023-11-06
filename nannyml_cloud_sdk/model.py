import datetime
from typing import Container, Iterable, List, Optional, TypedDict

import pandas as pd
from gql import gql

from .client import get_client
from .data import Data
from .enums import ChunkPeriod, PerformanceMetric, ProblemType
from .schema import ModelSchema, ModelSchemaColumn

_LIST_QUERY = gql("""
    query listModels($filter: ModelsFilter) {
        models(filter: $filter) {
            id
            name
            problemType
            createdAt
        }
    }
""")

_CREATE_MODEL = gql("""
    mutation createModel($input: CreateModelInput!) {
        create_model(model: $input) {
            id
        }
    }
""")

_DELETE_MODEL = gql("""
    mutation deleteModel($id: Int!) {
        delete_model(modelId: $id) {
            id
        }
    }
""")


class ModelSummary(TypedDict):
    id: str
    name: str
    problemType: ProblemType
    createdAt: datetime.datetime


class Model:
    """Operations for working with machine learning models"""

    @classmethod
    def list(cls, name: Optional[str] = None, problem_type: Optional[ProblemType] = None) -> List[ModelSummary]:
        """List defined models"""
        return get_client().execute(_LIST_QUERY, {
            'filter': {
                'name': name,
                'problemType': problem_type,
            }
        })['models']

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
    ):
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
                'hasAnalysisData': False,
                'columns': cls.__select_schema_subset(schema['columns'], target_data.columns),
                'storageInfo': Data.upload(target_data),
            })

        return get_client().execute(_CREATE_MODEL, {
            'input': {
                'name': name,
                'problemType': schema['problemType'],
                'chunkAggregation': chunk_period,
                'dataSources': data_sources,
                'mainPerformanceMetric': main_performance_metric,
            },
        })

    @classmethod
    def delete(cls, model_id: str):
        """Delete a model"""
        return get_client().execute(_DELETE_MODEL, {'id': int(model_id)})

    @staticmethod
    def __select_schema_subset(
        columns: Iterable[ModelSchemaColumn], column_names: Container[str]
    ) -> List[ModelSchemaColumn]:
        return [column for column in columns if column['name'] in column_names]

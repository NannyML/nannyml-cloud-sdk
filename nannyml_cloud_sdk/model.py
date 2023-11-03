from typing import List, TypedDict

from gql import gql

from .client import get_client
from .enums import ProblemType

_LIST_QUERY = gql("""
    query listModels {
        models {
            id
            name
            problemType
            createdAt
        }
    }
""")


class ModelSummary(TypedDict):
    id: str
    name: str
    problemType: ProblemType
    createdAt: str


class Model:
    """Operations for working with machine learning models"""

    @classmethod
    def list(cls) -> List[ModelSummary]:
        """List defined models"""
        return get_client().execute(_LIST_QUERY)['models']

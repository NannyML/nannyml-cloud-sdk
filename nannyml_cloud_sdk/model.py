from typing import List, TypedDict

from gql import gql

from .client import get_client

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


class ModelListResponse(TypedDict):
    id: str
    name: str
    problemType: str
    createdAt: str


class Model:
    @classmethod
    def list(cls) -> List[ModelListResponse]:
        """List defined models"""
        return get_client().execute(_LIST_QUERY)['models']

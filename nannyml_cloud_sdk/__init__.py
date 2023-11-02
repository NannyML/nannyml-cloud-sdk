from .graphql_client import ProblemType
from .model import Model
from .schema import Schema


api_token: str = ""
url: str = ""


__all__ = [
    'Model',
    'ProblemType',
    'Schema',
]

from typing import List

from .client import get_client
from .graphql_client import ListModelsModels


class Model:
    @classmethod
    def list(cls) -> List[ListModelsModels]:
        """List defined models"""
        return get_client().list_models().models

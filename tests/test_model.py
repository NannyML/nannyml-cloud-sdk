import pytest
from gql.transport.exceptions import TransportQueryError
from nannyml_cloud_sdk import Model


def test_model_list(gql_client):
    # Validate query raises transport error, i.e. it passes schema validation
    with pytest.raises(TransportQueryError):
        Model.list()

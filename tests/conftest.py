import pytest
from gql import Client

import nannyml_cloud_sdk


@pytest.fixture(scope="session")
def gql_schema():
    with open("schema.graphql") as f:
        return f.read()


@pytest.fixture
def gql_client(gql_schema):
    client = Client(schema=gql_schema)
    nannyml_cloud_sdk.client._active_client = client
    return client

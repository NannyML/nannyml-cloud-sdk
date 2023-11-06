import datetime
from typing import Optional

from graphql import GraphQLScalarType
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from gql.utilities import update_schema_scalars

import nannyml_cloud_sdk


_active_client: Optional[Client] = None


def get_client() -> Client:
    global _active_client
    if _active_client is not None:
        return _active_client

    if not nannyml_cloud_sdk.url:
        raise RuntimeError("nannyml_cloud_sdk.url is not set")

    headers = {}
    if nannyml_cloud_sdk.api_token:
        headers['Authorization'] = f"ApiToken {nannyml_cloud_sdk.api_token}"

    transport = RequestsHTTPTransport(url=f"{nannyml_cloud_sdk.url}/api/graphql", headers=headers)
    _active_client = Client(
        transport=transport, fetch_schema_from_transport=True, parse_results=True, serialize_variables=True
    )

    # Update the schema with custom scalars
    with _active_client as _:
        assert _active_client.schema is not None
        update_schema_scalars(_active_client.schema, [DateTimeScalar])

    return _active_client


# Extension of the native GraphQL scalar types
DateTimeScalar = GraphQLScalarType(
    name="DateTime",
    serialize=lambda datetime: datetime.isoformat(),
    parse_value=lambda value: datetime.datetime.fromisoformat(value),
)

from typing import Optional

from gql import Client
from gql.transport.requests import RequestsHTTPTransport

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
    _active_client = Client(transport=transport, fetch_schema_from_transport=True)
    return _active_client

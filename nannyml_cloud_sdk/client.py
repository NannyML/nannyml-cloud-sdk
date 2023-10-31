from typing import Optional

from .graphql_client import Client

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

    _active_client = Client(url=f"{nannyml_cloud_sdk.url}/api/graphql", headers=headers)
    return _active_client

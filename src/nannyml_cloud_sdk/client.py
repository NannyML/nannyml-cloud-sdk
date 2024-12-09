import datetime
import functools
from typing import Any, Callable, Optional, TypeVar

from graphql import GraphQLScalarType
from gql import Client
from gql.transport.exceptions import TransportQueryError, TransportServerError
from gql.transport.requests import RequestsHTTPTransport
from gql.utilities import update_schema_scalars

import nannyml_cloud_sdk
from .errors import ApiError, LicenseError
from ._typing import Concatenate, ParamSpec

_T = TypeVar('_T')
_P = ParamSpec('_P')


_active_client: Optional[Client] = None


def get_client() -> Client:
    """Get the active GraphQL client or create a new one if none exists"""
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


def _translate_gql_errors(fn: Callable[Concatenate[Client, _P], _T]) -> Callable[_P, _T]:
    """Decorator to translate GraphQL errors into Python exceptions"""
    @functools.wraps(fn)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        try:
            # Passing active client as first argument. The `fn` is assumed to be an unbound instance method.
            return fn(get_client(), *args, **kwargs)
        except TransportQueryError as ex:
            if ex.errors is not None:
                raise ApiError(ex.errors[0]['message']) from ex
            else:
                raise ApiError(str(ex)) from ex
        except TransportServerError as ex:
            cause: Any = ex.__cause__
            if ex.code == 403:
                data = cause.response.json()
                if data.get('type') == 'LicenseError':
                    raise LicenseError(data.get('detail', '')) from ex
            raise
    return wrapper


execute = _translate_gql_errors(Client.execute)
"""Execute query against the configured NannyML Cloud GraphQL API.

Raises:
    ApiError: If the GraphQL query fails.
"""


# Extension of the native GraphQL scalar types
DateTimeScalar = GraphQLScalarType(
    name="DateTime",
    serialize=lambda datetime: datetime.isoformat(),
    parse_value=lambda value: datetime.datetime.fromisoformat(value),
)

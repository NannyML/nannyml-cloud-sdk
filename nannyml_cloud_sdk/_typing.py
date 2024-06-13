import sys
from typing import TypeVar

# We use TypedDict.__required_keys__, which was introduced in Python 3.9
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


if sys.version_info >= (3, 10):
    from typing import Concatenate, ParamSpec, TypeGuard
else:
    from typing_extensions import Concatenate, ParamSpec, TypeGuard


class GraphQLObject(TypedDict):
    __typename: str


_GqlT = TypeVar('_GqlT', bound=GraphQLObject)


def is_gql_type(obj: GraphQLObject, type_: type[_GqlT]) -> TypeGuard[_GqlT]:
    """Check if the given object is of the specified GraphQL type

    Note the class name is compared with the '__typename' field of the object. For this to work as intended the class
    names must match the GraphQL type names.
    """
    return obj['__typename'] == type_.__name__


__all__ = [
    'Concatenate',
    'GraphQLObject',
    'ParamSpec',
    'TypedDict',
    'is_gql_type',
]

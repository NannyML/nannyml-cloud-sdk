import sys

# We use TypedDict.__required_keys__, which was introduced in Python 3.9
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


if sys.version_info >= (3, 10):
    from typing import Concatenate, ParamSpec
else:
    from typing_extensions import Concatenate, ParamSpec


__all__ = [
    'Concatenate',
    'ParamSpec',
    'TypedDict',
]

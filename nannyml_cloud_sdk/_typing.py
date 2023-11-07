import sys

# We use TypedDict.__required_keys__, which was introduced in Python 3.9
if sys.version_info >= (3, 9):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = [
    'TypedDict'
]

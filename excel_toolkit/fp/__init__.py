"""Functional programming primitives for Excel CLI Toolkit.

All types are implemented in-house with zero external dependencies.
Public API is purely functional - classes are internal implementation details.

Example:
    from excel_toolkit.fp import ok, err, is_ok, unwrap

    result = ok(42)
    if is_ok(result):
        value = unwrap(result)
"""

# Result API - functions only
from excel_toolkit.fp.result import (
    ok,
    err,
    is_ok,
    is_err,
    unwrap,
    unwrap_or,
    unwrap_or_else,
    unwrap_err,
    to_result as result_to_result,
    UnwrapError,
)

# Maybe API - functions only
from excel_toolkit.fp.maybe import (
    some,
    nothing,
    is_some,
    is_nothing,
    unwrap as unwrap_maybe,
    unwrap_or as unwrap_or_maybe,
    unwrap_or_else as unwrap_or_else_maybe,
    to_maybe,
)

# Immutable utilities
from excel_toolkit.fp.immutable import immutable

__all__ = [
    # Result
    "ok",
    "err",
    "is_ok",
    "is_err",
    "unwrap",
    "unwrap_or",
    "unwrap_or_else",
    "unwrap_err",
    "result_to_result",
    "UnwrapError",
    # Maybe
    "some",
    "nothing",
    "is_some",
    "is_nothing",
    "unwrap_maybe",
    "unwrap_or_maybe",
    "unwrap_or_else_maybe",
    "to_maybe",
    # Utilities
    "immutable",
]

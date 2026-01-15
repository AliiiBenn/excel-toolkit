"""Public Maybe type functional API.

This module provides the functional interface for the Maybe type.
Users should import and use these functions instead of the internal classes.

Example:
    from excel_toolkit.fp import some, nothing, is_some, unwrap

    maybe = some(42)
    if is_some(maybe):
        value = unwrap(maybe)
"""

from typing import TypeVar, Callable, Any
from excel_toolkit.fp._maybe import Maybe, Some, Nothing, _NOTHING
from excel_toolkit.fp.result import Result, ok, err

T = TypeVar('T')
U = TypeVar('U')


# Constructors

def some(value: T) -> Maybe[T]:
    """Create a Some containing a value.

    Args:
        value: The value to wrap

    Returns:
        Some containing the value

    Example:
        maybe = some(42)
        maybe = some(dataframe)
    """
    return Some(value)


def nothing() -> Maybe[Any]:
    """Create Nothing (no value).

    Returns:
        The singleton Nothing instance

    Example:
        maybe = nothing()
    """
    return _NOTHING


# Predicates

def is_some(maybe: Maybe[T]) -> bool:
    """Check if maybe has a value.

    Args:
        maybe: Maybe to check

    Returns:
        True if maybe is Some, False otherwise

    Example:
        if is_some(maybe):
            print("Has value!")
    """
    return isinstance(maybe, Some)


def is_nothing(maybe: Maybe[T]) -> bool:
    """Check if maybe is Nothing.

    Args:
        maybe: Maybe to check

    Returns:
        True if maybe is Nothing, False otherwise

    Example:
        if is_nothing(maybe):
            print("No value!")
    """
    return isinstance(maybe, Nothing)


# Unwrapping

def unwrap(maybe: Maybe[T]) -> T:
    """Extract the value from a Some.

    Raises UnwrapError if maybe is Nothing.

    Args:
        maybe: Maybe to unwrap

    Returns:
        The value if maybe is Some

    Raises:
        UnwrapError: If maybe is Nothing

    Example:
        maybe = some(42)
        value = unwrap(maybe)  # 42
    """
    if is_some(maybe):
        return maybe._value  # type: ignore
    raise UnwrapError("Cannot unwrap Nothing: use unwrap_or or is_nothing first")


def unwrap_or(maybe: Maybe[T], default: T) -> T:
    """Extract the value from Some, or return default if Nothing.

    Args:
        maybe: Maybe to unwrap
        default: Default value to return if Nothing

    Returns:
        The value if Some, default otherwise

    Example:
        maybe = some(42)
        unwrap_or(maybe, 0)  # 42

        maybe = nothing()
        unwrap_or(maybe, 0)  # 0
    """
    if is_some(maybe):
        return maybe._value  # type: ignore
    return default


def unwrap_or_else(maybe: Maybe[T], fn: Callable[[], T]) -> T:
    """Extract the value from Some, or compute default if Nothing.

    Args:
        maybe: Maybe to unwrap
        fn: Function to compute default value

    Returns:
        The value if Some, result of fn otherwise

    Example:
        maybe = some(42)
        unwrap_or_else(maybe, lambda: expensive_computation())  # 42

        maybe = nothing()
        unwrap_or_else(maybe, lambda: expensive_computation())  # computed value
    """
    if is_some(maybe):
        return maybe._value  # type: ignore
    return fn()


# Conversion

def to_maybe(result: Result[T, Any]) -> Maybe[T]:
    """Convert Result to Maybe.

    Loses error information - keeps the value if Ok, returns Nothing if Err.

    Args:
        result: Result to convert

    Returns:
        Some if result is Ok, Nothing if result is Err

    Example:
        result = ok(42)
        maybe = to_maybe(result)  # Some(42)

        result = err("error")
        maybe = to_maybe(result)  # Nothing
    """
    from excel_toolkit.fp import is_ok  # Avoid circular import

    if is_ok(result):
        return some(result._value)  # type: ignore
    return nothing()


# Custom exception

class UnwrapError(Exception):
    """Raised when trying to unwrap a Nothing.

    Reused from result.py for consistency.
    """
    pass

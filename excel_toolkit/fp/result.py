"""Public Result type functional API.

This module provides the functional interface for the Result type.
Users should import and use these functions instead of the internal classes.

Example:
    from excel_toolkit.fp import ok, err, is_ok, unwrap

    result = ok(42)
    if is_ok(result):
        value = unwrap(result)
"""

from typing import TypeVar, Callable, Any, TypeAlias
from excel_toolkit.fp._result import Result, Ok, Err

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')


# Constructors

def ok(value: T) -> Result[T, Any]:
    """Create an Ok result containing a value.

    Args:
        value: The success value

    Returns:
        Ok result containing the value

    Example:
        result = ok(42)
        result = ok(dataframe)
    """
    return Ok(value)


def err(error: E) -> Result[Any, E]:
    """Create an Err result containing an error.

    Args:
        error: The error value

    Returns:
        Err result containing the error

    Example:
        result = err(FileNotFound("data.xlsx"))
        result = err("Something went wrong")
    """
    return Err(error)


# Predicates

def is_ok(result: Result[T, E]) -> bool:
    """Check if result is Ok.

    Args:
        result: Result to check

    Returns:
        True if result is Ok, False otherwise

    Example:
        if is_ok(result):
            print("Success!")
    """
    return isinstance(result, Ok)


def is_err(result: Result[T, E]) -> bool:
    """Check if result is Err.

    Args:
        result: Result to check

    Returns:
        True if result is Err, False otherwise

    Example:
        if is_err(result):
            print("Failed!")
    """
    return isinstance(result, Err)


# Unwrapping

def unwrap(result: Result[T, E]) -> T:
    """Extract the value from an Ok result.

    Raises UnwrapError if result is Err.

    Args:
        result: Result to unwrap

    Returns:
        The value if result is Ok

    Raises:
        UnwrapError: If result is Err

    Example:
        result = ok(42)
        value = unwrap(result)  # 42
    """
    if is_ok(result):
        return result._value  # type: ignore
    raise UnwrapError("Cannot unwrap Err: use unwrap_or or is_err first")


def unwrap_or(result: Result[T, E], default: T) -> T:
    """Extract the value from Ok, or return default if Err.

    Args:
        result: Result to unwrap
        default: Default value to return if result is Err

    Returns:
        The value if result is Ok, default otherwise

    Example:
        result = ok(42)
        unwrap_or(result, 0)  # 42

        result = err("error")
        unwrap_or(result, 0)  # 0
    """
    if is_ok(result):
        return result._value  # type: ignore
    return default


def unwrap_or_else(result: Result[T, E], fn: Callable[[], T]) -> T:
    """Extract the value from Ok, or compute default if Err.

    Args:
        result: Result to unwrap
        fn: Function to compute default value

    Returns:
        The value if result is Ok, result of fn otherwise

    Example:
        result = ok(42)
        unwrap_or_else(result, lambda: expensive_computation())  # 42

        result = err("error")
        unwrap_or_else(result, lambda: expensive_computation())  # computed value
    """
    if is_ok(result):
        return result._value  # type: ignore
    return fn()


def unwrap_err(result: Result[T, E]) -> E:
    """Extract the error from an Err result.

    Raises UnwrapError if result is Ok.

    Args:
        result: Result to unwrap

    Returns:
        The error if result is Err

    Raises:
        UnwrapError: If result is Ok

    Example:
        result = err(FileNotFound("data.xlsx"))
        error = unwrap_err(result)
    """
    if is_err(result):
        return result._error  # type: ignore
    raise UnwrapError("Cannot unwrap Ok: use is_ok first")


# Conversion

def to_result(value: 'Maybe[T]', error: E) -> Result[T, E]:
    """Convert Maybe to Result.

    Args:
        value: Maybe to convert
        error: Error to use if Maybe is Nothing

    Returns:
        Ok if Maybe is Some, Err with given error if Nothing

    Example:
        maybe = some(42)
        result = to_result(maybe, ValueError("No value"))

        nothing = nothing()
        result = to_result(nothing, ValueError("No value"))
    """
    from excel_toolkit.fp import is_some  # Avoid circular import

    if is_some(value):
        return ok(value._value)  # type: ignore
    return err(error)


# Custom exception

class UnwrapError(Exception):
    """Raised when trying to unwrap an Err or Nothing."""

    pass

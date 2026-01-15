"""Internal Result type implementation.

This module contains the internal class-based implementation of the Result type.
Users should not import this module directly - use the functions in result.py instead.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, TypeVar, Any

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')


class Result(ABC, Generic[T, E]):
    """Base class for Result type.

    Represents a computation that can either succeed with a value (Ok) or fail
    with an error (Err). This is the internal class-based implementation.

    Users should use the functions in result.py instead of importing these classes.
    """

    @abstractmethod
    def map(self, fn: Callable[[T], U]) -> 'Result[U, E]':
        """Apply function if Ok, pass through if Err.

        Args:
            fn: Function to apply to the value

        Returns:
            New Result with transformed value or original Err
        """
        pass

    @abstractmethod
    def and_then(
        self, fn: Callable[[T], 'Result[U, E]']
    ) -> 'Result[U, E]':
        """Chain Result-returning function.

        Args:
            fn: Function that takes the value and returns a Result

        Returns:
            Result from fn if Ok, original Err if Err
        """
        pass

    @abstractmethod
    def or_else(self, default: 'Result[T, E]') -> 'Result[T, E]':
        """Provide fallback Result if this is Err.

        Args:
            default: Result to return if this is Err

        Returns:
            This Result if Ok, default if Err
        """
        pass

    @abstractmethod
    def or_else_try(
        self, fn: Callable[[], 'Result[T, E]']
    ) -> 'Result[T, E]':
        """Provide lazy fallback Result if this is Err.

        Args:
            fn: Function that produces fallback Result

        Returns:
            This Result if Ok, result of fn if Err
        """
        pass


@dataclass(frozen=True)
class Ok(Result[T, E]):
    """Success variant containing a value.

    Internal class - users should use ok() function instead.

    Attributes:
        _value: The success value
    """

    _value: T

    def map(self, fn: Callable[[T], U]) -> 'Result[U, E]':
        """Apply function to the value."""
        return Ok(fn(self._value))

    def and_then(
        self, fn: Callable[[T], 'Result[U, E]']
    ) -> 'Result[U, E]':
        """Chain Result-returning function."""
        return fn(self._value)

    def or_else(self, default: 'Result[T, E]') -> 'Result[T, E]':
        """Return this Ok, ignore default."""
        return self

    def or_else_try(
        self, fn: Callable[[], 'Result[T, E]']
    ) -> 'Result[T, E]':
        """Return this Ok, ignore fn."""
        return self


@dataclass(frozen=True)
class Err(Result[T, E]):
    """Error variant containing an error.

    Internal class - users should use err() function instead.

    Attributes:
        _error: The error value
    """

    _error: E

    def map(self, fn: Callable[[T], U]) -> 'Result[U, E]':
        """Return this Err, ignore function."""
        return self

    def and_then(
        self, fn: Callable[[T], 'Result[U, E]']
    ) -> 'Result[U, E]':
        """Return this Err, ignore function."""
        return self

    def or_else(self, default: 'Result[T, E]') -> 'Result[T, E]':
        """Return the fallback Result."""
        return default

    def or_else_try(
        self, fn: Callable[[], 'Result[T, E]']
    ) -> 'Result[T, E]':
        """Return result of fallback function."""
        return fn()

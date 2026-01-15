"""Internal Maybe type implementation.

This module contains the internal class-based implementation of the Maybe type.
Users should not import this module directly - use the functions in maybe.py instead.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, TypeVar

T = TypeVar('T')
U = TypeVar('U')


class Maybe(ABC, Generic[T]):
    """Base class for Maybe type.

    Represents an optional value that can either exist (Some) or not exist (Nothing).
    This is the internal class-based implementation.

    Users should use the functions in maybe.py instead of importing these classes.
    """

    @abstractmethod
    def map(self, fn: Callable[[T], U]) -> 'Maybe[U]':
        """Apply function if Some, pass through if Nothing.

        Args:
            fn: Function to apply to the value

        Returns:
            Some with transformed value or original Nothing
        """
        pass

    @abstractmethod
    def and_then(self, fn: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        """Chain Maybe-returning function.

        Args:
            fn: Function that takes the value and returns a Maybe

        Returns:
            Maybe from fn if Some, original Nothing if Nothing
        """
        pass

    @abstractmethod
    def or_else(self, default: T) -> T:
        """Extract value or return default.

        Args:
            default: Default value to return if Nothing

        Returns:
            The value if Some, default otherwise
        """
        pass


@dataclass(frozen=True)
class Some(Maybe[T]):
    """Variant containing a value.

    Internal class - users should use some() function instead.

    Attributes:
        _value: The contained value
    """

    _value: T

    def map(self, fn: Callable[[T], U]) -> 'Maybe[U]':
        """Apply function to the value."""
        return Some(fn(self._value))

    def and_then(self, fn: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        """Chain Maybe-returning function."""
        return fn(self._value)

    def or_else(self, default: T) -> T:
        """Return the value, ignore default."""
        return self._value


@dataclass(frozen=True)
class Nothing(Maybe[T]):
    """Variant representing no value.

    This is a singleton - only one instance exists.

    Internal class - users should use nothing() function instead.
    """

    __slots__ = ()

    def map(self, fn: Callable[[T], U]) -> 'Maybe[U]':
        """Return this Nothing, ignore function."""
        return self

    def and_then(self, fn: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        """Return this Nothing, ignore function."""
        return self

    def or_else(self, default: T) -> T:
        """Return the default value."""
        return default


# Singleton instance - the only Nothing instance
_NOTHING: Maybe[Any] = Nothing()
"""The singleton Nothing instance.

Use nothing() function to access this instead of importing directly.
"""

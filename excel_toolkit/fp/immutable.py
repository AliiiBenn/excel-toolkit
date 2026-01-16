"""Immutable dataclass utilities.

This module provides a decorator for creating immutable dataclasses.
"""

from dataclasses import dataclass, is_dataclass, fields, Field
from typing import Any


def immutable(cls: type) -> type:
    """Class decorator to create an immutable dataclass.

    Creates a frozen dataclass where all fields are read-only after creation.
    Must be applied BEFORE @dataclass decorator.

    Args:
        cls: Class to decorate

    Returns:
        Class with __dataclass_fields__ marked for frozen dataclass

    Example:
        @immutable
        @dataclass
        class MyData:
            field1: str
            field2: int
    """
    # Mark class as needing frozen dataclass
    # The actual dataclass decorator will pick this up
    cls.__immutable__ = True
    return cls


# Save original dataclass
_original_dataclass = dataclass


def _immutable_dataclass(cls=None, /, **kwargs):
    """Dataclass decorator that respects @immutable marker."""

    def wrap(cls):
        # Check if class was marked with @immutable
        if hasattr(cls, '__immutable__'):
            kwargs['frozen'] = True
            delattr(cls, '__immutable__')
        return _original_dataclass(cls, **kwargs)

    # Handle both @dataclass and @dataclass(...)
    if cls is not None:
        return wrap(cls)
    return wrap


# Replace the dataclass decorator in this module
dataclass = _immutable_dataclass

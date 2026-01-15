"""Unit tests for Maybe type."""

import pytest
from excel_toolkit.fp import some, nothing, is_some, is_nothing, unwrap_maybe, unwrap_or_maybe, unwrap_or_else_maybe


class TestMaybeConstruction:
    """Tests for Maybe construction."""

    def test_some_creates_some_instance(self):
        """some() should create Some instance."""
        maybe = some(42)
        assert is_some(maybe)
        assert not is_nothing(maybe)

    def test_nothing_creates_nothing_instance(self):
        """nothing() should create Nothing instance."""
        maybe = nothing()
        assert is_nothing(maybe)
        assert not is_some(maybe)

    def test_some_with_none(self):
        """some(None) should create Some with None value."""
        maybe = some(None)
        assert is_some(maybe)
        assert unwrap_maybe(maybe) is None

    def test_some_with_dataframe(self):
        """some() should work with complex types."""
        import pandas as pd

        df = pd.DataFrame({"a": [1, 2, 3]})
        maybe = some(df)
        assert is_some(maybe)
        assert unwrap_maybe(maybe).equals(df)

    def test_nothing_is_singleton(self):
        """nothing() should always return the same instance."""
        maybe1 = nothing()
        maybe2 = nothing()
        assert maybe1 is maybe2


class TestMaybePredicates:
    """Tests for Maybe predicates."""

    def test_is_some_true_for_some(self):
        """is_some() should return True for Some."""
        assert is_some(some(42))

    def test_is_some_false_for_nothing(self):
        """is_some() should return False for Nothing."""
        assert not is_some(nothing())

    def test_is_nothing_true_for_nothing(self):
        """is_nothing() should return True for Nothing."""
        assert is_nothing(nothing())

    def test_is_nothing_false_for_some(self):
        """is_nothing() should return False for Some."""
        assert not is_nothing(some(42))


class TestMaybeUnwrap:
    """Tests for Maybe unwrapping."""

    def test_unwrap_some(self):
        """unwrap_maybe() should extract value from Some."""
        maybe = some(42)
        assert unwrap_maybe(maybe) == 42

    def test_unwrap_nothing_raises(self):
        """unwrap_maybe() should raise UnwrapError for Nothing."""
        maybe = nothing()
        with pytest.raises(Exception):  # UnwrapError
            unwrap_maybe(maybe)

    def test_unwrap_or_with_some(self):
        """unwrap_or_maybe() should return value for Some."""
        maybe = some(42)
        assert unwrap_or_maybe(maybe, 0) == 42

    def test_unwrap_or_with_nothing(self):
        """unwrap_or_maybe() should return default for Nothing."""
        maybe = nothing()
        assert unwrap_or_maybe(maybe, 0) == 0

    def test_unwrap_or_else_with_some(self):
        """unwrap_or_else_maybe() should return value for Some."""
        maybe = some(42)
        assert unwrap_or_else_maybe(maybe, lambda: 0) == 42

    def test_unwrap_or_else_with_nothing(self):
        """unwrap_or_else_maybe() should return computed default for Nothing."""
        maybe = nothing()
        assert unwrap_or_else_maybe(maybe, lambda: 100) == 100


class TestMaybeMap:
    """Tests for Maybe.map()."""

    def test_map_on_some(self):
        """map() should apply function to Some value."""
        maybe = some(5)
        mapped = maybe.map(lambda x: x * 2)
        assert is_some(mapped)
        assert unwrap_maybe(mapped) == 10

    def test_map_on_nothing(self):
        """map() should be ignored on Nothing."""
        maybe = nothing()
        mapped = maybe.map(lambda x: x * 2)
        assert is_nothing(mapped)

    def test_map_chain(self):
        """map() can be chained."""
        maybe = some(5)
        mapped = maybe.map(lambda x: x * 2).map(lambda x: x + 1)
        assert unwrap_maybe(mapped) == 11

    def test_map_type_transformation(self):
        """map() can transform types."""
        maybe = some(42)
        mapped = maybe.map(lambda x: str(x))
        assert is_some(mapped)
        assert unwrap_maybe(mapped) == "42"


class TestMaybeAndThen:
    """Tests for Maybe.and_then()."""

    def test_and_then_on_some(self):
        """and_then() should apply function to Some value."""
        maybe = some(5)
        chained = maybe.and_then(lambda x: some(x * 2))
        assert is_some(chained)
        assert unwrap_maybe(chained) == 10

    def test_and_then_on_nothing(self):
        """and_then() should be ignored on Nothing."""
        maybe = nothing()
        chained = maybe.and_then(lambda x: some(x * 2))
        assert is_nothing(chained)

    def test_and_then_chain(self):
        """and_then() can be chained."""
        maybe = some(20)
        chained = (
            maybe.and_then(lambda x: some(x // 2))
            .and_then(lambda x: some(x + 1))
            .and_then(lambda x: some(x * 3))
        )
        assert unwrap_maybe(chained) == 33  # ((20 // 2) + 1) * 3

    def test_and_then_short_circuit_on_nothing(self):
        """and_then() should short-circuit on Nothing."""
        maybe = some(5)
        chained = maybe.and_then(lambda x: nothing()).and_then(
            lambda x: some(x * 2)
        )
        assert is_nothing(chained)


class TestMaybeOrElse:
    """Tests for Maybe.or_else()."""

    def test_or_else_on_some(self):
        """or_else() should return value, ignore default."""
        maybe = some(42)
        assert maybe.or_else(0) == 42

    def test_or_else_on_nothing(self):
        """or_else() should return default for Nothing."""
        maybe = nothing()
        assert maybe.or_else(0) == 0


class TestMaybeImmutability:
    """Tests for Maybe immutability."""

    def test_some_is_immutable(self):
        """Some instances should be immutable."""
        maybe = some(42)
        with pytest.raises(Exception):  # FrozenInstanceError
            maybe._value = 100

    def test_nothing_is_immutable(self):
        """Nothing instance should be immutable."""
        maybe = nothing()
        with pytest.raises(Exception):  # FrozenInstanceError
            maybe._value = 100


class TestMaybeEquality:
    """Tests for Maybe equality."""

    def test_some_equality(self):
        """Some instances should be equal if values are equal."""
        maybe1 = some(42)
        maybe2 = some(42)
        assert maybe1 == maybe2

    def test_some_inequality(self):
        """Some instances should not be equal if values differ."""
        maybe1 = some(42)
        maybe2 = some(43)
        assert maybe1 != maybe2

    def test_nothing_equality(self):
        """Nothing instances should be equal (singleton)."""
        maybe1 = nothing()
        maybe2 = nothing()
        assert maybe1 == maybe2
        assert maybe1 is maybe2  # Same instance

    def test_some_nothing_inequality(self):
        """Some and Nothing should never be equal."""
        assert some(42) != nothing()

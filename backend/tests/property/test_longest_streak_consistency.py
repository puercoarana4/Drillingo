"""
Property 5: Consistencia longest_streak
For any sequence of activity dates, longest_streak >= current_streak always holds.

Feature: drillingo, Property 5: longest_streak >= current_streak
Validates: Requirements 8.2
"""
from datetime import date

from hypothesis import given, settings
from hypothesis import strategies as st

# Reuse the pure computation helper from Property 2
from tests.property.test_streak_invariant import compute_streak_from_dates


@given(
    activity_dates=st.lists(
        st.dates(min_value=date(2024, 1, 1), max_value=date(2025, 12, 31)),
        min_size=1,
        max_size=365,
    )
    .map(lambda ds: sorted(set(ds)))
    .filter(lambda ds: len(ds) >= 1),
)
@settings(max_examples=100)
def test_longest_streak_always_gte_current(activity_dates: list[date]):
    """
    Property 5: longest_streak is always >= current_streak for any
    sequence of activity dates.
    """
    state = compute_streak_from_dates(activity_dates)
    assert state.longest_streak >= state.current_streak, (
        f"longest_streak={state.longest_streak} < current_streak={state.current_streak} "
        f"for dates={activity_dates}"
    )


@given(
    activity_dates=st.lists(
        st.dates(min_value=date(2024, 1, 1), max_value=date(2025, 12, 31)),
        min_size=1,
        max_size=365,
    )
    .map(lambda ds: sorted(set(ds)))
    .filter(lambda ds: len(ds) >= 1),
)
@settings(max_examples=100)
def test_longest_streak_is_non_decreasing(activity_dates: list[date]):
    """
    Property 5b: longest_streak never decreases as more dates are added.
    """
    prev_longest = 0
    for i in range(1, len(activity_dates) + 1):
        state = compute_streak_from_dates(activity_dates[:i])
        assert state.longest_streak >= prev_longest, (
            f"longest_streak decreased from {prev_longest} to {state.longest_streak}"
        )
        prev_longest = state.longest_streak

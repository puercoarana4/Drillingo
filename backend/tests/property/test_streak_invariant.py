"""
Property 2: Invariante del Streak
For any sequence of activity dates, the current_streak on the last day equals
the number of consecutive days ending on that day.

Feature: drillingo, Property 2: streak invariant
Validates: Requirements 8.7
"""
from datetime import date, timedelta

from hypothesis import given, settings
from hypothesis import strategies as st


# ── Pure streak computation (mirrors streak_engine.py logic) ─────────────────

class StreakState:
    def __init__(self):
        self.current_streak = 0
        self.longest_streak = 0
        self.last_activity_date: date | None = None


def compute_streak_from_dates(activity_dates: list[date]) -> StreakState:
    """
    Simulate the Streak Engine over a sorted list of unique activity dates.
    Returns the final StreakState.
    """
    state = StreakState()
    for d in activity_dates:
        if state.last_activity_date is None:
            state.current_streak = 1
        elif d == state.last_activity_date:
            # Same day — idempotent
            continue
        elif d == state.last_activity_date + timedelta(days=1):
            state.current_streak += 1
        else:
            state.current_streak = 1

        if state.current_streak > state.longest_streak:
            state.longest_streak = state.current_streak

        state.last_activity_date = d

    return state


def count_consecutive_days_ending_at(dates: list[date], target: date) -> int:
    """
    Count how many consecutive days ending at `target` have activity.
    """
    date_set = set(dates)
    count = 0
    current = target
    while current in date_set:
        count += 1
        current -= timedelta(days=1)
    return count


# ── Property test ─────────────────────────────────────────────────────────────

@given(
    activity_dates=st.lists(
        st.dates(min_value=date(2024, 1, 1), max_value=date(2025, 12, 31)),
        min_size=1,
        max_size=365,
    )
    .map(lambda ds: sorted(set(ds)))  # deduplicate and sort
    .filter(lambda ds: len(ds) >= 1),
)
@settings(max_examples=100)
def test_streak_invariant(activity_dates: list[date]):
    """
    Property 2: current_streak at the last day equals the number of
    consecutive days with activity ending on that day.
    """
    state = compute_streak_from_dates(activity_dates)
    last_day = activity_dates[-1]
    expected = count_consecutive_days_ending_at(activity_dates, last_day)

    assert state.current_streak == expected, (
        f"current_streak={state.current_streak} but expected={expected} "
        f"for dates={activity_dates}"
    )

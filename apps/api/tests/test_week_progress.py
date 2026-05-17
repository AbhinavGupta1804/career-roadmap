"""Run: cd apps/api && .venv/Scripts/python -m pytest tests/test_week_progress.py -q"""

from app.schemas.progress import WeekProgress
from app.services.week_progress import apply_week_toggle, compute_streaks


def test_compute_streaks_consecutive() -> None:
    current, longest = compute_streaks([1, 2, 3, 5])
    assert current == 1  # week 4 gap breaks streak before week 5
    assert longest == 3

    current_full, _ = compute_streaks([1, 2, 3])
    assert current_full == 3


def test_compute_streaks_gap_breaks_current() -> None:
    current, longest = compute_streaks([1, 2, 4, 5])
    assert current == 2
    assert longest == 2


def test_apply_week_toggle() -> None:
    progress = WeekProgress()
    updated = apply_week_toggle(progress, week=1, done=True, total_weeks=12)
    assert updated.completed_weeks == [1]
    assert updated.current_streak == 1
    assert updated.last_check_in is not None

    updated = apply_week_toggle(updated, week=2, done=True, total_weeks=12)
    assert updated.completed_weeks == [1, 2]
    assert updated.current_streak == 2

    updated = apply_week_toggle(updated, week=2, done=False, total_weeks=12)
    assert updated.completed_weeks == [1]
    assert updated.current_streak == 1

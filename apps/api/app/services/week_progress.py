"""Week completion tracking and streak calculation for learning plans."""

from __future__ import annotations

from datetime import date

from app.schemas.progress import WeekProgress


def compute_streaks(completed_weeks: list[int]) -> tuple[int, int]:
    """Return (current_streak, longest_streak) from sorted unique week numbers."""
    completed = sorted(set(completed_weeks))
    if not completed:
        return 0, 0

    longest = 1
    run = 1
    for i in range(1, len(completed)):
        if completed[i] == completed[i - 1] + 1:
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    current = 0
    expect = completed[-1]
    for week in reversed(completed):
        if week == expect:
            current += 1
            expect -= 1
        else:
            break

    return current, longest


def apply_week_toggle(
    progress: WeekProgress,
    *,
    week: int,
    done: bool,
    total_weeks: int,
) -> WeekProgress:
    if week > total_weeks:
        msg = f"Week {week} is outside your {total_weeks}-week plan"
        raise ValueError(msg)

    completed = set(progress.completed_weeks)
    if done:
        completed.add(week)
    else:
        completed.discard(week)

    ordered = sorted(completed)
    current, longest = compute_streaks(ordered)
    return WeekProgress(
        completed_weeks=ordered,
        current_streak=current,
        longest_streak=max(longest, progress.longest_streak),
        last_check_in=date.today().isoformat(),
    )


def parse_week_progress(raw: dict | None) -> WeekProgress:
    if not raw:
        return WeekProgress()
    return WeekProgress.model_validate(raw)

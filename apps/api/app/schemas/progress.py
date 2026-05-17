from pydantic import BaseModel, Field


class WeekProgress(BaseModel):
    completed_weeks: list[int] = Field(default_factory=list)
    current_streak: int = Field(ge=0, default=0)
    longest_streak: int = Field(ge=0, default=0)
    last_check_in: str | None = None  # ISO date YYYY-MM-DD


class WeekProgressUpdate(BaseModel):
    week: int = Field(ge=1)
    done: bool

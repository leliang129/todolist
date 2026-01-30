from pydantic import BaseModel


class StatsSummary(BaseModel):
    total_todos: int
    today_completed: int
    week_completion_rate: float

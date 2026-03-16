from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def _validate_iso_datetime(field_name: str, v: str | None) -> str | None:
    if v is not None:
        try:
            datetime.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(
                f"Invalid {field_name} format '{v}'. "
                "Use ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
            ) from exc
    return v


class AddHabitInput(BaseModel):
    name: str = Field(..., description="Name of the habit")
    description: str | None = Field(None, description="Description of the habit")
    category_id: int | None = Field(None, description="Category ID of the habit")
    frequency_type: Literal["daily", "weekly", "monthly"] = Field(
        ..., description="Frequency type of the habit"
    )
    frequency_target: int = Field(default=1, ge=1, description="Frequency target of the habit")


class AddTodoInput(BaseModel):
    title: str = Field(..., description="Title of the todo")
    notes: str | None = Field(None, description="Notes of the todo")
    priority: Literal["low", "medium", "high"] = Field(
        default="medium", description="Priority of the todo"
    )
    due_date: str | None = Field(None, description="ISO 8601 date string")
    category_id: int | None = Field(None, description="Category ID of the todo")
    habit_id: int | None = Field(None, description="Habit ID of the todo")

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: str | None) -> str | None:
        return _validate_iso_datetime("due_date", v)


class AddCategoryInput(BaseModel):
    name: str = Field(..., description="Name of the category")
    color: str | None = Field(None, description="Color of the category")
    sort_order: int = Field(default=0, description="Sort order of the category")


class CompleteHabitInput(BaseModel):
    habit_id: int = Field(..., description="ID of the habit to complete")
    note: str | None = Field(None, description="Optional journal entry")
    completed_at: str | None = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 datetime, defaults to now",
    )

    @field_validator("completed_at")
    @classmethod
    def validate_completed_at(cls, v: str | None) -> str | None:
        return _validate_iso_datetime("completed_at", v)


class CompleteTodoInput(BaseModel):
    todo_id: int = Field(..., description="ID of the todo to complete")
    note: str | None = Field(None, description="Optional journal entry")
    completed_at: str | None = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 datetime, defaults to now",
    )

    @field_validator("completed_at")
    @classmethod
    def validate_completed_at(cls, v: str | None) -> str | None:
        return _validate_iso_datetime("completed_at", v)


class ArchiveHabitInput(BaseModel):
    habit_id: int = Field(..., description="ID of the habit to archive")
    archived_at: str | None = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 datetime, defaults to now",
    )

    @field_validator("archived_at")
    @classmethod
    def validate_archived_at(cls, v: str | None) -> str | None:
        return _validate_iso_datetime("archived_at", v)


class ListHabitsInput(BaseModel):
    category_id: int | None = Field(None, description="Category ID of the habit")
    include_archived: bool = Field(default=False, description="Include archived habits")


class ListTodosInput(BaseModel):
    category_id: int | None = Field(None, description="Category ID of the todo")
    include_completed: bool = Field(default=False, description="Include completed todos")


class ListCategoriesInput(BaseModel):
    pass


class RunQueryInput(BaseModel):
    sql: str = Field(..., min_length=1, description="SQL query to execute")

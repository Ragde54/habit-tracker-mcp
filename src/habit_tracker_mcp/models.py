from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from habit_tracker_mcp.database import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    color: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (CheckConstraint("color LIKE '#%'", name="ck_categories_color_hex"),)

    habits: Mapped[list[Habit]] = relationship("Habit", back_populates="category")
    todos: Mapped[list[Todo]] = relationship("Todo", back_populates="category")


class Habit(Base):
    __tablename__ = "habits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    frequency_type: Mapped[str] = mapped_column(Text, nullable=False)
    frequency_target: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, server_default=func.now(), nullable=False)
    archived_at: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        CheckConstraint(
            "frequency_type IN ('daily', 'weekly', 'monthly')", name="ck_habits_frequency_type"
        ),
    )

    category: Mapped[Category] = relationship("Category", back_populates="habits")
    completions: Mapped[list[HabitCompletion]] = relationship(
        "HabitCompletion", back_populates="habit"
    )
    todos: Mapped[list[Todo]] = relationship("Todo", back_populates="habit")


class HabitCompletion(Base):
    __tablename__ = "habit_completions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"), nullable=False)
    completed_at: Mapped[str] = mapped_column(Text, server_default=func.now(), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    __table_args__ = (
        CheckConstraint("source IN ('manual', 'todo')", name="ck_habit_completions_source"),
    )

    habit: Mapped[Habit] = relationship("Habit", back_populates="completions")


class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    habit_id: Mapped[int | None] = mapped_column(ForeignKey("habits.id"), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(Text, server_default=func.now(), nullable=False)
    __table_args__ = (
        CheckConstraint("priority IN ('low', 'medium', 'high')", name="ck_todos_priority"),
    )

    category: Mapped[Category] = relationship("Category", back_populates="todos")
    habit: Mapped[Habit | None] = relationship("Habit", back_populates="todos")

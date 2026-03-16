# scripts/seed.py
from habit_tracker_mcp.database import SessionLocal
from habit_tracker_mcp.orm import Category, Habit, Todo


def seed() -> None:
    db = SessionLocal()
    try:
        health = Category(name="Health", color="#FF5733", sort_order=0)
        learning = Category(name="Learning", color="#33C1FF", sort_order=1)
        work = Category(name="Work", color="#FF33A8", sort_order=2)
        db.add_all([health, learning, work])
        db.flush()

        habit1 = Habit(
            category_id=health.id,
            name="Morning run",
            frequency_type="weekly",
            frequency_target=3,
        )
        habit2 = Habit(
            category_id=learning.id,
            name="Read 30 mins",
            frequency_type="daily",
            frequency_target=1,
        )
        habit3 = Habit(
            category_id=health.id,
            name="Drink water",
            frequency_type="daily",
            frequency_target=3,
        )
        db.add_all([habit1, habit2, habit3])
        db.flush()

        todo = Todo(
            category_id=learning.id,
            title="Read MCP docs",
            priority="high",
        )
        db.add(todo)
        db.commit()
        print("Seeded successfully.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()

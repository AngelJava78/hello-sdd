from datetime import date, timedelta
from typing import TypedDict


class Habit(TypedDict):
    name: str
    completed_dates: list[str]


class HabitData(TypedDict):
    habits: list[Habit]


class HabitSummary(TypedDict):
    name: str
    streak: int


def normalize_name(name: str) -> str:
    normalized_name = name.strip().casefold()
    if not normalized_name:
        raise ValueError("El nombre del hábito no puede estar vacío.")
    return normalized_name


def create_habit(data: HabitData, name: str) -> HabitData:
    display_name = name.strip()
    normalized_name = normalize_name(display_name)

    if any(
        normalize_name(habit["name"]) == normalized_name
        for habit in data["habits"]
    ):
        raise ValueError("Ya existe un hábito con ese nombre.")

    return {
        "habits": [
            *data["habits"],
            {"name": display_name, "completed_dates": []},
        ]
    }


def mark_habit_done(
    data: HabitData, name: str, today: date
) -> tuple[HabitData, bool]:
    normalized_name = normalize_name(name)
    habits = [
        {**habit, "completed_dates": list(habit["completed_dates"])}
        for habit in data["habits"]
    ]

    for habit in habits:
        if normalize_name(habit["name"]) != normalized_name:
            continue

        date_string = today.isoformat()
        already_done = date_string in habit["completed_dates"]
        if not already_done:
            habit["completed_dates"].append(date_string)
        return {"habits": habits}, already_done

    raise LookupError("No existe un hábito con ese nombre.")


def calculate_streak(completed_dates: list[str], today: date) -> int:
    completed = set(completed_dates)
    if today.isoformat() in completed:
        current_date = today
    elif (today - timedelta(days=1)).isoformat() in completed:
        current_date = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while current_date.isoformat() in completed:
        streak += 1
        current_date -= timedelta(days=1)
    return streak


def list_habits(data: HabitData, today: date) -> list[HabitSummary]:
    summaries = [
        {
            "name": habit["name"],
            "streak": calculate_streak(habit["completed_dates"], today),
        }
        for habit in data["habits"]
    ]
    return sorted(
        summaries,
        key=lambda habit: (-habit["streak"], normalize_name(habit["name"])),
    )

import pytest
from datetime import date

from habits.core import (
    HabitData,
    calculate_streak,
    create_habit,
    list_habits,
    mark_habit_done,
    normalize_name,
)
from habits.storage import load_data, save_data


def test_normalize_name_trims_surrounding_spaces_and_ignores_case() -> None:
    assert normalize_name("  Leer Apuntes  ") == "leer apuntes"


@pytest.mark.parametrize("name", ["", " ", "\t\n"])
def test_normalize_name_rejects_empty_or_whitespace_only(name: str) -> None:
    with pytest.raises(ValueError, match="El nombre del hábito no puede estar vacío"):
        normalize_name(name)


def test_create_habit_preserves_display_name_and_initializes_dates() -> None:
    data: HabitData = {"habits": []}

    updated = create_habit(data, "  Leer Apuntes  ")

    assert updated == {
        "habits": [{"name": "Leer Apuntes", "completed_dates": []}]
    }
    assert data == {"habits": []}


@pytest.mark.parametrize("duplicate", ["LEER", " leer "])
def test_create_habit_rejects_normalized_duplicate_without_mutation(
    duplicate: str,
) -> None:
    data: HabitData = {
        "habits": [{"name": "Leer", "completed_dates": ["2026-10-09"]}]
    }

    with pytest.raises(ValueError, match="Ya existe un hábito con ese nombre"):
        create_habit(data, duplicate)

    assert data == {
        "habits": [{"name": "Leer", "completed_dates": ["2026-10-09"]}]
    }


def test_created_habit_can_be_saved_and_loaded_again(tmp_path) -> None:
    path = tmp_path / "habits.json"
    data = load_data(path)

    save_data(path, create_habit(data, "Estudiar inglés"))

    assert load_data(path) == {
        "habits": [{"name": "Estudiar inglés", "completed_dates": []}]
    }


def test_mark_habit_done_records_date_and_is_idempotent() -> None:
    data: HabitData = {
        "habits": [{"name": "Leer", "completed_dates": []}]
    }
    today = date(2026, 10, 9)

    updated, already_done = mark_habit_done(data, " leer ", today)

    assert already_done is False
    assert updated == {
        "habits": [{"name": "Leer", "completed_dates": ["2026-10-09"]}]
    }

    repeated, already_done = mark_habit_done(updated, "LEER", today)

    assert already_done is True
    assert repeated == updated
    assert data["habits"][0]["completed_dates"] == []


def test_mark_habit_done_rejects_unknown_habit() -> None:
    with pytest.raises(LookupError, match="No existe un hábito con ese nombre"):
        mark_habit_done({"habits": []}, "Leer", date(2026, 10, 9))


@pytest.mark.parametrize(
    ("dates", "today", "expected"),
    [
        (["2026-10-09", "2026-10-08", "2026-10-07"], date(2026, 10, 9), 3),
        (["2026-10-08", "2026-10-07"], date(2026, 10, 9), 2),
        (["2026-10-09", "2026-10-07"], date(2026, 10, 9), 1),
        (["2026-10-06"], date(2026, 10, 9), 0),
        ([], date(2026, 10, 9), 0),
        (["2026-03-01", "2026-02-28", "2026-02-27"], date(2026, 3, 1), 3),
    ],
)
def test_calculate_streak(
    dates: list[str], today: date, expected: int
) -> None:
    assert calculate_streak(dates, today) == expected


def test_list_habits_orders_by_streak_then_normalized_name() -> None:
    data: HabitData = {
        "habits": [
            {"name": "Zeta", "completed_dates": ["2026-10-09"]},
            {"name": "beta", "completed_dates": ["2026-10-08"]},
            {"name": "Alpha", "completed_dates": ["2026-10-09"]},
            {"name": "Ayer", "completed_dates": []},
        ]
    }

    result = list_habits(data, date(2026, 10, 9))

    assert [(habit["name"], habit["streak"]) for habit in result] == [
        ("Alpha", 1),
        ("beta", 1),
        ("Zeta", 1),
        ("Ayer", 0),
    ]

import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import cast

from habits.core import HabitData


DATA_FILENAME = ".habits-cli.json"


def get_data_path() -> Path:
    return Path.cwd() / DATA_FILENAME


class InvalidDataError(ValueError):
    exit_code: int = 1


def load_data(path: Path | None = None) -> HabitData:
    data_path = path if path is not None else get_data_path()
    try:
        with data_path.open("r", encoding="utf-8") as data_file:
            payload = json.load(data_file)
    except FileNotFoundError:
        return {"habits": []}
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise InvalidDataError(
            f"El archivo de datos no contiene JSON válido: {error}"
        ) from error
    if not isinstance(payload, dict) or not isinstance(
        payload.get("habits"), list
    ):
        raise InvalidDataError("El archivo de datos no tiene una estructura válida.")

    for habit in payload["habits"]:
        if (
            not isinstance(habit, dict)
            or not isinstance(habit.get("name"), str)
            or not isinstance(habit.get("completed_dates"), list)
        ):
            raise InvalidDataError(
                "El archivo de datos contiene un hábito con una estructura inválida."
            )
        for completed_date in habit["completed_dates"]:
            if not isinstance(completed_date, str):
                raise InvalidDataError(
                    "El archivo de datos contiene una fecha de cumplimiento inválida."
                )
            try:
                parsed_date = date.fromisoformat(completed_date)
            except ValueError as error:
                raise InvalidDataError(
                    "El archivo de datos contiene una fecha de cumplimiento inválida."
                ) from error
            if parsed_date.isoformat() != completed_date:
                raise InvalidDataError(
                    "El archivo de datos contiene una fecha de cumplimiento inválida."
                )
    return cast(HabitData, payload)


def save_data(path: Path | None, data: HabitData) -> None:
    data_path = path if path is not None else get_data_path()
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=data_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(data, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.write("\n")

        os.replace(temporary_path, data_path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass

import argparse
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from habits.core import create_habit, list_habits, mark_habit_done
from habits.storage import (
    InvalidDataError,
    get_data_path,
    load_data,
    save_data,
)


class CliUsageError(Exception):
    pass


class SpanishArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.print_usage(sys.stderr)
        raise CliUsageError("Argumentos no válidos. Revisa el uso del comando.")

    def print_usage(self, file=None) -> None:
        target = file if file is not None else sys.stdout
        target.write(f"uso: {self.usage or 'habits'}\n")

    def format_help(self) -> str:
        return super().format_help().replace("usage:", "uso:", 1)


def _new_parser(**kwargs) -> SpanishArgumentParser:
    return SpanishArgumentParser(
        prog="habits",
        add_help=False,
        **kwargs,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = _new_parser(
        description="Gestiona tus hábitos de estudio desde la terminal.",
        usage="habits [opciones] comando",
    )
    options = parser.add_argument_group("Opciones")
    options.add_argument(
        "-h",
        "--help",
        action="help",
        help="muestra esta ayuda y termina",
    )
    commands = parser.add_subparsers(
        dest="command",
        title="Comandos",
        required=True,
        parser_class=SpanishArgumentParser,
    )

    add_parser = commands.add_parser(
        "add",
        help="crea un hábito",
        description="Crea un hábito de estudio.",
    )
    add_parser.add_argument("name", help="nombre del hábito")

    done_parser = commands.add_parser(
        "done",
        help="marca un hábito como hecho hoy",
        description="Registra el cumplimiento de hoy.",
    )
    done_parser.add_argument("name", help="nombre del hábito")

    list_parser = commands.add_parser(
        "list",
        help="muestra los hábitos y sus rachas",
        description="Muestra todos los hábitos y sus rachas actuales.",
    )
    del list_parser
    return parser


def _load_or_report(path: Path):
    try:
        return load_data(path)
    except InvalidDataError as error:
        print(str(error), file=sys.stderr)
    except OSError as error:
        print(f"No se pudo leer el archivo de datos: {error}", file=sys.stderr)
    return None


def _save_or_report(path: Path, data) -> bool:
    try:
        save_data(path, data)
    except OSError as error:
        print(f"No se pudo guardar el archivo de datos: {error}", file=sys.stderr)
        return False
    return True


def main(
    arguments: Sequence[str] | None = None,
    *,
    data_path: Path | None = None,
    today: date | None = None,
) -> int:
    try:
        args = build_parser().parse_args(arguments)
    except CliUsageError as error:
        print(str(error), file=sys.stderr)
        return 2

    current_date = today if today is not None else date.today()
    resolved_data_path = data_path if data_path is not None else get_data_path()
    data = _load_or_report(resolved_data_path)
    if data is None:
        return 1

    if args.command == "add":
        try:
            updated_data = create_habit(data, args.name)
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 1
        if not _save_or_report(resolved_data_path, updated_data):
            return 1
        print(f"Hábito creado: {args.name.strip()}")
        return 0

    if args.command == "done":
        try:
            updated_data, already_done = mark_habit_done(
                data, args.name, current_date
            )
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 1
        except LookupError:
            print(
                "No existe ese hábito. Consulta la lista con "
                "'python -m habits list'.",
                file=sys.stderr,
            )
            return 1

        if already_done:
            print(f"{args.name.strip()} ya estaba marcado hoy.")
            return 0
        if not _save_or_report(resolved_data_path, updated_data):
            return 1
        print(f"{args.name.strip()} marcado como hecho hoy.")
        return 0

    if args.command == "list":
        if not data["habits"]:
            print("No hay hábitos todavía. Crea tu primer hábito con 'add'.")
            return 0
        try:
            summaries = list_habits(data, current_date)
        except (KeyError, TypeError, ValueError) as error:
            print(f"El archivo de datos contiene hábitos inválidos: {error}", file=sys.stderr)
            return 1
        for habit in summaries:
            unit = "día" if habit["streak"] == 1 else "días"
            print(f"{habit['name']}: {habit['streak']} {unit}")
        return 0

    raise RuntimeError(f"Comando no gestionado: {args.command}")

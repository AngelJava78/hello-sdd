from datetime import date
from pathlib import Path

import pytest

from habits.cli import main


def run_cli(
    arguments: list[str],
    data_path: Path,
    today: date = date(2026, 10, 9),
) -> int:
    return main(arguments, data_path=data_path, today=today)


def test_add_creates_and_confirms_habit(tmp_path: Path, capsys) -> None:
    path = tmp_path / "habits.json"

    assert run_cli(["add", "Leer apuntes"], path) == 0
    assert "Hábito creado: Leer apuntes" in capsys.readouterr().out
    assert run_cli(["list"], path) == 0
    assert "Leer apuntes" in capsys.readouterr().out


@pytest.mark.parametrize("name", ["", "   "])
def test_add_rejects_empty_name_without_saving(
    tmp_path: Path, capsys, name: str
) -> None:
    path = tmp_path / "habits.json"

    assert run_cli(["add", name], path) == 1
    assert "nombre del hábito no puede estar vacío" in capsys.readouterr().err
    assert not path.exists()


def test_add_rejects_duplicate_name_without_changing_saved_data(
    tmp_path: Path, capsys
) -> None:
    path = tmp_path / "habits.json"
    assert run_cli(["add", "Leer"], path) == 0
    original_contents = path.read_bytes()

    assert run_cli(["add", " leer "], path) == 1

    assert "Ya existe un hábito" in capsys.readouterr().err
    assert path.read_bytes() == original_contents


def test_done_records_today_and_repeat_is_idempotent(tmp_path: Path, capsys) -> None:
    path = tmp_path / "habits.json"
    run_cli(["add", "Leer"], path)
    capsys.readouterr()

    assert run_cli(["done", "leer"], path) == 0
    assert "marcado como hecho hoy" in capsys.readouterr().out
    assert run_cli(["done", "LEER"], path) == 0
    assert "ya estaba marcado hoy" in capsys.readouterr().out
    assert run_cli(["list"], path) == 0
    assert "1 día" in capsys.readouterr().out


def test_done_unknown_habit_reports_list_hint(tmp_path: Path, capsys) -> None:
    path = tmp_path / "habits.json"

    assert run_cli(["done", "Desconocido"], path) == 1

    assert "python -m habits list" in capsys.readouterr().err
    assert not path.exists()


def test_list_empty_invites_user_to_create_first_habit(
    tmp_path: Path, capsys
) -> None:
    assert run_cli(["list"], tmp_path / "habits.json") == 0
    assert "Crea tu primer hábito" in capsys.readouterr().out


def test_list_displays_sorted_habits_and_streaks(tmp_path: Path, capsys) -> None:
    path = tmp_path / "habits.json"
    for name in ["Zeta", "beta", "Alpha", "Ayer"]:
        assert run_cli(["add", name], path) == 0
        capsys.readouterr()
    for name in ["Zeta", "beta", "Alpha"]:
        assert run_cli(["done", name], path) == 0
        capsys.readouterr()

    assert run_cli(["list"], path) == 0
    output = capsys.readouterr().out
    assert output.index("Alpha") < output.index("beta") < output.index("Zeta")
    assert output.index("beta") < output.index("Ayer")
    assert output.count("1 día") == 3
    assert "Ayer: 0 días" in output


@pytest.mark.parametrize(
    "arguments", [[], ["unknown"], ["add"], ["done"], ["list", "extra"]]
)
def test_invalid_invocation_displays_usage_in_spanish_and_returns_two(
    tmp_path: Path, capsys, arguments: list[str]
) -> None:
    result = run_cli(arguments, tmp_path / "habits.json")

    assert result == 2
    captured = capsys.readouterr()
    assert "uso:" in captured.err
    assert "argumentos" in captured.err.lower()


def test_corrupt_json_returns_error_and_preserves_file(
    tmp_path: Path, capsys
) -> None:
    path = tmp_path / "habits.json"
    original_contents = b'{"habits": nope}'
    path.write_bytes(original_contents)

    assert run_cli(["list"], path) == 1

    assert "JSON válido" in capsys.readouterr().err
    assert path.read_bytes() == original_contents


def test_read_error_returns_error_without_success_message(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    def fail_read(_path: Path):
        raise OSError("denegado")

    monkeypatch.setattr("habits.cli.load_data", fail_read)

    assert run_cli(["list"], tmp_path / "habits.json") == 1

    captured = capsys.readouterr()
    assert "No se pudo leer" in captured.err
    assert captured.out == ""


def test_write_error_returns_error_without_success_message(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    def fail_write(_path: Path, _data):
        raise OSError("sin espacio")

    monkeypatch.setattr("habits.cli.save_data", fail_write)

    assert run_cli(["add", "Leer"], tmp_path / "habits.json") == 1

    captured = capsys.readouterr()
    assert "No se pudo guardar" in captured.err
    assert "Hábito creado" not in captured.out


def test_default_storage_tracks_working_directory_and_preserves_legacy_home_file(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    first_directory = tmp_path / "first"
    second_directory = tmp_path / "second"
    fake_home = tmp_path / "home"
    first_directory.mkdir()
    second_directory.mkdir()
    fake_home.mkdir()
    legacy_path = fake_home / ".habits-cli.json"
    legacy_contents = (
        b'{"habits": [{"name": "Legacy", "completed_dates": []}]}\n'
    )
    legacy_path.write_bytes(legacy_contents)

    monkeypatch.setattr(Path, "home", lambda: fake_home)
    monkeypatch.chdir(first_directory)
    assert main(["add", "Primer directorio"]) == 0
    capsys.readouterr()
    first_contents = (first_directory / ".habits-cli.json").read_bytes()

    monkeypatch.chdir(second_directory)
    assert main(["list"]) == 0
    assert "Crea tu primer hábito" in capsys.readouterr().out
    assert main(["add", "Segundo directorio"]) == 0
    capsys.readouterr()

    assert (second_directory / ".habits-cli.json").exists()
    assert (first_directory / ".habits-cli.json").read_bytes() == first_contents
    assert legacy_path.read_bytes() == legacy_contents


def test_data_access_error_uses_current_directory_and_never_falls_back_to_home(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    working_directory = tmp_path / "working"
    fake_home = tmp_path / "home"
    working_directory.mkdir()
    fake_home.mkdir()
    monkeypatch.chdir(working_directory)
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    captured_paths: list[Path] = []

    def fail_read(path: Path):
        captured_paths.append(path)
        raise PermissionError("acceso denegado")

    monkeypatch.setattr("habits.cli.load_data", fail_read)

    assert main(["list"]) == 1

    captured = capsys.readouterr()
    assert captured_paths == [working_directory / ".habits-cli.json"]
    assert "No se pudo leer" in captured.err
    assert captured.out == ""
    assert not (fake_home / ".habits-cli.json").exists()


def test_data_write_error_uses_current_directory_and_returns_code_one(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    working_directory = tmp_path / "working"
    fake_home = tmp_path / "home"
    working_directory.mkdir()
    fake_home.mkdir()
    monkeypatch.chdir(working_directory)
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    save_paths: list[Path] = []

    def fail_write(path: Path, _data) -> None:
        save_paths.append(path)
        raise PermissionError("acceso denegado")

    monkeypatch.setattr("habits.cli.save_data", fail_write)

    assert main(["add", "No guardado"]) == 1

    captured = capsys.readouterr()
    assert save_paths == [working_directory / ".habits-cli.json"]
    assert "No se pudo guardar" in captured.err
    assert "Hábito creado" not in captured.out
    assert not (fake_home / ".habits-cli.json").exists()

import json
from pathlib import Path

import pytest

from habits.storage import InvalidDataError, get_data_path, load_data, save_data


def test_load_missing_file_returns_empty_collection(tmp_path: Path) -> None:
    assert load_data(tmp_path / "habits.json") == {"habits": []}


def test_default_data_path_is_resolved_from_current_working_directory(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    assert get_data_path() == tmp_path / ".habits-cli.json"


def test_save_writes_human_readable_utf8_json_and_loads_without_loss(
    tmp_path: Path,
) -> None:
    path = tmp_path / "habits.json"
    data = {
        "habits": [
            {
                "name": "Repasar química",
                "completed_dates": ["2026-10-08", "2026-10-09"],
            }
        ]
    }

    save_data(path, data)

    contents = path.read_text(encoding="utf-8")
    assert contents == json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    assert load_data(path) == data


def test_load_invalid_json_raises_clear_error_without_modifying_file(
    tmp_path: Path,
) -> None:
    path = tmp_path / "habits.json"
    original_contents = b'{"habits": [invalid]}'
    path.write_bytes(original_contents)

    with pytest.raises(InvalidDataError) as error:
        load_data(path)

    assert "El archivo de datos no contiene JSON válido" in str(error.value)
    assert error.value.exit_code == 1
    assert path.read_bytes() == original_contents


@pytest.mark.parametrize(
    "original_contents",
    [
        b"\xff\xfe",
        b'{"habits": "not-a-list"}',
        b'{"habits": [{"name": "Leer", "completed_dates": ["not-a-date"]}]}',
    ],
)
def test_load_invalid_data_shape_or_encoding_preserves_file(
    tmp_path: Path, original_contents: bytes
) -> None:
    path = tmp_path / "habits.json"
    path.write_bytes(original_contents)

    with pytest.raises(InvalidDataError):
        load_data(path)

    assert path.read_bytes() == original_contents


def test_failed_atomic_replace_keeps_previous_file_contents(
    tmp_path: Path, monkeypatch
) -> None:
    import habits.storage as storage

    path = tmp_path / "habits.json"
    original_contents = b'{"habits": []}\n'
    path.write_bytes(original_contents)

    def fail_replace(_source: Path, _destination: Path) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(storage.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        save_data(path, {"habits": []})

    assert path.read_bytes() == original_contents
    assert list(tmp_path.iterdir()) == [path]

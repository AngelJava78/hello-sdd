import subprocess
import sys
from pathlib import Path


def test_module_entry_point_displays_help_in_spanish() -> None:
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "habits", "--help"],
        capture_output=True,
        check=False,
        cwd=project_root,
        text=True,
    )

    assert result.returncode == 0
    assert "Gestiona tus hábitos de estudio" in result.stdout
    assert "uso:" in result.stdout
    assert "usage:" not in result.stdout
    assert "muestra esta ayuda y termina" in result.stdout

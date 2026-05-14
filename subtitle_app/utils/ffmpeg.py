import os
import sys
from pathlib import Path


def _find_binary(name: str) -> str:
    """Locate a binary: PyInstaller bundle -> project bin/ -> env var -> PATH."""
    if getattr(sys, "frozen", False):
        bundled = Path(sys._MEIPASS) / "bin" / name
        if bundled.exists():
            return str(bundled)

    # Check project-level bin/ directory (supports both .exe and non-.exe)
    project_bin = Path(__file__).resolve().parent.parent.parent / "bin"
    for candidate in (project_bin / name, project_bin / f"{name}.exe"):
        if candidate.exists():
            return str(candidate)

    env_key = f"{name.upper()}_PATH"
    if os.environ.get(env_key):
        return os.environ[env_key]

    return name


def get_ffmpeg_path() -> str:
    return _find_binary("ffmpeg")


def get_ffprobe_path() -> str:
    return _find_binary("ffprobe")

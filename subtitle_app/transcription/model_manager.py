import sys
from pathlib import Path


REPO_ID = "Systran/faster-whisper"


def get_model_path(model_size: str) -> str:
    """Find a model directory. Checks next to exe, then dev location."""
    local = _get_local_model_dir(model_size)
    if local and _model_files_present(local):
        return local

    raise FileNotFoundError(
        f"Model '{model_size}' not found. "
        "Please download the model and place it in the 'models' folder "
        "next to the application."
    )


def _get_local_model_dir(model_size: str) -> str | None:
    base = _get_models_base_dir()
    if base is None:
        return None
    return str(base / model_size)


def _get_models_base_dir() -> Path:
    """Determine where to look for model files."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "models"
    return Path(__file__).resolve().parent.parent.parent / "models"


def _model_files_present(model_dir: str) -> bool:
    return Path(model_dir, "model.bin").exists() and Path(model_dir, "config.json").exists()


def is_model_cached(model_size: str) -> bool:
    local = _get_local_model_dir(model_size)
    return local is not None and _model_files_present(local)


def get_cached_models() -> list[str]:
    from subtitle_app.utils.config import SUPPORTED_MODELS
    return [m for m in SUPPORTED_MODELS if is_model_cached(m)]

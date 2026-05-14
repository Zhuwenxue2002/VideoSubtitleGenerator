"""
Download Whisper models for Video Subtitle Generator.

Usage:
    python download_models.py small
    python download_models.py tiny base small medium

Models will be placed in the 'models/' directory, ready to use
alongside the application.

For gated models (large-v3), first accept terms at:
    https://huggingface.co/Systran/faster-whisper-large-v3
Then set HF_TOKEN:
    Windows: set HF_TOKEN=hf_your_token
    Linux:   export HF_TOKEN=hf_your_token
"""

import os
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

# large-v3 is in its own repo; others are in Systran/faster-whisper
REPO_MAP: dict[str, str] = {
    "large-v3": "Systran/faster-whisper-large-v3",
}
DEFAULT_REPO = "Systran/faster-whisper"

FILES = ["config.json", "model.bin", "tokenizer.json", "vocabulary.txt"]
# large-v3 uses vocabulary.json instead of vocabulary.txt
EXTRA_FILES: dict[str, list[str]] = {
    "large-v3": ["vocabulary.json", "preprocessor_config.json"],
}

HF_TOKEN = os.environ.get("HF_TOKEN")


def get_files(model_size: str) -> list[str]:
    files = list(FILES)
    if model_size in EXTRA_FILES:
        # Replace vocabulary.txt with vocabulary.json for large-v3
        if "vocabulary.json" in EXTRA_FILES[model_size]:
            files = [f for f in files if f != "vocabulary.txt"]
        files.extend(EXTRA_FILES[model_size])
    return files


def download_model(model_size: str) -> None:
    from huggingface_hub import hf_hub_download

    repo_id = REPO_MAP.get(model_size, DEFAULT_REPO)
    dest = MODELS_DIR / model_size
    dest.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {model_size} from {repo_id}...")
    for filename in get_files(model_size):
        print(f"  {filename}...")
        downloaded = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            token=HF_TOKEN,
            resume=True,
        )
        path = Path(downloaded)
        target = dest / filename
        if path != target:
            shutil.copy2(path, target)
    print(f"  -> {dest}")
    print()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python download_models.py <model_size> [model_size ...]")
        print("  Available: tiny, base, small, medium, large-v3")
        print()
        print("  Set HF_TOKEN if using gated models (large-v3):")
        print("    Windows: set HF_TOKEN=your_token")
        print("    Linux:   export HF_TOKEN=your_token")
        sys.exit(1)

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("Error: huggingface_hub not installed.")
        print("Run: pip install huggingface_hub")
        sys.exit(1)

    for size in sys.argv[1:]:
        download_model(size)

    print("Done!")
    print(f"Models saved to: {MODELS_DIR}")
    print("Copy the 'models' folder next to the exe when distributing.")


if __name__ == "__main__":
    main()

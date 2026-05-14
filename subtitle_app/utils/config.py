from pathlib import Path
import os

APP_NAME = "VideoSubtitleGenerator"

HF_HOME = os.environ.get("HF_HOME", str(Path.home() / ".cache" / "huggingface"))

DEFAULT_MODEL = "small"

SUPPORTED_MODELS = ["tiny", "base", "small", "medium", "large-v3"]

SUPPORTED_LANGUAGES = {
    "auto": "自动检测",
    "en": "English",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "ru": "Русский",
    "pt": "Português",
    "it": "Italiano",
    "th": "ไทย",
    "vi": "Tiếng Việt",
    "ar": "العربية",
    "id": "Bahasa Indonesia",
    "nl": "Nederlands",
    "pl": "Polski",
    "tr": "Türkçe",
}

# HuggingFace mirror for users in mainland China
HF_ENDPOINT = os.environ.get("HF_ENDPOINT", "https://huggingface.co")

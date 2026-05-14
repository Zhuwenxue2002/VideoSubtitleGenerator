from dataclasses import dataclass
from pathlib import Path

from subtitle_app.transcription.model_manager import get_model_path


@dataclass
class Segment:
    start: float
    end: float
    text: str


class TranscriptionError(Exception):
    pass


def transcribe(
    audio_path: str,
    model_size: str = "base",
    language: str | None = None,
    progress_callback=None,
    cancel_event=None,
) -> list[Segment]:
    """
    Transcribe a WAV audio file using faster-whisper.

    Args:
        audio_path: Path to 16kHz mono WAV file.
        model_size: One of tiny, base, small, medium.
        language: Language code (en, zh) or None for auto-detect.
        progress_callback: Called with (current_segment, total_duration) for progress.
        cancel_event: threading.Event to signal cancellation.

    Returns:
        List of Segment objects with start, end time and text.
    """
    if not Path(audio_path).exists():
        raise TranscriptionError(f"Audio file not found: {audio_path}")

    from faster_whisper import WhisperModel

    model_path = get_model_path(model_size)

    model = WhisperModel(model_path, device="cpu", compute_type="int8")

    segments_result, info = model.transcribe(
        audio_path,
        language=language,
        beam_size=5,
        vad_filter=True,
    )

    duration = info.duration
    segments = []

    for seg in segments_result:
        if cancel_event and cancel_event.is_set():
            break
        segments.append(Segment(start=seg.start, end=seg.end, text=seg.text.strip()))
        if progress_callback:
            progress_callback(seg.end, duration)

    return segments

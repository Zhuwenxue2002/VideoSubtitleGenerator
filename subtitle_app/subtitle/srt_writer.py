from pathlib import Path

from subtitle_app.transcription.engine import Segment


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def segments_to_srt(segments: list[Segment], output_path: str) -> Path:
    """
    Write a list of segments to an SRT subtitle file.

    Returns the path to the SRT file.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with open(out, "w", encoding="utf-8-sig") as f:
        for i, seg in enumerate(segments, 1):
            start = _format_timestamp(seg.start)
            end = _format_timestamp(seg.end)
            f.write(f"{i}\n{start} --> {end}\n{seg.text}\n\n")

    return out

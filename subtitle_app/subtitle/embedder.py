import subprocess
from pathlib import Path

from subtitle_app.utils.ffmpeg import get_ffmpeg_path


class EmbeddingError(Exception):
    pass


def embed_subtitles(video_path: str, srt_path: str, output_path: str | None = None) -> str:
    """
    Soft-embed SRT subtitles into a video as a subtitle stream.

    Returns the path to the output video.
    Raises EmbeddingError on failure.
    """
    video = Path(video_path)
    srt = Path(srt_path)

    if not srt.exists():
        raise EmbeddingError(f"Subtitle file not found: {srt_path}")

    if output_path:
        out = Path(output_path)
    else:
        out = video.parent / f"{video.stem}_subtitled{video.suffix}"

    cmd = [
        get_ffmpeg_path(),
        "-i", str(video),
        "-i", str(srt),
        "-c", "copy",
    ]

    # MKV supports SRT natively; MP4/etc need mov_text codec
    if video.suffix.lower() != ".mkv":
        cmd.extend(["-c:s", "mov_text"])

    cmd.extend(["-y", str(out)])

    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        raise EmbeddingError(
            f"FFmpeg failed to embed subtitles:\n{result.stderr}"
        )

    return str(out)

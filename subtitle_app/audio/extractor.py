import subprocess
from pathlib import Path

from subtitle_app.utils.ffmpeg import get_ffmpeg_path


class AudioExtractionError(Exception):
    pass


def extract_audio(video_path: str, output_dir: str | None = None) -> Path:
    """
    Extract audio from a video file as 16kHz mono WAV.

    Returns the path to the extracted WAV file.
    Raises AudioExtractionError on failure.
    """
    video = Path(video_path)
    if not video.exists():
        raise AudioExtractionError(f"Video file not found: {video_path}")

    out_dir = Path(output_dir) if output_dir else video.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    wav_path = out_dir / f"{video.stem}_audio.wav"

    cmd = [
        get_ffmpeg_path(),
        "-y",
        "-i", str(video),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(wav_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        raise AudioExtractionError(
            f"FFmpeg failed to extract audio from {video_path}:\n{result.stderr}"
        )

    return wav_path

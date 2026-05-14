import argparse
import sys
from pathlib import Path


def run_cli(video_path: str, model: str, language: str | None, output: str | None, embed: bool = False) -> None:
    """Command-line pipeline: extract audio -> transcribe -> write SRT -> optional embed."""
    from subtitle_app.audio.extractor import AudioExtractionError, extract_audio
    from subtitle_app.subtitle.srt_writer import segments_to_srt
    from subtitle_app.transcription.engine import TranscriptionError, transcribe

    video = Path(video_path)
    if not video.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    srt_path = Path(output) if output else video.with_suffix(".srt")

    print(f"Video: {video}")
    print(f"Model: {model}")
    print(f"Language: {language or 'auto-detect'}")
    print(f"Output: {srt_path}")
    print()

    print("Extracting audio...")
    try:
        wav = extract_audio(video_path)
        print(f"  -> {wav}")
    except AudioExtractionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("Transcribing (this may take a while)...")

    def progress(current: float, total: float) -> None:
        pct = min(current / total * 100, 100) if total > 0 else 0
        print(f"\r  Progress: {pct:.0f}%", end="", flush=True)

    try:
        segments = transcribe(
            str(wav),
            model_size=model,
            language=language,
            progress_callback=progress,
        )
        print()
        print(f"  -> {len(segments)} segments")
    except TranscriptionError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

    print("Writing SRT...")
    out = segments_to_srt(segments, str(srt_path))
    print(f"  -> {out}")

    if embed:
        from subtitle_app.subtitle.embedder import EmbeddingError, embed_subtitles
        print("Embedding subtitles into video...")
        try:
            embedded = embed_subtitles(video_path, str(out))
            print(f"  -> {embedded}")
        except EmbeddingError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Clean up temporary WAV
    wav.unlink(missing_ok=True)

    print()
    print("Done!")


def main() -> None:
    from subtitle_app.utils.config import DEFAULT_MODEL, SUPPORTED_LANGUAGES, SUPPORTED_MODELS

    parser = argparse.ArgumentParser(
        description="Video Subtitle Generator - Generate SRT subtitles from video using Whisper"
    )
    parser.add_argument(
        "--cli",
        type=str,
        metavar="VIDEO",
        help="Run in CLI mode with the given video file path",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        choices=SUPPORTED_MODELS,
        help=f"Whisper model size (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        choices=list(SUPPORTED_LANGUAGES.keys()),
        help="Language code: en (English), zh (Chinese), or auto (default)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output SRT file path (default: same as video with .srt extension)",
    )
    parser.add_argument(
        "--embed",
        action="store_true",
        help="Embed generated subtitles into the video as a subtitle stream",
    )

    args = parser.parse_args()

    if args.cli:
        lang = None if args.language == "auto" else args.language
        run_cli(args.cli, args.model, lang, args.output, embed=args.embed)
    else:
        from subtitle_app.gui.main_window import launch_gui
        launch_gui()


if __name__ == "__main__":
    main()

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from subtitle_app.transcription.model_manager import get_cached_models
from subtitle_app.utils.config import DEFAULT_MODEL, SUPPORTED_LANGUAGES

LANGUAGE_OPTIONS = [("自动检测", None)] + [
    (f"{code} - {name}", code if code != "auto" else None)
    for code, name in SUPPORTED_LANGUAGES.items()
    if code != "auto"
]


def launch_gui() -> None:
    root = tk.Tk()
    root.title("视频字幕生成器")
    root.geometry("600x420")
    root.resizable(False, False)

    app = SubtitleApp(root)
    app.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    root.mainloop()


class SubtitleApp(ttk.Frame):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.parent = parent
        self._cancel_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._wav_path: Path | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        # --- Video file selection ---
        file_frame = ttk.LabelFrame(self, text="视频文件", padding=8)
        file_frame.pack(fill=tk.X, pady=(0, 8))

        self.video_path_var = tk.StringVar()
        video_entry = ttk.Entry(file_frame, textvariable=self.video_path_var)
        video_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Button(file_frame, text="浏览...", command=self._browse_video).pack(side=tk.RIGHT)

        # --- Settings row ---
        settings_frame = ttk.Frame(self)
        settings_frame.pack(fill=tk.X, pady=(0, 8))

        # Model selection - shows only locally available models
        ttk.Label(settings_frame, text="模型：").pack(side=tk.LEFT)
        available = get_cached_models()
        if not available:
            available = ["(无可用模型)"]
        self.model_var = tk.StringVar(value=available[0])
        model_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.model_var,
            values=available,
            state="readonly",
            width=14,
        )
        model_combo.pack(side=tk.LEFT, padx=(4, 16))

        # Language selection
        ttk.Label(settings_frame, text="语言：").pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value="自动检测")
        lang_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.language_var,
            values=[label for label, _ in LANGUAGE_OPTIONS],
            state="readonly",
            width=12,
        )
        lang_combo.pack(side=tk.LEFT, padx=(4, 16))

        # Output path
        ttk.Label(settings_frame, text="输出：").pack(side=tk.LEFT)
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(settings_frame, textvariable=self.output_var, width=20)
        output_entry.pack(side=tk.LEFT, padx=(4, 0))

        # --- Embed checkbox ---
        self.embed_var = tk.BooleanVar(value=False)
        embed_cb = ttk.Checkbutton(
            self, text="内嵌字幕到视频", variable=self.embed_var
        )
        embed_cb.pack(anchor=tk.W, pady=(0, 8))

        # --- Progress area ---
        self.progress_frame = ttk.LabelFrame(self, text="进度", padding=8)

        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self.progress_frame, textvariable=self.status_var)
        self.status_label.pack(anchor=tk.W, pady=(0, 4))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            mode="determinate",
        )
        self.progress_bar.pack(fill=tk.X)

        # --- Buttons ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=(12, 0))

        self.generate_btn = ttk.Button(
            btn_frame, text="生成字幕", command=self._start
        )
        self.generate_btn.pack(side=tk.LEFT)

        self.cancel_btn = ttk.Button(
            btn_frame, text="取消", command=self._cancel, state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=(8, 0))

    def _browse_video(self) -> None:
        path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频/音频文件", "*.mp4 *.mkv *.avi *.mov *.flv *.wmv *.webm *.mp3 *.m4a *.wav *.aac *.flac *.ogg"),
                ("所有文件", "*.*"),
            ],
        )
        if path:
            self.video_path_var.set(path)
            if not self.output_var.get():
                self.output_var.set(str(Path(path).with_suffix(".srt")))

    def _get_language_code(self) -> str | None:
        label = self.language_var.get()
        for lbl, code in LANGUAGE_OPTIONS:
            if lbl == label:
                return code
        return None

    def _start(self) -> None:
        video_path = self.video_path_var.get()
        if not video_path:
            messagebox.showwarning("未选择视频", "请先选择一个视频文件。")
            return
        if not Path(video_path).exists():
            messagebox.showerror("文件未找到", f"视频文件未找到：\n{video_path}")
            return

        self._cancel_event.clear()
        self._set_ui_state(running=True)
        self._show_progress()

        model = self.model_var.get()
        if model == "(无可用模型)":
            messagebox.showwarning(
                "模型未找到",
                "未找到 Whisper 模型文件。\n\n"
                "请将模型文件夹放在程序所在目录的 models/ 下，例如：\n"
                "models/small/model.bin\n"
                "models/small/config.json\n\n"
                "支持: tiny, base, small, medium",
            )
            self._set_ui_state(running=False)
            return
        language = self._get_language_code()

        self._worker = threading.Thread(
            target=self._run_pipeline,
            args=(video_path, model, language),
            daemon=True,
        )
        self._worker.start()

    def _cancel(self) -> None:
        self._cancel_event.set()
        self.status_var.set("正在取消...")

    def _run_pipeline(self, video_path: str, model: str, language: str | None) -> None:
        from subtitle_app.audio.extractor import AudioExtractionError, extract_audio
        from subtitle_app.subtitle.srt_writer import segments_to_srt
        from subtitle_app.transcription.engine import TranscriptionError, transcribe

        try:
            self._update_status("正在提取音频...")
            self._update_progress(0)

            wav = extract_audio(video_path)
            self._wav_path = wav

            if self._cancel_event.is_set():
                return self._on_done(cancelled=True)

            self._update_status("正在转录音频...")

            def progress(current: float, total: float) -> None:
                if total > 0:
                    self._update_progress(current / total * 100)

            segments = transcribe(
                str(wav),
                model_size=model,
                language=language,
                progress_callback=progress,
                cancel_event=self._cancel_event,
            )

            if self._cancel_event.is_set():
                return self._on_done(cancelled=True)

            self._update_status("正在写入字幕文件...")
            self._update_progress(100)

            output = self.output_var.get() or str(Path(video_path).with_suffix(".srt"))
            out = segments_to_srt(segments, output)

            self._update_status(f"完成！已保存至：{out}")

            if self.embed_var.get():
                self._update_status("正在内嵌字幕到视频...")
                from subtitle_app.subtitle.embedder import EmbeddingError, embed_subtitles
                try:
                    embedded = embed_subtitles(video_path, str(out))
                    self._update_status(f"完成！字幕视频：{embedded}")
                except EmbeddingError as e:
                    self._update_status(f"内嵌字幕失败：{e}")

        except AudioExtractionError as e:
            self._update_status(f"提取音频时出错：{e}")
        except TranscriptionError as e:
            self._update_status(f"转录音频时出错：{e}")
        except Exception as e:
            self._update_status(f"意外错误：{e}")
        finally:
            self._on_done()

    def _update_status(self, msg: str) -> None:
        self.parent.after(0, lambda: self.status_var.set(msg))

    def _update_progress(self, value: float) -> None:
        self.parent.after(0, lambda: self.progress_var.set(value))

    def _on_done(self, cancelled: bool = False) -> None:
        self.parent.after(0, lambda: self._set_ui_state(running=False))

        # Clean up temp WAV
        if self._wav_path and self._wav_path.exists():
            self._wav_path.unlink(missing_ok=True)

        if cancelled:
            self._update_status("已取消。")

    def _show_progress(self) -> None:
        self.progress_frame.pack(fill=tk.X, pady=(0, 8))

    def _set_ui_state(self, running: bool) -> None:
        self.generate_btn.config(state=tk.DISABLED if running else tk.NORMAL)
        self.cancel_btn.config(state=tk.NORMAL if running else tk.DISABLED)
        self.progress_var.set(0)

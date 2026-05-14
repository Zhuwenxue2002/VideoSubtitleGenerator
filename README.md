# Video Subtitle Generator

基于 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 的视频字幕生成工具，支持图形界面和命令行两种使用方式。

> 已编译好的 Windows 版本可在 [Releases](https://github.com/Zhuwenxue2002/VideoSubtitleGenerator/releases) 页面下载，解压即可使用，无需安装 Python 环境。

## 功能特点

- 使用 Whisper 模型进行语音转文字（支持 tiny / base / small / medium / large-v3）
- 支持多种语言（中文、英语、日语、韩语、法语、德语等）
- 自动检测语言或手动指定
- 支持将字幕内嵌到视频中作为字幕流
- 输出标准 SRT 格式字幕文件
- 提供图形界面（Tkinter）和命令行两种模式
- 支持 Windows 打包为独立 exe

## 环境要求

- Python 3.10+
- ffmpeg（用于音频提取）
- 建议 8GB+ 内存（small 模型约需 4GB，large 模型需要更多）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 ffmpeg

**Windows**: 从 [gyan.dev ffmpeg builds](https://www.gyan.dev/ffmpeg/builds/) 下载 `ffmpeg-release-essentials.zip`，解压后将 `bin/ffmpeg.exe` 和 `bin/ffprobe.exe` 放入项目 `bin/` 目录。

**Linux**:
```bash
sudo apt install ffmpeg
```

### 3. 下载模型

```bash
# 下载 small 模型（推荐，平衡速度与准确度）
python download_models.py small

# 下载多个模型
python download_models.py tiny base small medium

# 下载 large-v3（需先设置 HF_TOKEN）
set HF_TOKEN=hf_your_token
python download_models.py large-v3
```

模型文件会保存在 `models/` 目录下，目录结构如下：

```
models/
  small/
    config.json
    model.bin
    tokenizer.json
    vocabulary.txt
```

> **注意**：large-v3 是受限模型，需要先访问 https://huggingface.co/Systran/faster-whisper-large-v3 同意协议，然后在 [Settings / Access Tokens](https://huggingface.co/settings/tokens) 创建 token。

### 4. 运行

**图形界面模式**：
```bash
python main.py
```

**命令行模式**：
```bash
python main.py --cli "视频文件.mp4"
```

指定语言和模型：
```bash
python main.py --cli "视频文件.mp4" --model small --language zh
```

生成字幕并内嵌到视频：
```bash
python main.py --cli "视频文件.mp4" --model small --embed
```

## 使用说明

### GUI 界面

启动后界面包含：

1. **视频文件选择** — 点击"浏览"选择视频文件
2. **模型选择** — 选择已下载的 Whisper 模型（只有 models/ 目录中存在的模型才会显示）
3. **语言选择** — 选择输出语言或自动检测
4. **输出路径** — 指定 SRT 文件保存位置（默认与视频同名）
5. **内嵌字幕** — 勾选后将字幕流嵌入视频文件
6. **进度显示** — 实时显示处理进度

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--cli VIDEO` | 指定视频文件路径，启用命令行模式 |
| `--model MODEL` | 模型大小：tiny / base / small / medium / large-v3（默认：small） |
| `--language LANG` | 语言代码：en / zh / ja / ko / auto 等（默认：auto） |
| `--output PATH` | 输出 SRT 文件路径 |
| `--embed` | 内嵌字幕到视频 |

## 打包为 Windows exe

使用 PyInstaller 打包为单文件 exe：

```bash
pip install pyinstaller
pyinstaller build.spec
```

打包后的 exe 在 `dist/VideoSubtitleGenerator.exe`。

**使用打包后的 exe 需要：**

1. 将 `models/` 目录复制到 exe 同目录下
2. 将 `ffmpeg.exe` 和 `ffprobe.exe` 放入 exe 同目录下的 `bin/` 文件夹

目录结构：
```
VideoSubtitleGenerator.exe
bin/
  ffmpeg.exe
  ffprobe.exe
models/
  small/
    model.bin
    config.json
    ...
```

CLI 模式运行：
```bash
VideoSubtitleGenerator.exe --cli "视频文件.mp4"
```

## 项目结构

```
my-python-project/
├── main.py                     # 主入口（GUI + CLI）
├── build.spec                  # PyInstaller 打包配置
├── download_models.py          # 模型下载脚本
├── requirements.txt            # Python 依赖
├── subtitle_app/
│   ├── audio/
│   │   └── extractor.py        # 音频提取（ffmpeg）
│   ├── gui/
│   │   └── main_window.py      # Tkinter 图形界面
│   ├── subtitle/
│   │   ├── embedder.py         # 字幕内嵌
│   │   └── srt_writer.py       # SRT 文件生成
│   ├── transcription/
│   │   ├── engine.py           # Whisper 转录引擎
│   │   └── model_manager.py    # 模型路径管理
│   └── utils/
│       ├── config.py           # 配置常量
│       └── ffmpeg.py           # ffmpeg 路径查找
├── bin/                        # ffmpeg 可执行文件
├── models/                     # Whisper 模型文件
└── logs/                       # 运行日志
```

## 常见问题

### Q: 提示 `[WinError 2]` 系统找不到指定的文件
确保 `bin/` 目录下有 `ffmpeg.exe` 和 `ffprobe.exe`，或者通过环境变量 `FFMPEG_PATH` 和 `FFPROBE_PATH` 指定路径。

### Q: 提示模型未找到
确保模型文件在正确的位置。开发环境下在 `models/` 目录，打包后在 exe 同级的 `models/` 目录。可通过 `python download_models.py small` 下载。

### Q: 打包后运行提示 `NoSuchFile` / `silero_vad_v6.onnx`
使用 `build.spec` 重新打包，已包含必要的资源文件。

### Q: 字幕时间不准
试试 larger 模型（medium 或 large-v3），或在命令行中指定正确的语言。

## 许可证

MIT

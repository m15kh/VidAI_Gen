# Auto-Subtitle

A comprehensive tool for automatically generating and adding captions to videos with support for multiple languages including English, Persian, and Arabic. Perfect for content creators looking to make their videos more accessible across different language barriers.

## Features

- Automatic video transcription using Whisper models
- Translation between multiple languages (over 50 supported languages)
- YouTube video downloading with automatic processing
- Custom caption styling with font, color, and size options
- Word-by-word highlighting for better readability
- Special RTL (Right-to-Left) language support for Arabic and Persian
- Configurable shadow and stroke effects for subtitle visibility
- Pipeline-based processing for easy workflow automation
- Logo overlay capabilities with customizable positioning
- AI-powered title and description generation for content

## Installation

### Prerequisites

- Python 3.9+
- FFmpeg
- Internet connection for model downloads

### Setup

1. Clone the repository:
```bash
git clone https://github.com/m15kh/auto-subtitle.git
cd auto-subtitle
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Download the required models (will be done automatically on first run)

## Usage

### Basic Usage

Edit the configuration file at `config/config.yaml` with your video path or YouTube URL, then run:

```bash
python main.py
```

### Using the Pipeline

The pipeline allows you to process videos through downloading, transcription, and captioning in one step:

```bash
python -m scripts.src.pipeline
```

### Processing YouTube Videos

To download and process a YouTube video:

1. Set the video URL in `config.yaml`:
```yaml
video_path: "https://youtube.com/shorts/kJ23zVr3HkE?si=M1O4CTvycVwbnZwR"
subtitle_path: null  # Let the system generate subtitles
```

2. Run the pipeline script

### Processing Local Videos

To process a video you already have:

1. Set the video file path in `config.yaml`:
```yaml
video_path: "/path/to/your/video.mp4"
subtitle_path: null  # Let the system generate subtitles
```

2. Run the pipeline script

## Configuration

Configuration is done through the `config/config.yaml` file:

```yaml
# Main configuration
video_path: "https://youtube.com/shorts/kJ23zVr3HkE?si=M1O4CTvycVwbnZwR"
subtitle_path: null  # Set to a JSON file path to use existing subtitles
output_dir: "output"
debug_mode: True

# YouTube download settings
youtube:
  quality: "best"  # Options: "best", "worst", or format code
  ratio: "9:16"    # Common values: "16:9" (landscape), "9:16" (portrait/shorts)

  output:
    filename: null  # Auto-generated if null
    merge: true     # Merge all segments into single video

# Subtitle processing settings
process_subtitle:
  enabled: true
  model: "large"    # Choices: tiny, base, small, medium, large
  verbose: false
  task: "translate" # Choices: transcribe, translate
  language: "en"    # Source language (auto for automatic detection) 
  translate_to: 'fa_IR'  # Target language, null for no translation

# Video editor settings
video_editor:
  logo:
    enabled: false  # Enable/disable logo overlay
```

## Supported Languages

Auto-Subtitle supports over 50 languages including:

- English (en_XX)
- Persian/Farsi (fa_IR)
- Arabic (ar_AR)
- Chinese (zh_CN)
- German (de_DE)
- Spanish (es_XX)
- Russian (ru_RU)
- Korean (ko_KR)
- French (fr_XX)
- Japanese (ja_XX)
- Portuguese (pt_XX)
- Turkish (tr_TR)
- Hindi (hi_IN)
- Italian (it_IT)
- Dutch (nl_XX)
- and many more...

## Output Files

The system generates several files during processing:

1. **JSON subtitle file**: Contains time-aligned words and sentences
2. **WAV audio file**: Temporary extracted audio for processing
3. **Final video file**: Video with the captions burned in
4. **Content description file**: Optional AI-generated video titles and descriptions

## Customizing Captions

You can customize the appearance of captions by modifying parameters in the configuration or directly via function calls:

```python
captacity.add_captions(
    video_file=video_path,
    output_dir=output_dir_path,
    subtitle_path=subtitle_path,
    font="/path/to/your/font.ttf",
    font_size=50,
    font_color="white",
    stroke_width=2,
    stroke_color="black",
    shadow_strength=1.0,
    shadow_blur=0.8,
    highlight_current_word=True,
    word_highlight_color="blue",
    line_count=2,
    padding=50,
    print_info=True,
)
```

### Caption Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| font | Path to TTF font file | System default |
| font_size | Size of subtitle text | 50 |
| font_color | Color of subtitle text | "white" |
| stroke_width | Width of text outline | 2 |
| stroke_color | Color of text outline | "black" |
| shadow_strength | Intensity of drop shadow (0.0-1.0) | 1.0 |
| shadow_blur | Blur radius for shadow | 0.8 |
| highlight_current_word | Whether to highlight the current word | True |
| word_highlight_color | Color for highlighted words | "blue" |
| line_count | Maximum number of subtitle lines | 2 |
| padding | Bottom padding for subtitles | 50 |

## Project Structure

```
auto-subtitle/
├── config/                 # Configuration files
│   └── config.yaml         # Main configuration
├── data/                   # Input video files
├── output/                 # Generated subtitle and video files
├── scripts/
│   ├── models/
│   │   ├── captacity/      # Caption styling and rendering
│   │   ├── subtitle/       # Subtitle generation
│   │   └── youtube/        # YouTube video download functionality
│   └── src/
│       └── pipeline.py     # Main processing pipeline
├── main.py                 # Entry point for direct captioning
├── README.md               # This file
└── TODO                    # Future plans and development notes
```

## Arabic/Persian Text Support

The project includes special handling for Right-to-Left (RTL) languages:

- Arabic text reshaping
- Bidirectional text handling
- Special word order processing

## Roadmap

### Phase 1
- Support for short English videos with subtitles and logo addition

### Phase 2
- Support for Persian videos from YouTube with subtitles

### Phase 3
- Upgrade models from LLama2 to LLama3

### Phase 4
- Automatic upload to Instagram

### Phase 5
- Automatic upload to YouTube

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

[Include license information here]

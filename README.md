# Auto-Subtitle

A comprehensive tool for automatically generating and adding captions to videos with support for multiple languages including English, Persian, and Arabic.

## Features

- Automatic video transcription using Whisper models
- Custom caption styling with font, color, and size options
- Word-by-word highlighting for better readability
- Special RTL (Right-to-Left) language support for Arabic and Persian
- Configurable shadow and stroke effects for subtitle visibility
- Pipeline-based processing for easy workflow automation

## Installation

### Prerequisites

- Python 3.9+
- FFmpeg

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

## Usage

### Basic Usage

```bash
python main.py
```

### Using the Pipeline

The pipeline allows you to process videos through transcription and captioning in one step:

```bash
python -m scripts.src.pipeline
```

## Configuration

Configuration is done through the `config/config.yaml` file:

```yaml
video:
  # Path to video file or URL
  address: "/path/to/your/video.mp4"
  subtitle: "/path/to/subtitle/file.json"
  format: "mp4"
  
subtitle:
  model: "large"  # Options: base, small, medium, large
  
processing:
  debug_mode: false
  language: "en"  # Options: en, fa, ar, etc.
  quality: "medium"  # Options: low, medium, high

output:
  subtitle_format: "srt"
  
debug_mode: True
output_dir: /path/to/output
```

## Customizing Captions

You can customize the appearance of captions by modifying parameters in `main.py` or `pipeline.py`:

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

from moviepy.editor import VideoFileClip, CompositeVideoClip
import subprocess
import tempfile
import time
import os
import json
from . import segment_parser
from . import transcriber

# Add imports for Arabic text support
import arabic_reshaper
from bidi.algorithm import get_display
import re

from .text_drawer import (
    get_text_size_ex,
    create_text_ex,
    blur_text_clip,
    Word,
)

shadow_cache = {}
lines_cache = {}

# Function to detect and process Arabic text
def process_arabic_text(text):
    # Check if the text contains Arabic characters
    arabic_pattern = re.compile('[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    if arabic_pattern.search(text):
        # Reshape Arabic text
        reshaped_text = arabic_reshaper.reshape(text)
        # Handle bidirectional text
        bidi_text = get_display(reshaped_text)
        return bidi_text
    return text

# Modify the Word class to handle Arabic text
def create_word_objects(text, highlight_color=None):
    words = text.split()
    word_list = []
    for w in words:
        w = process_arabic_text(w)
        word_obj = Word(w)
        if highlight_color:
            word_obj.set_color(highlight_color)
        word_list.append(word_obj)
    return word_list

def fits_frame(line_count, font, font_size, stroke_width, frame_width):
    def fit_function(text):
        lines = calculate_lines(
            text,
            font,
            font_size,
            stroke_width,
            frame_width
        )
        return len(lines["lines"]) <= line_count
    return fit_function

def calculate_lines(text, font, font_size, stroke_width, frame_width):
    global lines_cache

    # Process Arabic text if needed
    processed_text = process_arabic_text(text)
    
    arg_hash = hash((processed_text, font, font_size, stroke_width, frame_width))

    if arg_hash in lines_cache:
        return lines_cache[arg_hash]

    lines = []

    line_to_draw = None
    line = ""
    words = processed_text.split()
    word_index = 0
    total_height = 0
    while word_index < len(words):
        word = words[word_index]
        line += word + " "
        text_size = get_text_size_ex(line.strip(), font, font_size, stroke_width)
        text_width = text_size[0]
        line_height = text_size[1]

        if text_width < frame_width:
            line_to_draw = {
                "text": line.strip(),
                "height": line_height,
            }
            word_index += 1
        else:
            if not line_to_draw:
                print(f"NOTICE: Word '{line.strip()}' is too long for the frame!")
                line_to_draw = {
                    "text": line.strip(),
                    "height": line_height,
                }
                word_index += 1

            lines.append(line_to_draw)
            total_height += line_height
            line_to_draw = None
            line = ""

    if line_to_draw:
        lines.append(line_to_draw)
        total_height += line_height

    data = {
        "lines": lines,
        "height": total_height,
    }

    lines_cache[arg_hash] = data

    return data

def ffmpeg(command):
    return subprocess.run(command, capture_output=True)

def create_shadow(text: str, font_size: int, font: str, blur_radius: float, opacity: float=1.0):
    global shadow_cache

    arg_hash = hash((text, font_size, font, blur_radius, opacity))

    if arg_hash in shadow_cache:
        return shadow_cache[arg_hash].copy()

    shadow = create_text_ex(text, font_size, "black", font, opacity=opacity)
    shadow = blur_text_clip(shadow, int(font_size*blur_radius))

    shadow_cache[arg_hash] = shadow.copy()

    return shadow

def get_font_path(font):
    if os.path.exists(font):
        return font

    dirname = os.path.dirname(__file__)
    font = os.path.join(dirname, "assets", "fonts", font)

    if not os.path.exists(font):
        raise FileNotFoundError(f"Font '{font}' not found")

    return font

def detect_local_whisper(print_info):
    try:
        import whisper
        use_local_whisper = True
        if print_info:
            print("Using local whisper model...")
    except ImportError:
        use_local_whisper = False
        if print_info:
            print("Using OpenAI Whisper API...")

    return use_local_whisper

def add_captions(
    video_file,
    output_file = "with_transcript.mp4",

    font = "Bangers-Regular.ttf",
    font_size = 130,
    font_color = "yellow",

    stroke_width = 3,
    stroke_color = "black",

    highlight_current_word = True,
    word_highlight_color = "red",

    line_count = 2,
    fit_function = None,

    padding = 50,
    position = ("center", "center"),
    shadow_strength = 1.0,
    shadow_blur = 0.1,
    print_info = False,
    initial_prompt = None,
    segments = None,

    use_local_whisper = "auto",
):
    _start_time = time.time()

    font = get_font_path(font)

    if print_info:
        print("Extracting audio...")

    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav").name
    ffmpeg([
        'ffmpeg',
        '-y',
        '-i', video_file,
        temp_audio_file
    ])

    if segments is None:
        if print_info:
            print("Transcribing audio...")

        if use_local_whisper == "auto":
            use_local_whisper = detect_local_whisper(print_info)

        if use_local_whisper:
            segments = transcriber.transcribe_locally(temp_audio_file, initial_prompt)
            print("-----------------------------")
            print(segments)
        else:
            segments = transcriber.transcribe_with_api(temp_audio_file, initial_prompt)

        if print_info:
            output_path = os.path.dirname(output_file)
            video_filename = os.path.splitext(os.path.basename(video_file))[0]
            subtitle_path = os.path.join(output_path, f"{video_filename}_subtitle.json")
            
            with open(subtitle_path, 'w') as json_file:
                json.dump(segments, json_file)
                

        with open('/home/rteam2/m15kh/auto-subtitle/test.json', 'r') as json_file:
            segments = json.load(json_file)
     
    if print_info:
        print("Generating video elements...")

    # Open the video file
    video = VideoFileClip(video_file)
    text_bbox_width = video.w-padding*2
    clips = [video]
    index = 0  # Define 'index' for tracking highlighted word

    captions = segment_parser.parse(
        segments=segments,
        fit_function=fit_function if fit_function else fits_frame(
            line_count,
            font,
            font_size,
            stroke_width,
            text_bbox_width,
        ),
    )

    for caption in captions:
        captions_to_draw = []
        if highlight_current_word:
            for i, word in enumerate(caption["words"]):
                if i+1 < len(caption["words"]):
                    end = caption["words"][i+1]["start"]
                else:
                    end = word["end"]

                captions_to_draw.append({
                    "text": process_arabic_text(caption["text"]),
                    "start": word["start"],
                    "end": end,
                })
        else:
            captions_to_draw.append({
                "text": process_arabic_text(caption["text"]),
                "start": caption["start"],
                "end": caption["end"]
            })

        for current_index, subcaption in enumerate(captions_to_draw):
            line_data = calculate_lines(subcaption["text"], font, font_size, stroke_width, text_bbox_width)

            # Check if we're dealing with Arabic text
            is_arabic = re.compile('[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+').search(subcaption["text"])
            
            lines_to_render = line_data["lines"]

            # Calculate total height
            line_total_height = sum(line["height"] for line in lines_to_render)
            text_y_offset = video.h // 2 - line_total_height // 2

            # Reverse so the first entry in the list goes at the top
            lines_to_render = lines_to_render[::-1]

            for line in lines_to_render:
                pos = ("center", text_y_offset)

                word_list = create_word_objects(
                    line["text"], 
                    word_highlight_color if highlight_current_word and index == current_index else None
                )
                index += len(line["text"].split())

                text = create_text_ex(
                    word_list,
                    font_size,
                    font_color,
                    font,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                )
                text = text.set_position(pos).set_start(subcaption["start"]).set_end(subcaption["end"])
                clips.append(text)

                text_y_offset += line["height"]

    end_time = time.time()
    generation_time = end_time - _start_time

    if print_info:
        print(f"Generated in {generation_time//60:02.0f}:{generation_time%60:02.0f} ({len(clips)} clips)")

    if print_info:
        print("Rendering video...")

    video_with_text = CompositeVideoClip(clips)

    video_with_text.write_videofile(
        filename=output_file,
        codec="libx264",
        fps=video.fps,
        logger="bar" if print_info else None,
    )

    end_time = time.time()
    total_time = end_time - _start_time
    render_time = total_time - generation_time

    if print_info:
        print(f"Generated in {generation_time//60:02.0f}:{generation_time%60:02.0f}")
        print(f"Rendered in {render_time//60:02.0f}:{render_time%60:02.0f}")
        print(f"Done in {total_time//60:02.0f}:{total_time%60:02.0f}")
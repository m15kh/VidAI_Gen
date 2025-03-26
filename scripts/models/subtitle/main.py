import sys
import yaml
import os
import warnings
from auto_subtitle_llama.utils import *
from auto_subtitle_llama.llama import *
from SmartAITool.core import cprint, bprint


def generate_subtitle(video_path, output_dir, model_name, language, translate_to, args):
    """
    Generate subtitles for video files
    
    Args:
        video_path (list): List of paths to video files
        output_dir_path (str): Output directory path
        model_name (str): Name of the model to use
        language (str): Language code
        translate_to (str): Target language for translation
        args (dict): Additional arguments
    """
    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"
    # if translate task used and language argument is set, then use it
    elif language != "auto":
        # Convert language code to Whisper format
        args["language"] = convert_language_code(language)
    
    print("Loading Whisper model")
    model = whisper.load_model(model_name)
    
    print("Extracting audio from video")
# Ensure video_path is a list for get_audio function
    video_paths = [video_path] if isinstance(video_path, str) else video_path
    audios = get_audio(video_paths)
    
    # Extract subtitle output directory from output_dir tuple
    _, _, subtitle_dir, _ = output_dir
    output_srt = True  # Enable SRT output
    
    print("Generating subtitles")
    pretty_subtitle, _ = get_subtitles( 
        audios, 
        output_dir,
        model,
        args, 
        translate_to=translate_to,
    )
    
    return pretty_subtitle



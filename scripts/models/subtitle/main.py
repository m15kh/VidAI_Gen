import sys
import yaml
import os
import warnings
from auto_subtitle_llama.utils import *
from auto_subtitle_llama.llama import *
from SmartAITool.core import cprint, bprint


def generate_subtitle(video_path, output_dir_path, model_name, language, translate_to, args):
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
    # Validate video paths
    if not video_path:
        cprint("Error: No video paths provided", "red")
        return

    # Ensure video_path is a list
    if not isinstance(video_path, list):
        video_path = [video_path]

    for path in video_path:
        if not os.path.exists(path):
            cprint(f"Error: Video file not found: {path}", "red")
            return

    # Create output directory for the first video
    video_filename = os.path.splitext(os.path.basename(video_path[0]))[0]
    video_output_dir = os.path.join(output_dir_path, video_filename, "video")
    os.makedirs(video_output_dir, exist_ok=True)

    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"
    # if translate task used and language argument is set, then use it
    elif language != "auto":
        # Convert language code to Whisper format
        args["language"] = convert_language_code(language)
    
    bprint("Loading Whisper model")
    model = whisper.load_model(model_name)
    
    bprint("Extracting audio from video")
    audios = get_audio(video_path)
    
    bprint("Generating subtitles")
    pretty_subtitle = get_subtitles( #if you wanna add subtitle to video with local model uncomment  a below code 
        audios, 
        output_dir_path, 
        model,
        args, 
        translate_to=translate_to,
        video_path=video_path[0]
    )
    
    return pretty_subtitle



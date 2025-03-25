import sys
import yaml
import os
import warnings
from auto_subtitle_llama.utils import *
from auto_subtitle_llama.llama import *
from SmartAITool.core import cprint, bprint


def generate_subtitle(download_video_path, output_dir_path, model_name, language, translate_to, args):
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
    if not download_video_path:
        cprint("Error: No video paths provided", "red")
        return

    # Ensure video_path is a list
    if not isinstance(download_video_path, list):
        download_video_path = [download_video_path]

    for path in download_video_path:
        if not os.path.exists(path):
            cprint(f"Error: Video file not found: {path}", "red")
            return


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
    audios = get_audio(download_video_path)
    
    print("Generating subtitles")
    pretty_subtitle = get_subtitles( #if you wanna add subtitle to video with local model uncomment  a below code 
        audios, 
        download_video_path[0], 
        model,
        args, 
        translate_to=translate_to,
    )
    
    return pretty_subtitle



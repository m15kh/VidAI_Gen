import yaml
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))) # Add the parent directory of the 'models' folder to the system path

from SmartAITool.core import cprint
from scripts.models.captacity import add_captions
from scripts.src.pipeline_subtitle import generate_subtitle


def load_yaml_config(file_path):
    #read the yaml file
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def main():
    # Load the configuration file
    config = load_yaml_config("/home/rteam2/m15kh/auto-subtitle/config/config.yaml")
    debugger = config['debug_mode']
    video_path = config["video_path"]
    subtitle_path = config["subtitle_path"]
    output_dir_path = config['output_dir']


    #CONFIG file for subtitle model
    model_name = config["process_subtitle"].get("model", "large")
    language = config["process_subtitle"].get("language", "auto")
    translate_to = config["process_subtitle"].get("translate_to", None)
    args = {
        "task": config["process_subtitle"].get("task", "transcribe"),
        "verbose": config["process_subtitle"].get("verbose", False),
        "language": None  # Default to None, will be set later if needed
    }
    
    if debugger:
        cprint("the debug-mode is: ON", "red")
    else:
        cprint("the debug-mode is: OFF", "green")


    if subtitle_path == None:
           cprint("loading subtitle model ...", "green")
           subtitle = generate_subtitle(video_path, output_dir_path, model_name, language, translate_to, args)

    else:
        cprint("subtitle path is provided", "red")
        with open(subtitle_path, 'r') as file:
            subtitle = json.load(file)
            
            
            
    cprint("editing video ...", "yellow")
    add_captions(
        video_file=video_path,
        output_dir=output_dir_path,
        subtitle= subtitle,
        font = "/home/rteam2/.fonts/truetype/Vazir/vazirmatn-master/fonts/ttf/Vazirmatn-Black.ttf",
        font_size=50,
        font_color="white",
        stroke_width=2,
        stroke_color="black",
        shadow_strength=1.0,
        shadow_blur=0.8,
        highlight_current_word=True,
        word_highlight_color="blue",
        position=("center", "bottom"),  
        line_count=1,
        padding=50,
        print_info=True,
    )
    
if __name__ == "__main__":
    main()
    
    cprint("video edited successfully", "green")

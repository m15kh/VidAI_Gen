import yaml
import sys
import os
import json
from time import time


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))) # Add the parent directory of the 'models' folder to the system path

from SmartAITool.core import *
from scripts.models.captacity import add_captions
from scripts.models.subtitle.main import generate_subtitle
from scripts.models.youtube.downloader import youtube_downloader

def load_general_config(config):   
    
    debugger = config['debug_mode']
    video_path = config["video_path"]
    subtitle_path = config["subtitle_path"]
    output_dir_path = config['output_dir']
        
        
    return debugger, video_path, subtitle_path, output_dir_path

def load_subtitle_config(config):
     
    model_name = config["process_subtitle"].get("model", "large")
    language = config["process_subtitle"].get("language", "auto")
    translate_to = config["process_subtitle"].get("translate_to", None)
    args = {
        "task": config["process_subtitle"].get("task", "transcribe"),
        "verbose": config["process_subtitle"].get("verbose", False),
        "language": None  # Default to None, will be set later if needed
    }
    return model_name, language, translate_to, args
    

    
def main(config):
    #Load the configuration file [MAIN]
    debugger, video_path, subtitle_path, output_dir_path = load_general_config(config)
    
    cprint(f"the debug-mode is: {'ON' if debugger else 'OFF'}", "red" if debugger else "green")

    if video_path.startswith("http://") or video_path.startswith("https://"):
        cprint("[PIPELINE 1] downloading the video ...", "magenta")
    else:
        cprint("The video path is an MP4 file [SKIP [PIPELINE 1]]", "red")

    
    # ---------------------[PIPELINE 1](download videos)----------------------
  
    download_video_path = youtube_downloader(config)
    
    

    # ---------------------[PIPELINE 2](process subtitle)---------------------
    model_name, language, translate_to, args = load_subtitle_config(config)


    if subtitle_path == None:
           cprint("[PIPELINE 2] loading subtitle model ...", "magenta")
           subtitle = generate_subtitle(download_video_path, output_dir_path, model_name, language, translate_to, args)
    else:
        cprint("subtitle path is provided [SKIP [PIPELINE 2]]", "red")
        with open(subtitle_path, 'r') as file:
            subtitle = json.load(file)
            
            
            
    cprint("[PIPELINE 3] editing video ...", "magenta")
    # add_captions(
    #     download_video_path=download_video_path,
    #     subtitle= subtitle,
    #     font = "/home/rteam2/.fonts/truetype/Vazir/vazirmatn-master/fonts/ttf/Vazirmatn-Black.ttf",
    #     font_size=50,
    #     font_color="white",
    #     stroke_width=2,
    #     stroke_color="black",
    #     shadow_strength=1.0,
    #     shadow_blur=0.8,
    #     highlight_current_word=True,
    #     word_highlight_color="blue",
    #     position=("center", "bottom"),  
    #     line_count=1,
    #     padding=50,
    #     print_info=True,
    # )
    
if __name__ == "__main__":
    
    cprint("pipeline is running ...", "blue")
    
    start_time = time()
    with open("/home/rteam2/m15kh/auto-subtitle/config/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
        
    main(config)
    end_time = time()
    execution_time = end_time - start_time
    cprint(f"pipeline finished successfully in {execution_time:.2f} seconds", "blue")

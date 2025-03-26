import yaml
import sys
import os
import json
from time import time
from SmartAITool.core import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))) # Add the parent directory of the 'models' folder to the system path
#local
from scripts.models.process_video import add_captions
from scripts.models.subtitle.main import generate_subtitle
from scripts.models.youtube.downloader import youtube_downloader
from scripts.models.process_video.logo import add_logo
from scripts.src.config import load_general_config, load_subtitle_config

    
def main(config):
    #Load the configuration file [MAIN]
    debugger, video_path, subtitle_path = load_general_config(config)
    
    cprint(f"the debug-mode is: {'ON' if debugger else 'OFF'}", "red" if debugger else "green")

    if video_path.startswith("http://") or video_path.startswith("https://"):
        cprint("[PIPELINE 1] downloading the video ...", "magenta")
        video_path = youtube_downloader(config)
        cprint(f"video is downloaded: {video_path}", "yellow")


    else:
        cprint("The video path is an MP4 file [SKIP [PIPELINE 1]]", "red")

    
    # ---------------------[PIPELINE 1](download videos)----------------------
   #download_video_path = "video is downloaded: output/youtube/25_youtube_Motivate_me/download/Cristiano_Ronaldo_Winning_Mentality__Cristiano_Ronaldo_Motivation.mp4"

    # ---------------(create directory for videos and subtitle)----------------
    filename = os.path.splitext(os.path.basename(video_path))[0]
    base_dir = os.path.dirname(os.path.dirname(video_path))  # Gets output/youtube/11_youtube_Motivate_me
    subtitle_dir = os.path.join(base_dir, "subtitle")
    os.makedirs(subtitle_dir, exist_ok=True)
    final_video_dir = os.path.join(base_dir, "final_video")
    os.makedirs(final_video_dir, exist_ok=True)
    output_dir  = video_path, filename, subtitle_dir, final_video_dir 

    # ---------------------[PIPELINE 2](process subtitle)---------------------
    model_name, language, translate_to, args = load_subtitle_config(config)




    if subtitle_path == None:
        cprint("[PIPELINE 2] creating subtitle model ...", "magenta")
        subtitle = generate_subtitle(video_path, output_dir, model_name, language, translate_to, args)
        
        subtitle_json_path = os.path.join(subtitle_dir, f"{filename}.json")
        with open(subtitle_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(subtitle, json_file, indent=4, ensure_ascii=False)
        cprint(f"subtitle json format is saved: {subtitle_json_path}", 'yellow')

    else:
        cprint("subtitle path is provided [SKIP [PIPELINE 2]]", "red")
        with open(subtitle_path, 'r') as file:
            subtitle = json.load(file)
            
            
    # ---------------------[PIPELINE 3](adding subtitle to video)---------------------
    if config["process_subtitle"]["enabled"] == True:
        cprint("[PIPELINE 3] adding subtitle to video ...", "magenta")
        edit_video = add_captions(
            video_path=video_path,
            subtitle= subtitle,
            font = "/home/rteam2/.fonts/truetype/Vazir/vazirmatn-master/fonts/ttf/Vazirmatn-Black.ttf",
            font_size=60,
            font_color="white",
            stroke_width=2,
            stroke_color="black",
            shadow_strength=1.0,
            shadow_blur=0.8,
            highlight_current_word=True,
            word_highlight_color="red",
            position=("center", "bottom"),  
            line_count=1,
            padding=50,
            print_info=True,
        )
    else:
        cprint("adding subtitle is disabled [SKIP [PIPELINE 3]]", "red")
        
    # ---------------------[PIPELINE 3](Adding logo to the video)---------------------
    
    if config["video_editor"]["logo"]["enabled"] == True:
        cprint("[PIPELINE 4] Adding logo to the video ...", "magenta")
        if config["process_subtitle"]["enabled"] == False:
            edit_video = video_path
        edit_video = add_logo(config, edit_video)
    else:
        cprint("adding logo is disabled [SKIP [PIPELINE 4]]", "red")
    
    # ---------------------[PIPELINE 5](Generate Descrption and Title)---------------------
    # cprint("[PIPELINE 5] Generate Descrption and Title ...", "magenta")

    # ---------------------[PIPELINE 6](Adding thumbail to the video)---------------------
    # cprint("[PIPELINE 6] Adding thumbail to the video ...", "magenta")
    
    
    # ---------------------[PIPELINE 7](Save Final-Video)---------------------
    cprint("[PIPELINE 7] Saving Final-Video ...", "magenta")
    output_video_path = os.path.join(final_video_dir, f"{filename}_final.mp4")
    edit_video.write_videofile(output_video_path, codec="libx264")
    cprint(f"Final video saved at: {output_video_path}", "yellow")
    #----------------------[PIPELINE 8](upload telegram)---------------------
    #----------------------[PIPELINE 9](Removing temp files)---------------------
    

        
if __name__ == "__main__":
    
    cprint("pipeline is running ...", "blue")
    
    start_time = time()
    with open("/home/rteam2/m15kh/auto-subtitle/config/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
        
    main(config)
    end_time = time()
    execution_time = end_time - start_time
    cprint(f"pipeline finished successfully in {execution_time:.2f} seconds", "blue")

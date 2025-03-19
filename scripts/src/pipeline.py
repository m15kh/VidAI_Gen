import sys
import os
from SmartAITool.core import cprint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))) # Add the parent directory of the 'models' folder to the system path


import yaml

#local import
from scripts.models.subtitle.generator_subtitle import transcribe_video
from scripts.models import captacity

def load_yaml_config(file_path):
    #read the yaml file
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def main():
    # Load the configuration file
    config = load_yaml_config("/home/rteam2/m15kh/auto-subtitle/config/config.yaml")
    debugger = config['debug_mode']
    # Get the video path from the configuration file
    video_path = config['video']["address"]
    model_subtitle = config['subtitle']['model']
    output_dir_path = config['output_dir']




    if debugger:
        cprint("the debug-mode is: ON", "red")

        print(f"Video Path: {video_path}")
        print(f"Subtitle Model: {model_subtitle}")
        print(f"Transcribing video: {video_path} with model: {model_subtitle}") 
    else:
        cprint("the debug-mode is: OFF", "green")

        
    print("loading subtitle model ...")
    subtitle, status = transcribe_video(video_path,output_dir_path,model_subtitle )
    print("Subtitle generated successfully" if status else "Subtitle generation ****failed****")
    
    print("Adding captions to video ...")
    
    captacity.add_captions( #LOG
    video_file=video_path,
    output_dir=output_dir_path,
    font = "/home/rteam2/.fonts/truetype/Vazir/vazirmatn-master/fonts/ttf/Vazirmatn-Black.ttf",
    # font="fonts/Bangers-Regular.ttf",
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

    

if __name__ == "__main__":
    main()
    cprint("Pipeline finished successfully", "blue")
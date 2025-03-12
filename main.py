import sys
sys.path.append("..") 

from scripts.models import captacity
import os

# Get input video path
input_video = "/home/rteam2/m15kh/auto-subtitle/data/fa-tst4.mp4"
# Extract just the filename without extension
base_filename = os.path.splitext(os.path.basename(input_video))[0]
# Specify output folder
output_folder = "/home/rteam2/m15kh/auto-subtitle/result"
# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)
# Generate output path
output_path = os.path.join(output_folder, f"{base_filename}_captioned.mp4")

captacity.add_captions(
    video_file=input_video,
    output_file=output_path,
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

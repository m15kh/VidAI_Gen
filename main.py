import sys
sys.path.append("..") 

from scripts.models import captacity

captacity.add_captions(
    video_file="/home/rteam2/m15kh/auto-subtitle/data/fa-tst4.mp4",
    output_file="/home/rteam2/m15kh/auto-subtitle/fa_tst4_edit.mp4",
    #/home/rteam2/.fonts/truetype/Vazir/vazirmatn-master/fonts/ttf/Vazirmatn-Black.ttf
    #/home/rteam2/m15kh/video-subtitle/notebook/auto-subtitle/auto_subtitle/captacity/captacity/assets/fonts/Bangers-Regular.ttf",

    font = "/home/rteam2/.fonts/truetype/Vazir/vazirmatn-master/fonts/ttf/Vazirmatn-Black.ttf",
    font_size = 130,
    font_color = "white",

    stroke_width = 2,
    stroke_color = "black",

    shadow_strength = 1.0,
    shadow_blur = 0.8,

    highlight_current_word = True,
    word_highlight_color = "blue",

    line_count=2,

    padding = 50,
    print_info = True,
    
    
)
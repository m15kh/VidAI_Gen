from moviepy.editor import *
import yaml
import os
import numpy as np
import random  # Add import for random module
from PIL import Image, ImageFilter, ImageFont

def create_shadow_text(text, fontsize, text_color, bg_color, shadow_config, size=None):
    """Create text with shadow effect"""
    # Create shadow text clip
    if shadow_config.get("enabled", False):
        shadow_color = shadow_config.get("color", "black")
        offset_x = shadow_config.get("offset_x", 2)
        offset_y = shadow_config.get("offset_y", 2)
        blur = shadow_config.get("blur", 3)
        
        # Create shadow clip (positioned behind the main text)
        shadow = TextClip(text, fontsize=fontsize, color=shadow_color, 
                         font="Arial", size=size, method="caption")
        
        if blur > 0 and hasattr(shadow, "filter"):
            # Apply blur if available and requested
            try:
                shadow = shadow.filter(lambda image: Image.fromarray(image).filter(
                    ImageFilter.GaussianBlur(radius=blur)))
            except (ImportError, NameError):
                # If PIL filters not available, skip blur
                pass
                
        # Main text clip
        txt_clip = TextClip(text, fontsize=fontsize, color=text_color, bg_color=bg_color,
                           font="Arial", size=size, method="caption")
        
        # Combine shadow and text with shadow offset
        return CompositeVideoClip([
            shadow.set_position((offset_x, offset_y)),
            txt_clip.set_position((0, 0))
        ])
    else:
        # Return simple text clip without shadow
        return TextClip(text, fontsize=fontsize, color=text_color, bg_color=bg_color,
                       font="Arial", size=size, method="caption")

def apply_text_effect(txt_clip, effect, duration, speed=1.0):
    """Apply visual effects to text clip"""
    if effect == "fade_in_out":
        # Fade in and out effect
        fade_duration = min(1.0, duration / 4) * speed
        return txt_clip.fadein(fade_duration).fadeout(fade_duration)
    
    elif effect == "pulse":
        # Pulsing size effect
        def resize_func(t):
            # Pulse between 90% and 110% size
            pulse = 0.1 * np.sin(2 * np.pi * t * speed)
            return 1.0 + pulse
        
        return txt_clip.fx(vfx.resize, resize_func)
    
    elif effect == "bounce":
        # Bouncing effect
        def y_pos(t):
            # Simple bounce with sin function
            return 20 * np.abs(np.sin(2 * np.pi * t * speed))
        
        return txt_clip.set_position(lambda t: (txt_clip.pos(t)[0], txt_clip.pos(t)[1] + y_pos(t)))
    
    else:
        # No effect
        return txt_clip

def add_logo(config, video):
    """Main function to process video with subtitle and logo effects"""

# Check if the path is valid
    if os.path.isfile(video):
        video = VideoFileClip(video)


    # Check if subtitle is enabled
    subtitle_enabled = config["video_editor"].get("subtitle", {}).get("enabled", True)

    # List to hold all clips (starting with the base video)
    clips = [video]

    # Add subtitle if enabled
    if subtitle_enabled:
        subtitle_config = config["video_editor"].get("subtitle", {})
        subtitle_text = subtitle_config.get("text", "Sample Subtitle")
        subtitle_fontsize = subtitle_config.get("fontsize", 30)
        subtitle_color = subtitle_config.get("color", "white")
        subtitle_bg = subtitle_config.get("background_color", "rgba(0,0,0,0.5)")
        
        # Randomly select movement type instead of using the config value
        movement_options = ["diagonal", "horizontal", "vertical"]
        subtitle_movement = random.choice(movement_options)
        print(f"Randomly selected movement: {subtitle_movement}")
        
        shadow_config = subtitle_config.get("shadow", {})
        text_effect = subtitle_config.get("effect", "none")
        animation_speed = subtitle_config.get("animation_speed", 1.0)

        # Create subtitle text clip with shadow
        subtitle = create_shadow_text(
            subtitle_text, 
            subtitle_fontsize,
            subtitle_color,
            subtitle_bg,
            shadow_config,
            size=(video.w * 0.8, None)
        ).set_duration(video.duration)
        
        # Apply configured text effect
        subtitle = apply_text_effect(subtitle, text_effect, video.duration, animation_speed)

        # Define subtitle movement based on configuration
        if subtitle_movement == "horizontal":
            subtitle_position = lambda t: (int(video.w * t / video.duration - subtitle.w / 2), video.h - subtitle.h - 50)
        elif subtitle_movement == "vertical":
            subtitle_position = lambda t: (int(video.w / 2 - subtitle.w / 2), int(video.h * t / video.duration - subtitle.h / 2))
        else:  # Default: diagonal
            subtitle_position = lambda t: (int(video.w * t / video.duration - subtitle.w / 2), 
                                         int(video.h * (1 - t / video.duration) - subtitle.h / 2))

        # Apply movement to subtitle
        subtitle = subtitle.set_position(subtitle_position)
        clips.append(subtitle)

    # Create the final composite video with all enabled elements
    final_video = CompositeVideoClip(clips).set_duration(video.duration)

    # Save the video in high quality
    # final_video.write_videofile(output_video_path)

    return final_video
if __name__ == "__main__":
    # Path to config file (in the same directory as this script)
    config_path = "/home/rteam2/m15kh/auto-subtitle/config/config.yaml"
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)



    add_logo(config)
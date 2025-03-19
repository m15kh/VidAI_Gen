import whisper
import json
import os

def transcribe_video(video_path, output_dir_path, model_type="large", word_timestamps=True):
    """
    Transcribe video with Whisper model.
    
    Args:
        video_path: Path to the video file
        output_dir_path: Path to the output directory
        model_type: Whisper model type (default: "large")
        word_timestamps: Whether to include word-level timestamps
        debug: Debug mode (default: False)
    
    Returns:
        Transcription result
    """

    model = whisper.load_model(model_type)
    result = model.transcribe(video_path, word_timestamps=word_timestamps)

    # Create a folder named after the video file (without extension) inside the output directory
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_dir = os.path.join(output_dir_path, video_name, "subtitle")
    os.makedirs(video_output_dir, exist_ok=True)
    
    # Save the subtitle JSON file in the created folder
    output_file = os.path.join(video_output_dir, f"subtitle_{video_name}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    if result not in [None, ""]:
        return result, True
    return result , False

# Example usage
if __name__ == "__main__":
    video_path = "/home/rteam2/m15kh/auto-subtitle/data/fa-tst4.mp4"
    output_dir_path = "/home/rteam2/m15kh/auto-subtitle/output"
    model_type = "large"  # or "turbo"
    result = transcribe_video(video_path, output_dir_path, model_type)

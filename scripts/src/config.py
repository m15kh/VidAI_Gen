
def load_general_config(config):   
    
    debugger = config['debug_mode']
    video_path = config["video_path"]
    subtitle_path = config["subtitle_path"]
        
        
    return debugger, video_path, subtitle_path

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
    

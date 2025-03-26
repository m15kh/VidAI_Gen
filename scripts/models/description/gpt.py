import openai
import json
import os
import yaml  # Add yaml import for config parsing

def load_config():
    """Load GPT configuration settings from config file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                               "config", "config.yaml")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    
    # Check if GPT configuration exists
    if "gpt" not in config:
        raise ValueError("GPT configuration is missing in the config file")
    
    return config["gpt"]

def read_subtitle_file(file_path):
    """Read a JSON file containing subtitle data."""
    with open(file_path, 'r') as file:
        return json.load(file)

def generate_instagram_description(subtitle_data, config):
    """Generate an Instagram description from subtitle data."""
    # Extract the text from each segment
    text_segments = [item['text'] for item in subtitle_data]
    
    # Combine all text segments
    full_text = " ".join(text_segments)
    
    # Generate description using GPT
    response = openai.chat.completions.create(
        model=config.get("model", "gpt-4o"),
        messages=[
            {"role": "system", "content": config["description"]["system_prompt"]},
            {"role": "user", "content": config["description"]["user_prompt_template"].format(content=full_text)}
        ],
        max_tokens=config["description"]["max_tokens"]
    )
    
    description = response.choices[0].message.content
    
    # Ensure the description is under max_length characters
    max_length = config["description"].get("max_length", 150)
    if len(description) > max_length:
        description = description[:max_length-3] + "..."
        
    return description

def generate_hashtags(subtitle_data, config):
    """Generate 10 relevant hashtags for Instagram based on subtitle content."""
    # Extract the text from each segment
    text_segments = [item['text'] for item in subtitle_data]
    
    # Combine all text segments
    full_text = " ".join(text_segments)
    
    # Generate hashtags using GPT
    response = openai.chat.completions.create(
        model=config.get("model", "gpt-4o"),
        messages=[
            {"role": "system", "content": config["hashtags"]["system_prompt"]},
            {"role": "user", "content": config["hashtags"]["user_prompt_template"].format(content=full_text)}
        ],
        max_tokens=config["hashtags"]["max_tokens"]
    )
    
    hashtags_text = response.choices[0].message.content
    
    # Process the hashtags to ensure we have exactly the requested number
    import re
    hashtags = re.findall(r'#\w+', hashtags_text)
    
    # If we don't have enough formatted hashtags, extract from a numbered or bulleted list
    if len(hashtags) != config["hashtags"]["count"]:
        list_items = re.findall(r'[\d\.\*\-]\s*#?(\w+)', hashtags_text)
        hashtags = [f"#{item}" if not item.startswith('#') else item for item in list_items]
    
    # If we still don't have enough hashtags, use any words we can find
    if len(hashtags) != config["hashtags"]["count"]:
        words = re.findall(r'\b(\w+)\b', hashtags_text)
        hashtags = [f"#{word.lower()}" for word in words if len(word) > 3][:config["hashtags"]["count"]]
    
    # Ensure we have exactly the requested number of hashtags
    if len(hashtags) > config["hashtags"]["count"]:
        hashtags = hashtags[:config["hashtags"]["count"]]
    
    return " ".join(hashtags)

def generate_video_title(subtitle_data, config):
    """Generate an engaging video title based on subtitle content."""
    # Extract the text from each segment
    text_segments = [item['text'] for item in subtitle_data]
    
    # Combine all text segments
    full_text = " ".join(text_segments)
    
    # Generate title using GPT
    response = openai.chat.completions.create(
        model=config.get("model", "gpt-4o"),
        messages=[
            {"role": "system", "content": config["title"]["system_prompt"]},
            {"role": "user", "content": config["title"]["user_prompt_template"].format(content=full_text)}
        ],
        max_tokens=config["title"]["max_tokens"]
    )
    
    title = response.choices[0].message.content.strip()
    
    # Remove quotes if they exist
    if title.startswith('"') and title.endswith('"'):
        title = title[1:-1]
    
    return title

def main(file_path, output_file=None):
    """Main function to process subtitle file and generate content."""
    # Load configuration
    config = load_config()
    
    # Set API key
    openai.api_key = config["api_key"]
    
    subtitle_data = read_subtitle_file(file_path)
    
    # Generate title
    title = generate_video_title(subtitle_data, config)
    
    # Generate Instagram content
    description = generate_instagram_description(subtitle_data, config)
    hashtags = generate_hashtags(subtitle_data, config)
    
    # Prepare output content as JSON
    output_content = {
        "title": title,
        "description": description,
        "hashtags": hashtags
    }
    
    # Print to console
    print(output_content)
    
    # Save to file if output_file is specified
    if output_file:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_content, f, ensure_ascii=False, indent=4)
        print(f"Output saved to: {output_file}")
    
    return title, description, hashtags

# Example usage
if __name__ == "__main__":
    # Replace with your actual JSON file path
    input_file = "/home/rteam2/m15kh/auto-subtitle/output/youtube/20_youtube_Motivate_me/subtitle/Cristiano_Ronaldo_Winning_Mentality__Cristiano_Ronaldo_Motivation.json"
    
    # Generate output file path based on input file
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(os.path.dirname(os.path.dirname(input_file)), "descriptions")
    output_file = os.path.join(output_dir, f"{base_name}_content.json")
    
    main(input_file, output_file)

import openai
import json
import os

openai.api_key = "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"

def read_subtitle_file(file_path):
    """Read a JSON file containing subtitle data."""
    with open(file_path, 'r') as file:
        return json.load(file)

def generate_instagram_description(subtitle_data):
    """Generate an Instagram description from subtitle data."""
    # Extract the text from each segment
    text_segments = [item['text'] for item in subtitle_data]
    
    # Combine all text segments
    full_text = " ".join(text_segments)
    
    # Generate description using GPT
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a social media expert. Create a concise and engaging Instagram description."},
            {"role": "user", "content": f"Create an Instagram description (maximum 150 characters) for this content: {full_text}"}
        ],
        max_tokens=100
    )
    
    description = response.choices[0].message.content
    
    # Ensure the description is under 150 characters
    if len(description) > 150:
        description = description[:147] + "..."
        
    return description

def generate_hashtags(subtitle_data):
    """Generate 10 relevant hashtags for Instagram based on subtitle content."""
    # Extract the text from each segment
    text_segments = [item['text'] for item in subtitle_data]
    
    # Combine all text segments
    full_text = " ".join(text_segments)
    
    # Generate hashtags using GPT
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a social media hashtag expert. Create exactly 10 relevant and trending hashtags."},
            {"role": "user", "content": f"Create exactly 10 relevant hashtags for Instagram for this content: {full_text}. Format them as a list of strings with hashtag symbols."}
        ],
        max_tokens=100
    )
    
    hashtags_text = response.choices[0].message.content
    
    # Process the hashtags to ensure we have exactly 10
    # First, try to extract hashtags that already have # symbol
    import re
    hashtags = re.findall(r'#\w+', hashtags_text)
    
    # If we don't have enough formatted hashtags, extract words and add # symbol
    if len(hashtags) != 10:
        # Try to extract from a numbered or bulleted list
        list_items = re.findall(r'[\d\.\*\-]\s*#?(\w+)', hashtags_text)
        hashtags = [f"#{item}" if not item.startswith('#') else item for item in list_items]
    
    # If we still don't have 10 hashtags, use any words we can find
    if len(hashtags) != 10:
        words = re.findall(r'\b(\w+)\b', hashtags_text)
        hashtags = [f"#{word.lower()}" for word in words if len(word) > 3][:10]
    
    # Ensure we have exactly 10 hashtags
    if len(hashtags) > 10:
        hashtags = hashtags[:10]
    
    return " ".join(hashtags)

def generate_video_title(subtitle_data):
    """Generate an engaging video title based on subtitle content."""
    # Extract the text from each segment
    text_segments = [item['text'] for item in subtitle_data]
    
    # Combine all text segments
    full_text = " ".join(text_segments)
    
    # Generate title using GPT
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a YouTube video title expert. Create attention-grabbing, SEO-friendly titles."},
            {"role": "user", "content": f"""Create an engaging and clickable video title based on this content: {full_text}

Examples of great titles:
1. "The Winner's Mindset: Transform Challenges into Opportunities"
2. "Losers React, Winners Respond: The Crucial Difference"
3. "How Top Performers Turn Negative Emotions into Success"
4. "The Secret Mindset Shift That Separates Winners from Everyone Else"
5. "Transmute Your Struggles: The Psychology of High Achievement"

Create a title that's catchy, specific, and around 5-10 words.
"""}
        ],
        max_tokens=50
    )
    
    title = response.choices[0].message.content.strip()
    
    # Remove quotes if they exist
    if title.startswith('"') and title.endswith('"'):
        title = title[1:-1]
    
    return title

def main(file_path, output_file=None):
    """Main function to process subtitle file and generate content."""
    subtitle_data = read_subtitle_file(file_path)
    
    # Generate title
    title = generate_video_title(subtitle_data)
    
    # Generate Instagram content
    description = generate_instagram_description(subtitle_data)
    hashtags = generate_hashtags(subtitle_data)
    
    # Prepare output content
    output_content = f"""Video Title:
{title}
Character count: {len(title)}

{'-'*50}

Instagram Description (150 char max):
{description}
Character count: {len(description)}

Instagram Hashtags (10):
{hashtags}
"""
    
    # Print to console
    print(output_content)
    
    # Save to file if output_file is specified
    if output_file:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Output saved to: {output_file}")
    
    return title, description, hashtags

# Example usage
if __name__ == "__main__":
    # Replace with your actual JSON file path
    input_file = "/home/rteam2/m15kh/auto-subtitle/output/youtube/20_youtube_Motivate_me/subtitle/Cristiano_Ronaldo_Winning_Mentality__Cristiano_Ronaldo_Motivation.json"
    
    # Generate output file path based on input file
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(os.path.dirname(os.path.dirname(input_file)), "descriptions")
    output_file = os.path.join(output_dir, f"{base_name}_content.txt")
    
    main(input_file, output_file)

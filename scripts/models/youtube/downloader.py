import yaml
import subprocess
import os
import re
import tempfile
import shutil
import json
from pathlib import Path



def is_short_video(url):
    """Detect if URL is for a YouTube Short."""
    return '/shorts/' in url or 'youtube.com/shorts' in url

def parse_aspect_ratio(ratio_str):
    """Parse aspect ratio string (e.g., '16:9') to a float."""
    try:
        w, h = map(int, ratio_str.split(':'))
        return w / h
    except (ValueError, ZeroDivisionError):
        return 16 / 9  # Default to 16:9 if parsing fails

def get_video_info(url):
    """Get channel name and video title from YouTube URL using yt-dlp."""
    try:
        # Use yt-dlp to fetch video metadata in JSON format
        cmd = ['yt-dlp', '--dump-json', '--skip-download', url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            metadata = json.loads(result.stdout)
            channel_name = metadata.get('channel', metadata.get('uploader', 'unknown'))
            video_title = metadata.get('title', 'video')
            
            # Clean channel name (remove special characters, spaces to underscores)
            channel_name = re.sub(r'[^\w\s-]', '', channel_name).strip().replace(' ', '_')
            
            return {
                'channel': channel_name,
                'title': video_title
            }
    except Exception as e:
        print(f"Error getting video info: {str(e)}")
    
    # Return defaults if we couldn't get the info
    return {
        'channel': 'channel',
        'title': 'video'
    }

def get_next_counter(counter_file=None):
    """Get the next counter value and increment the stored value."""
    if counter_file is None:
        counter_file = os.path.join(os.path.dirname(__file__), 'download_counter.txt')
    
    # Default starting counter
    counter = 1
    
    # Try to read existing counter
    try:
        if os.path.exists(counter_file):
            with open(counter_file, 'r') as f:
                counter = int(f.read().strip())
    except Exception as e:
        print(f"Error reading counter: {str(e)}")
    
    # Write incremented counter back to file
    try:
        with open(counter_file, 'w') as f:
            f.write(str(counter + 1))
    except Exception as e:
        print(f"Error writing counter: {str(e)}")
    
    return counter

def create_nested_folder_structure(output_base_dir, counter, channel_name):
    """Create a nested folder structure for the downloaded video."""
    # First create a youtube folder inside the output directory
    youtube_folder_path = os.path.join(output_base_dir, "youtube")
    Path(youtube_folder_path).mkdir(parents=True, exist_ok=True)
    
    # Create main folder name with counter, youtube, and channel name inside the youtube folder
    main_folder_name = f"{counter}_youtube_{channel_name}"
    main_folder_path = os.path.join(youtube_folder_path, main_folder_name)
    
    # Create download subfolder inside the main folder
    download_folder_path = os.path.join(main_folder_path, "download")
    
    # Create both folders
    Path(main_folder_path).mkdir(parents=True, exist_ok=True)
    Path(download_folder_path).mkdir(parents=True, exist_ok=True)
    
    return {
        "youtube_folder": youtube_folder_path,
        "main_folder": main_folder_path,
        "download_folder": download_folder_path
    }

def download_video(config):
    """
    Extract YouTube configuration and download video segments using yt-dlp.
    Returns the path to the downloaded video or list of segment files.
    """
    # Extract all YouTube configuration parameters from the config dict
    params = {
        # Basic video parameters
        'url': config.get('video_path', ''),
        'quality': config['youtube'].get('quality', 'best'),
        'resolution': config['youtube'].get('resolution', None),
        'download_full': config['youtube'].get('download_full', False),
        'video_type': config['youtube'].get('video_type', None),
        
        # Filename format settings
        'filename_format': {
            'use_counter': config['youtube'].get('filename_format', {}).get('use_counter', True),
            'use_channel': config['youtube'].get('filename_format', {}).get('use_channel', True),
            'prefix': config['youtube'].get('filename_format', {}).get('prefix', ''),
            'use_nested_folders': config['youtube'].get('filename_format', {}).get('use_nested_folders', True),
        },
        
        # Output parameters
        'output_dir': config.get('output_dir', './output'),
        'output': {
            'filename': config['youtube']['output'].get('filename', None) if 'output' in config['youtube'] else None,
            'merge': config['youtube']['output'].get('merge', True) if 'output' in config['youtube'] else True,
        },
        
        # Segments for partial download
        'segments': config['youtube'].get('segments', [])
    }
    
    # For backward compatibility with old format
    if 'time' in config['youtube']:
        params['time'] = config['youtube'].get('time', {})
    if 'aspect_ratio' in config['youtube']:
        params['aspect_ratio'] = config['youtube'].get('aspect_ratio', {})
    
    # Extract common parameters from the parsed config
    url = params['url']
    quality = params['quality']
    resolution = params['resolution']
    download_full = params['download_full']
    manual_video_type = params['video_type']
    
    # Get filename format settings
    filename_format = params['filename_format']
    use_counter = filename_format['use_counter']
    use_channel = filename_format['use_channel']
    custom_prefix = filename_format['prefix']
    use_nested_folders = filename_format['use_nested_folders']
    
    # Output parameters
    output_dir = params['output_dir']
    base_filename = params['output']['filename']
    should_merge = params['output']['merge']
    
    # If custom filename formatting is enabled and no base_filename is provided
    if not base_filename and (use_counter or use_channel):
        # The actual filename will be generated in download_segment
        base_filename = None
        
    # If nested folder structure is enabled, set base_filename to None
    # to use our custom folder structure
    if use_nested_folders:
        base_filename = None
        
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Check if we want to download the full video
    if download_full:
        print("\n==== Downloading Full Video ====")
        # Create a segment with no time constraints but with aspect ratio settings
        aspect_config = {}
        
        # For full video downloads, get aspect ratio from first segment if available
        if params['segments']:
            aspect_config = params['segments'][0].get('aspect_ratio', {})
        
        segment = {
            'aspect_ratio': aspect_config
        }
        
        # Download the full video
        result = download_segment(url, segment, quality, resolution, output_dir, base_filename, manual_video_type)
        return result
        
    # Handle segments if not downloading full video
    if params['segments']:
        segments = params['segments']
        print(f"Processing {len(segments)} video segments")
        
        segment_files = []
        
        # If not merging, use the final output directory for individual segments
        segments_dir = tempfile.mkdtemp(prefix="yt_segments_") if should_merge else output_dir
        
        for i, segment in enumerate(segments):
            # Create a unique filename for each segment
            if base_filename and not should_merge:
                segment_filename = f"{base_filename}_segment{i+1}"
            elif should_merge:
                segment_filename = f"segment_{i+1:03d}"
            else:
                segment_filename = f"segment_{i+1:03d}"
                
            print(f"\n==== Processing Segment {i+1} ====")
            output_file = download_segment(url, segment, quality, resolution, segments_dir, segment_filename, manual_video_type)
            if output_file:
                segment_files.append(output_file)
        
        if segment_files and should_merge:
            # Merge all segments into final output
            if base_filename:
                final_output = os.path.join(output_dir, f"{base_filename}.mp4")
            else:
                final_output = os.path.join(output_dir, "merged_output.mp4")
                
            print(f"\n==== Merging {len(segment_files)} segments into final output ====")
            success = merge_video_segments(segment_files, final_output)
            
            # Clean up temp directory if merging was successful
            if success:
                print(f"Final video saved to: {final_output}")
                shutil.rmtree(segments_dir)
                return final_output
            else:
                print("Merging failed. Segment files are preserved in the temporary directory.")
                print(f"Temporary directory: {segments_dir}")
                return None
        elif segment_files and not should_merge:
            print(f"\n==== Skipping merge (merge=false) ====")
            print(f"Individual segments saved to: {output_dir}")
            for file in segment_files:
                print(f"  - {os.path.basename(file)}")
            return segment_files
        return None
    else:
        # Backward compatibility with old format
        time_config = params.get('time', {})
        aspect_config = params.get('aspect_ratio', {})
        
        # Create a segment from the old format
        segment = {
            'time': time_config,
            'aspect_ratio': aspect_config
        }
        
        result = download_segment(url, segment, quality, resolution, output_dir, base_filename, manual_video_type)
        return result

def download_segment(url, segment, quality, resolution, output_dir, segment_filename=None, manual_video_type=None):
    """Download a video segment with specific settings."""
    # Time range parameters
    time_config = segment.get('time', {})
    start_time = time_config.get('start', None)
    end_time = time_config.get('end', None)
    
    # Aspect ratio parameters
    aspect_config = segment.get('aspect_ratio', {})
    aspect_mode = aspect_config.get('mode', 'auto')
    aspect_ratio = aspect_config.get('ratio', '16:9')
    crop_position = aspect_config.get('crop_position', 'center')
    
    # Determine if it's a short video - use manual override if provided
    if manual_video_type is not None:
        is_short = manual_video_type.lower() == "short"
        print(f"Using manual video type: {'Short' if is_short else 'Regular'}")
    else:
        # Fall back to automatic detection
        is_short = is_short_video(url) if aspect_mode == 'auto' else False
    
    # Get video info for naming
    video_info = get_video_info(url)
    counter = get_next_counter()
    
    # Create nested folder structure if no filename was provided
    if not segment_filename:
        # Create folder structure - using output_dir as base
        folders = create_nested_folder_structure(output_dir, counter, video_info['channel'])
        
        # Set the output path to the download subfolder
        output_dir = folders["download_folder"]
        
        # Use video title as filename inside the download folder
        video_title = re.sub(r'[^\w\s-]', '', video_info['title']).strip().replace(' ', '_')
        segment_filename = video_title if video_title else "video"
        
        print(f"Creating nested folder structure:")
        print(f"  YouTube folder: {folders['youtube_folder']}")
        print(f"  Main folder: {folders['main_folder']}")
        print(f"  Download folder: {folders['download_folder']}")
    
    # Build yt-dlp command
    cmd = ['yt-dlp']
    
    # Add URL
    cmd.append(url)
    
    # Handle quality and resolution for YouTube videos
    # Ensure we're only downloading a single format to avoid multiple downloads
    if is_short:
        # For shorts, use a simpler format selector
        cmd.extend(['-f', 'best'])
    elif resolution:
        # For regular videos with resolution, use a more specific selector
        # The slash indicates fallback, not multiple formats
        res_value = resolution.rstrip("p")
        cmd.extend(['-f', f'best[height<={res_value}]/best'])
    elif quality != 'best':
        # Use the specific quality parameter if provided
        cmd.extend(['-f', quality])
    else:
        # Default to best format
        cmd.extend(['-f', 'best'])
    
    # Add --no-playlist to ensure only the video is downloaded, not related videos
    cmd.append('--no-playlist')
    
    # Handle time range
    if start_time or end_time:
        time_range = []
        if start_time:
            time_range.append(start_time)
        else:
            time_range.append('0')
            
        if end_time:
            time_range.append(end_time)
        
        if time_range:
            cmd.extend(['--download-sections', '*' + '-'.join(time_range)])
    
    # Ensure MP4 output for easier merging
    cmd.extend(['--merge-output-format', 'mp4'])
    
    # Define output filename template
    output_template = os.path.join(output_dir, segment_filename)
    cmd.extend(['-o', f'{output_template}.%(ext)s'])
    expected_output = f"{output_template}.mp4"
    
    # Add metadata about video type/aspect ratio
    cmd.extend(['--add-metadata'])
    
    # Add crop options if crop mode is enabled
    if aspect_mode == 'crop':
        # Add ffmpeg post-processing to crop the video
        crop_filter = f"\"crop='if(gt(dar,{parse_aspect_ratio(aspect_ratio)}),ih*{parse_aspect_ratio(aspect_ratio)},iw):"
        crop_filter += f"if(gt(dar,{parse_aspect_ratio(aspect_ratio)}),ih,iw/{parse_aspect_ratio(aspect_ratio)})"
        
        # Handle crop position
        if crop_position == 'center':
            crop_filter += ":if(gt(dar,{0}),(iw-ih*{0})/2,0):if(gt(dar,{0}),0,(ih-iw/{0})/2)'\"".format(parse_aspect_ratio(aspect_ratio))
        elif crop_position == 'left':
            crop_filter += ":0:if(gt(dar,{0}),0,(ih-iw/{0})/2)'\"".format(parse_aspect_ratio(aspect_ratio))
        elif crop_position == 'right':
            crop_filter += ":if(gt(dar,{0}),iw-ih*{0},0):if(gt(dar,{0}),0,(ih-iw/{0})/2)'\"".format(parse_aspect_ratio(aspect_ratio))
        elif crop_position == 'top':
            crop_filter += ":if(gt(dar,{0}),(iw-ih*{0})/2,0):0'\"".format(parse_aspect_ratio(aspect_ratio))
        elif crop_position == 'bottom':
            crop_filter += ":if(gt(dar,{0}),(iw-ih*{0})/2,0):if(gt(dar,{0}),ih-ih,ih-iw/{0})'\"".format(parse_aspect_ratio(aspect_ratio))
        
        # Add the -c:v libx264 parameter to force re-encoding instead of stream copying
        cmd.extend(['--postprocessor-args', f"ffmpeg:-vf {crop_filter} -c:v libx264"])
    
    # Add scale/pad options if scale mode is enabled (and not a short video)
    elif aspect_mode == 'scale' and not is_short:
        target_ratio = parse_aspect_ratio(aspect_ratio)
        # Calculate scaling and padding to maintain aspect ratio while fitting into target ratio
        pad_filter = f"\"scale=iw:ih,setsar=1,pad=max(iw\\,ih*{target_ratio}):max(ih\\,iw/{target_ratio}):(ow-iw)/2:(oh-ih)/2:black'\"" 
        
        # Add the filter to FFmpeg command
        cmd.extend(['--postprocessor-args', f"ffmpeg:-vf {pad_filter} -c:v libx264"])
    
    # Print segment information
    print(f"Segment time: {start_time} to {end_time}")
    print(f"Aspect ratio mode: {aspect_mode}")
    print(f"Video type: {'Short' if is_short else 'Regular'} {'(manually set)' if manual_video_type else '(auto-detected)'}")
    if aspect_mode in ['force', 'crop', 'scale']:
        print(f"Target aspect ratio: {aspect_ratio}")
    if aspect_mode == 'crop':
        print(f"Crop position: {crop_position}")
    if aspect_mode == 'scale' and is_short:
        print("Short video detected - downloading without modification")
    
    # Execute the command
    print(f"Executing command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # First fallback: if initial download fails, try with --force-generic-extractor
    if result.returncode != 0:
        print("\nInitial download failed. Trying with force-generic-extractor...")
        # Remove any format specification that might be causing problems
        cmd = [c for c in cmd if not (c.startswith('best[height') or c.startswith('bv*[height'))]
        if '-f' in cmd:
            idx = cmd.index('-f')
            if idx < len(cmd)-1:
                cmd.pop(idx+1)  # Remove format specifier
            cmd.pop(idx)  # Remove -f flag
        
        # Add force-generic-extractor which can help with signature extraction issues
        cmd.append('--force-generic-extractor')
        print(f"Retrying with command: {' '.join(cmd)}")
        result = subprocess.run(cmd)
    
    # Second fallback: If that still fails, try with --no-check-certificate
    if result.returncode != 0:
        print("\nSecond attempt failed. Trying with no-check-certificate...")
        if '--force-generic-extractor' not in cmd:
            cmd.append('--force-generic-extractor')
        cmd.append('--no-check-certificate')
        print(f"Retrying with command: {' '.join(cmd)}")
        result = subprocess.run(cmd)
    
    # Return the output filename if successful
    if result.returncode == 0 and expected_output:
        if os.path.exists(expected_output):
            return expected_output
    
    # If we don't have a predetermined filename, try to find the downloaded file
    if not expected_output and result.returncode == 0:
        # Look for the newest mp4 file in the output directory
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                if f.endswith('.mp4') and os.path.isfile(os.path.join(output_dir, f))]
        
        if files:
            newest_file = max(files, key=os.path.getmtime)
            return newest_file
    
    return None

def merge_video_segments(segment_files, output_file):
    """Merge multiple video segments into a single file using FFmpeg."""
    if not segment_files:
        print("No segments to merge.")
        return False
        
    # Create a temporary file list for FFmpeg
    list_file_path = os.path.join(os.path.dirname(segment_files[0]), "filelist.txt")
    
    with open(list_file_path, 'w') as list_file:
        for file in segment_files:
            if os.path.exists(file):
                list_file.write(f"file '{file}'\n")
    
    # Build FFmpeg command for concatenation
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_file_path,
        '-c', 'copy',
        '-y',  # Overwrite output file if it exists
        output_file
    ]
    
    print(f"Executing merge command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # Clean up the list file
    if os.path.exists(list_file_path):
        os.remove(list_file_path)
        
    return result.returncode == 0

def youtube_downloader(config):
    # Check if we want to directly use download_segment or the regular flow
    if config['youtube'].get('direct_segment_download', False):
        # Direct call to download_segment with parameters from config
        url = config.get('video_path', '')
        quality = config['youtube'].get('quality', 'best')
        resolution = config['youtube'].get('resolution', None)
        output_dir = config.get('output_dir', './output')
        base_filename = config['youtube'].get('output', {}).get('filename', None)
        manual_video_type = config['youtube'].get('video_type', None)
        
        # Create segment from time and aspect_ratio if available
        segment = {}
        if 'time' in config['youtube']:
            segment['time'] = config['youtube']['time']
        if 'aspect_ratio' in config['youtube']:
            segment['aspect_ratio'] = config['youtube']['aspect_ratio']
        elif config['youtube'].get('segments') and len(config['youtube']['segments']) > 0:
            # If no direct aspect_ratio but segments exist, use the first segment's aspect_ratio
            segment['aspect_ratio'] = config['youtube']['segments'][0].get('aspect_ratio', {})
        
        # Call download_segment directly
        result = download_segment(url, segment, quality, resolution, output_dir, base_filename, manual_video_type)
        print(f"Download result: {result}")
        return result
    else:
        # Regular flow
        result = download_video(config)
        print(f"Download result: {result}")
        return result

if __name__ == '__main__':
    
    config_path = '/home/rteam2/m15kh/auto-subtitle/config/config.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    video_path = youtube_downloader(config)

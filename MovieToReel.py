import cv2
import os
import numpy as np
import subprocess
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def time_to_seconds(time_str):
    """Convert time in 'MM:SS' or 'HH:MM:SS' format to total seconds."""
    parts = time_str.split(':')
    if len(parts) == 2:  # MM:SS format
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:  # HH:MM:SS format
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        raise ValueError("Invalid time format. Use 'MM:SS' or 'HH:MM:SS'.")

def process_segment_with_ffmpeg(video_path, start_time, segment_duration, segment_count, target_width, target_height, fps, video_name):
    # Create a proper naming format with Part1, Part2, etc., for each segment
    final_output_path = os.path.join("Reels", f"{video_name}_Part{segment_count + 1}.mp4")

    # Define the text to overlay on the video
    part_text = f"Part {segment_count + 1}"  # Text for overlay

    # Specify the font path (ensure the font file exists)
    font_path = "Lovelo-Black.ttf"
    font_path2 = "Montserrat.ttf"

    # Command to extract video, resize, pad to 9:16 aspect ratio, and include the audio
    ffmpeg_command = [
        'ffmpeg',
        '-ss', str(start_time),  # Start time for extraction
        '-i', video_path,  # Input video
        '-t', str(segment_duration),  # Duration of the segment
        '-vf', f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black,drawtext=text=\'{part_text}\':fontfile={font_path}:fontcolor=white:fontsize=100:bordercolor=black:borderw=2:x=(w-text_w)/2:y=h-th-380,drawtext=text=\'{video_name}\':fontfile={font_path}:fontcolor=red:fontsize=50:bordercolor=black:borderw=2:x=(w-text_w)/2:y=h-th-500, drawtext=text=Follow @movies_onyourdemand:fontfile={font_path2}:fontcolor=white:fontsize=50:bordercolor=black:borderw=2:x=(w-text_w)/2:y=500',  # Resize, pad, and add text
        '-c:v', 'libx264',  # Video codec
        '-c:a', 'aac',  # Audio codec
        '-strict', 'experimental',  # Allow the use of experimental codecs (needed for AAC)
        '-y',  # Overwrite the output file if it exists
        final_output_path  # Output file
    ]

    # Run ffmpeg to process both video and audio
    process = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check for errors in the process
    if process.returncode != 0:
        logging.error(f'Error processing segment {segment_count + 1}: {process.stderr.decode()}')
    else:
        logging.info(f'Segment {segment_count + 1} processed: {final_output_path}')

def split_video_with_ffmpeg(video_path, segment_duration=59, start_time="0:00", end_time=None):
    # Extract the base name of the video file without extension
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Convert start_time and end_time to seconds
    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time) if end_time else None

    # Create the output directory if it doesn't exist
    output_dir = "Reels"
    os.makedirs(output_dir, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Target dimensions for 9:16 aspect ratio
    target_height = 1920  # Adjust as needed
    target_width = int(target_height * 9 / 16)

    # Calculate end frame if end_time is provided
    if end_seconds is not None:
        end_frame = int(end_seconds * fps)
    else:
        end_frame = total_frames  # Default to the end of the video

    # Calculate start frame based on start_time
    start_frame = int(start_seconds * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Initialize segment count
    segment_count = 0

    # Total segments to process (between start and end times)
    total_segments = int(np.ceil((end_frame - start_frame) / (segment_duration * fps)))

    while segment_count < total_segments:
        # Calculate current start time in seconds
        current_start_time = start_seconds + (segment_count * segment_duration)

        # Process each segment (video + audio + text) using ffmpeg
        process_segment_with_ffmpeg(video_path, current_start_time, segment_duration, segment_count, target_width, target_height, fps, video_name)

        # Move to the next segment
        segment_count += 1

    logging.info('Splitting and text addition completed! Output segments saved in the "Reels" folder.')

# Example usage
video_path = 'Spiderman Homecoming.mkv'  # Path to your input video
split_video_with_ffmpeg(video_path, segment_duration=59, start_time="2:00", end_time="6:00")  # Split from 4:00 to 6:00

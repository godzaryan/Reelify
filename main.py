import os.path
import shutil
import os
from fontTools.misc.plistlib import totree
from textual import on
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Middle, Center
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static, Input, Label, Switch, LoadingIndicator
from textual.color import Gradient
from textual.widgets import ProgressBar
import cv2
import os
import numpy as np
import subprocess
from tqdm import tqdm


def delete_all_files_and_folders(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Loop through all the files and folders in the directory
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Failed to delete file {file_path}: {e}")

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                shutil.rmtree(dir_path)
                print(f"Deleted folder: {dir_path}")
            except Exception as e:
                print(f"Failed to delete folder {dir_path}: {e}")

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

def process_segment_with_ffmpeg(video_path, start_time, segment_duration, segment_count, target_width, target_height, fps, video_name, instagramid):
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
        '-vf', f'scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black,drawtext=text=\'{part_text}\':fontfile={font_path}:fontcolor=white:fontsize=100:bordercolor=black:borderw=2:x=(w-text_w)/2:y=h-th-380,drawtext=text=\'{video_name}\':fontfile={font_path}:fontcolor=red:fontsize=50:bordercolor=black:borderw=2:x=(w-text_w)/2:y=h-th-500, drawtext=text=Follow @{instagramid}:fontfile={font_path2}:fontcolor=white:fontsize=50:bordercolor=black:borderw=2:x=(w-text_w)/2:y=500',  # Resize, pad, and add text
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
        ReelifyConverter.notify(message=f'Error processing segment {segment_count + 1}: {process.stderr.decode()}', title="Error processing segment", severity="error")
    else:
        ReelifyConverter.notify(message=f'Segment {segment_count + 1} processed: {final_output_path}', severity="warning")

def split_video_with_ffmpeg(video_path, instaid, segment_duration=59, start_time="0:00", end_time=None):
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
        process_segment_with_ffmpeg(video_path, current_start_time, segment_duration, segment_count, target_width, target_height, fps, video_name, instaid)

        # Move to the next segment
        segment_count += 1

    ReelifyConverter.notify(message='Splitting and text addition completed! Output segments saved in the "Reels" folder.', title="Export success!", severity="")

class ReelifyLogin(Static):
    username = reactive("")
    password = reactive("")


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "login":
            self.handle_login()

    def handle_login(self):
        print(f"Username: {self.username}, Password: {self.password}")
        self.app.show_converter_ui()

    def watch_username(self, username: str) -> None:
        self.query_one("#username_input").value = username

    def watch_password(self, password: str) -> None:
        self.query_one("#password_input").value = password

    def compose(self) -> ComposeResult:
        yield Label("Login to Reelify", id="login_label")
        yield Label("Username:", id="username_label")
        yield Input(placeholder="Enter username", id="username_input")
        yield Label("Password:", id="password_label")
        yield Input(placeholder="Enter password", password=True, id="password_input")
        yield Button("Login", id="login", variant="success")

class ReelifyConverter(Static):

    video_path = reactive("")
    split_duration = reactive("")
    video_start_time = reactive("")
    video_end_time = reactive("")
    instagram_id = reactive("")
    insta_auto_upload = reactive(False)
    insta_username = reactive("")
    insta_password = reactive("")

    @on(Button.Pressed, "#submit")
    def handle_submit(self):
        print(f"Video Path: {self.video_path}")
        print(f"Split Duration: {self.split_duration}")
        print(f"Video Start Time: {self.video_start_time}")
        print(f"Video End Time: {self.video_end_time}")
        print(f"Instagram ID: {self.instagram_id}")
        print(f"Auto Upload to Instagram: {'On' if self.insta_auto_upload else 'Off'}")
        print(f"Instagram Username: {self.insta_username}, Password: {self.insta_password}")


        #Verifications
        if not os.path.isfile(self.video_path):
            self.notify("Video file doesn't exist at the specified path",title="Error 404", severity="error")
            return

        if int(self.split_duration) <= 0 or int(self.split_duration) > 60:
            self.notify("Enter a valid split duration between 0-60 seconds", title="Spliting error", severity="error")
            return

        #Clean-up directory
        delete_all_files_and_folders("Reels")

        if self.video_end_time == "":
            split_video_with_ffmpeg(self.video_path, instaid=self.instagram_id, segment_duration=int(self.split_duration), start_time=self.video_start_time)
        else:
            split_video_with_ffmpeg(self.video_path, instaid=self.instagram_id, segment_duration=int(self.split_duration), start_time=self.video_start_time, end_time=self.video_end_time)


    @on(Input.Changed, "#video_path_input")
    def on_video_path_change(self, event: Input.Changed) -> None:
        self.video_path = event.value

    @on(Input.Changed, "#split_duration_input")
    def on_split_duration_change(self, event: Input.Changed) -> None:
        self.split_duration = event.value

    @on(Input.Changed, "#video_start_time_input")
    def on_video_start_time_change(self, event: Input.Changed) -> None:
        self.video_start_time = event.value

    @on(Input.Changed, "#video_end_time_input")
    def on_video_end_time_change(self, event: Input.Changed) -> None:
        self.video_end_time = event.value

    @on(Input.Changed, "#instagram_id_input")
    def on_instagram_id_change(self, event: Input.Changed) -> None:
        self.instagram_id = event.value

    @on(Switch.Changed, "#auto_upload_switch")
    def on_switch_changed(self, event: Switch.Changed) -> None:
        self.insta_auto_upload = event.value
        print(f"Auto upload to Instagram: {'On' if self.insta_auto_upload else 'Off'}")

    @on(Input.Changed, "#insta_username_input")
    def on_instagram_username_change(self, event: Input.Changed) -> None:
        self.insta_username = event.value

    @on(Input.Changed, "#insta_password_input")
    def on_instagram_password_change(self, event: Input.Changed) -> None:
        self.insta_password = event.value

    def compose(self) -> ComposeResult:
        with Center():
            yield Label("\n\nReelify - Automated movies to reel converter\n\n", id="title")
        yield Label("Video Path [full path of the video]:", id="video_path_label")
        yield Input(placeholder="Enter video path", id="video_path_input", value="D:\\input.mp4")
        yield Label("Split Duration [max 60]:", id="split_duration_label")
        yield Input(placeholder="Enter split duration [max 60 seconds]", id="split_duration_input", value="60")
        yield Label("Video Start Time:", id="video_start_time_label")
        yield Input(placeholder="Enter video start time", id="video_start_time_input", value="00:00")
        yield Label("Video End Time:", id="video_end_time_label")
        yield Input(placeholder="Enter video end time [leave empty for end of the video]", id="video_end_time_input")
        yield Label("Instagram ID:", id="instagram_id_label")
        yield Input(placeholder="Enter Instagram ID [will be displayed on each video]", id="instagram_id_input", value="")
        yield Label("Auto Upload to Instagram:", id="auto_upload_label")
        yield Switch(id="auto_upload_switch")
        yield Label("Instagram Username:", id="insta_username_label")
        yield Input(placeholder="Enter Instagram username", id="insta_username_input")
        yield Label("Instagram Password:", id="insta_password_label")
        yield Input(placeholder="Enter Instagram password", password=True, id="insta_password_input")
        with Center():
            yield Button("Submit", id="submit", variant="success")
        gradient = Gradient.from_colors(
            "#881177",
            "#aa3355",
            "#cc6666",
            "#ee9944",
            "#eedd00",
            "#99dd55",
            "#44dd88",
            "#22ccbb",
            "#00bbcc",
            "#0099cc",
            "#3366bb",
            "#663399",
        )
        with Center():
            yield ProgressBar(total=100, gradient=gradient)



class Reelify_AI(App):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        #yield LoadingIndicator(disabled=True)
        #yield ScrollableContainer(ReelifyLogin(), id="login_form")
        yield ScrollableContainer(ReelifyConverter(), id="converter_form")

    def show_converter_ui(self) -> None:
        self.query_one("#login_form").remove()
        self.mount(ScrollableContainer(ReelifyConverter(), id="converter_form"))


if __name__ == "__main__":
    app = Reelify_AI()
    app.run()

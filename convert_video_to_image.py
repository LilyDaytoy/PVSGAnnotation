# python convert_video_to_image.py
import os
import subprocess

# Define the working variables
name = "Teaser_v14"  # you can change the name as required
maskvideo_dir = os.path.join('./data', 'data_' + name, "release/maskvideos")
videomask_dir = os.path.join('./data', 'data_' + name, "release/masks")

if not os.path.exists(videomask_dir):
    os.makedirs(videomask_dir)

# Iterate through all mkv files inside the workdir
for video_name in os.listdir(maskvideo_dir):
    # Check if it's a directory
    maskvideo_path = os.path.join(maskvideo_dir, video_name)
    if os.path.isfile(maskvideo_path) and maskvideo_path.endswith('.mkv'):
        video_path = os.path.join(videomask_dir, video_name.strip('.mkv'))
        if not os.path.exists(video_path):
            os.makedirs(video_path)
        # Construct the FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', os.path.join(maskvideo_dir, video_name),
            '-q:v', '0', 
            '-start_number', '0',
            os.path.join(video_path, '%04d.png'),
        ]
        
        # Execute the FFmpeg command
        subprocess.run(cmd)

print("Processing complete.")

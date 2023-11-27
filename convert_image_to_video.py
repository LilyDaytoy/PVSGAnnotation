# python convert_image_to_video.py
import os
import subprocess

# Define the working variables
name = "Teaser_v14"  # you can change the name as required
maskdir = os.path.join('./data', 'data_' + name, 'masks')
maskvideo_dir = os.path.join('./data', 'data_' + name, "release/maskvideos")

if not os.path.exists(maskvideo_dir):
    os.makedirs(maskvideo_dir)

# Iterate through all directories inside the workdir
for dir_name in os.listdir(maskdir):
    # Check if it's a directory
    maskdir_path = os.path.join(maskdir, dir_name)
    if os.path.isdir(maskdir_path):
        # Construct the FFmpeg command
        cmd = [
            'ffmpeg', 
            '-framerate', '5', 
            '-pattern_type', 'glob', 
            '-i', os.path.join(maskdir_path, '*.png'), 
            '-c:v', 'ffv1', 
            '-q:v', '0', 
            os.path.join(maskvideo_dir, f"{dir_name}.mkv")
        ]
        
        # Execute the FFmpeg command
        subprocess.run(cmd)

print("Processing complete.")

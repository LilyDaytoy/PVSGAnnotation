import os
import shutil

# Set the main directory name
main_dir = "data"
project_name = "data_EpicKitchen_v8"

# Get a list of all directories starting with "data_EpicKitchen_v8_"
sub_dirs = [name for name in os.listdir(main_dir) if name.startswith(f"{project_name}_")]

# Iterate over the subdirectories
for sub_dir in sub_dirs:
    mask_dir = os.path.join(main_dir, sub_dir, "final_masks")  # Path to the 'mask' directory in the subdirectory
    dest_dir = os.path.join(main_dir, project_name)  # Destination directory in the main directory
    
    # Create the destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Copy the 'mask' directory to the destination directory
    shutil.copytree(mask_dir, os.path.join(dest_dir, "final_masks"))

print("Directory copying complete.")

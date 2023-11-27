# python programs/temp_rebase.py Task_0129_v10
import os
import glob
import sys

data_dir = sys.argv[1]

work_dir = f"./data/data_{data_dir}/sa_{data_dir}/"
video_list = [video_id for video_id in os.listdir(work_dir) if video_id != 'classes']

for video_id in video_list:
    # specify your path
    path = f"./data/data_{data_dir}/sa_{data_dir}/{video_id}"

    for file in glob.glob(os.path.join(path, "*.png")):
        if not file.endswith("___save.png"):
            os.remove(file)

    for file in glob.glob(os.path.join(path, "*.png.json")):
        base = os.path.splitext(file)[0]
        os.rename(file, base + "___pixel.json")

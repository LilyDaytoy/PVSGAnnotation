import os, math
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from tqdm import tqdm
from utils.file_helper import load_file, load_json
import warnings

warnings.filterwarnings("ignore")

def normalize_rgb(color):
    return (color[0]/255, color[1]/255, color[2]/255)


def generate_tagged_masks(data_dir, pass_vids):
    pass_result = load_file(f"./{data_dir}/results.pickle", "pickle")
    pass_result = {x: pass_result[x]['id_map'] for x in pass_vids}
    
    keyframes = load_file(f"./{data_dir}/frames.json", "json")

    class_info = load_file(f"./{data_dir}/class_info.json", "json")
    class_info = class_info['indexes2cates']

    class_info = load_file(f"./{data_dir}/class_info.json", "json")
    class_info = class_info['indexes2cates']

    if 'Ego' in data_dir or 'Epic' in data_dir:
        font = ImageFont.truetype('./programs/utils/OpenSans-Bold.ttf', 24)
    else:
        font = ImageFont.truetype('./programs/utils/OpenSans-Bold.ttf', 12)

    for video_id in tqdm(pass_vids):
        object_dict = pass_result[video_id]
        object_dict = {v: f'{class_info[str(int(k) % 1000)]}_{int(k) // 1000}' 
                    for k, v in object_dict.items() if k != 0}
        if os.path.exists(f'./{data_dir}/final_masks/{video_id}/'):
            mask_dir = 'final_masks'
        else:
            mask_dir = 'masks'
        pngfiles = sorted([f for f in os.listdir(f'./{data_dir}/{mask_dir}/{video_id}/') 
                        if f.endswith('.png')])
        for pngfile in pngfiles:
            sample_img = f'./{data_dir}/{mask_dir}/{video_id}/{pngfile}'
            image = Image.open(sample_img)
            palette_dict = {v: k for k, v in image.palette.colors.items()}
            image = Image.open(sample_img)
            draw = ImageDraw.Draw(image)

            for i, tag_name in object_dict.items():
                centerx, centery = ndimage.center_of_mass(np.array(image)==i)
                text_width, text_height = draw.textsize(tag_name, font=font)
                draw.rectangle([centery-5, centerx-5, 
                                centery-5+text_width, centerx-5+text_height], 
                                fill=(0,0,0))
                if not math.isnan(float(centerx)):
                    draw.text((centery-5, centerx-5), tag_name, font=font, fill=palette_dict[i])

            # a tag to show frame id
            text_width, text_height = draw.textsize(pngfile.strip('.png'), font=font)
            draw.rectangle([10, 10, 10+text_width, 10+text_height], 
                        fill=(0,0,0))
            if pngfile in keyframes[video_id]:
                draw.text((10, 10), pngfile.strip('.png'), font=font, fill='red')
            else:
                draw.text((10, 10), pngfile.strip('.png'), font=font, fill='white')
            
            os.makedirs(f"./{data_dir}/caption_masks/{video_id}/", exist_ok=True)
            image.save(f"./{data_dir}/caption_masks/{video_id}/{pngfile}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='process masks and images to generate mask-overlayed video')
    parser.add_argument('--data_dir', type=str, help='which data you want to read')
    args = parser.parse_args()
    all_frames = load_json(args.data_dir+'/frames.json')
    generate_tagged_masks(args.data_dir, list(all_frames.keys()))

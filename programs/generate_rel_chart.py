from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
import numpy as np
import os
from tqdm import tqdm
import warnings
from utils.file_helper import load_file, load_json
from utils.annotator_helper import get_video_metadata, process_excel_relations
import sys

warnings.filterwarnings("ignore")

data_dir = sys.argv[1]


def normalize_rgb(color):
    return (color[0]/255, color[1]/255, color[2]/255)


def get_color_by_luminance(rgb_color):
    luminance = rgb_color[0] * 0.2126 + rgb_color[1] * 0.7152 + rgb_color[2] * 0.0722
    if luminance < 140:
        return (200, 200, 200)
    else:
        return (0, 0, 0)

# def get_color_by_luminance(rgb_color):
#     return (255-rgb_color[0], 255-rgb_color[1], 255-rgb_color[2])

# anno_df_pass = load_file("./PVSG.csv", "csv")
# anno_df_pass = anno_df_pass[anno_df_pass['Verification Status'] == "TORUN"].reset_index()
# pass_vids = list(anno_df_pass['Video_ID'])
# pass_vids = [pass_vid.strip('\n') for pass_vid in pass_vids]

frame_path = f"./data/data_{data_dir}/frames.json"
frames_dict = load_json(frame_path)
pass_vids = list(frames_dict)
# pass_vids = ['1155_5810255954']

class_info = load_file(f"./data/data_{data_dir}/class_info.json", "json")
class_info = class_info['indexes2cates']

pass_result = load_file(f"./data/data_{data_dir}/results.pickle", "pickle")
pass_result = {x: pass_result[x]['id_map'] for x in pass_vids}

metadata = dict()
image_root = f"./data/data_{data_dir}/images"
for vid in pass_vids:
    metadata[vid] = get_video_metadata(vid, image_root)

relations = load_file(f"./data/data_{data_dir}/relations_str.json", "json")

# for video_id in tqdm(['1155_5810255954']):
for video_id in tqdm(pass_vids):
    old_object_dict = pass_result[video_id]
    object_dict = {}
    for k, v in old_object_dict.items():
        if k != 0:
            if int(k) // 1000 != 0:
                object_dict[v] = f'{class_info[str(int(k) % 1000)]}-{int(k) // 1000}'
            else:
                object_dict[v] = f'{class_info[str(int(k) % 1000)]}'

        # object_dict = {v: f'{class_info[str(int(k) % 1000)]}-{int(k) // 1000}' 
        #             for k, v in object_dict.items() if k != 0}
        
    object2color_dict = dict(zip(object_dict.values(), object_dict.keys()))

    # start process video
    chart_width = metadata[video_id]['width']
    duration = metadata[video_id]['duration']
    num_frame = metadata[video_id]['no_frames']

    relation_dict = relations[video_id]
    if not relation_dict:
        relation_list = []
    else:
        relation_list = list(relation_dict)

    # start process frames
    if os.path.exists(f'./data/data_{data_dir}/final_masks/{video_id}/'):
        mask_dir = 'final_masks'
    else:
        mask_dir = 'masks'
    pngfiles = sorted([f for f in os.listdir(f'./data/data_{data_dir}/{mask_dir}/{video_id}/') 
                    if f.endswith('.png')])
    for pngfile in pngfiles:
        # # save text caption on the masks
        sample_img = f'./data/data_{data_dir}/{mask_dir}/{video_id}/{pngfile}'
        image = Image.open(sample_img)
        palette_dict = {v: k for k, v in image.palette.colors.items()}
        # draw = ImageDraw.Draw(image)

        # for i, tag_name in object_dict.items():
        #     centerx, centery = ndimage.center_of_mass(np.array(image)==i)
        #     text_width, text_height = draw.textsize(tag_name)
        #     draw.rectangle([centery-5, centerx-5, 
        #                     centery-5+text_width, centerx-5+text_height], 
        #                     fill=(0,0,0))
        #     draw.text((centery-5, centerx-5), tag_name, fill=palette_dict[i])
        
        # text_width, text_height = draw.textsize(pngfile.strip('.png'))
        # draw.rectangle([10, 10, 10+text_width, 10+text_height], 
        #                 fill=(0,0,0))
        # draw.text((10, 10), pngfile.strip('.png'), fill='white')

        # os.makedirs(f"./caption_masks/{video_id}/", exist_ok=True)
        # image.save(f"./caption_masks/{video_id}/{pngfile}")

        # save a timeline chart

        # Create an image
        chart_height = 15 + len(relation_list) * 13
        chart = Image.new("RGB", (chart_width, chart_height), (255, 255, 255))

        # Create a draw object
        draw_bar = ImageDraw.Draw(chart)
        font = ImageFont.truetype('./programs/utils/OpenSans-Bold.ttf', size=10)

        # Draw the progress bar
        bar_height = 5
        draw_bar.rectangle([0, 0, chart_width, bar_height], 
                    fill=(0, 0, 0))

        # Draw the dot and time tags
        dot_interval = chart_width/10
        time_interval = duration/10
        for i in range(11):
            dot_x = i*dot_interval
            dot_y = bar_height/2
            draw_bar.ellipse([dot_x-1, dot_y-1, dot_x+1, dot_y+1], fill=(255, 255, 255))
            tag_x = dot_x - 21
            tag_y = dot_y - 2
            time = time_interval*i
            draw_bar.text((tag_x, tag_y), f"{time:.1f}s", fill=(255, 0, 0), font=font)

        # Draw the relation bar
        bar_height = 10
        for i, relation_entry in enumerate(relation_list):
            s, o, r, relation_durations = relation_entry
            for slot_i, relation_duration in enumerate(relation_durations):
                start_time = relation_duration[0] / num_frame * chart_width
                if slot_i == 0:
                    text_start = start_time
                start_height = 10 + (bar_height + 3) * i
                relation_length = relation_duration[1] - relation_duration[0]
                try:
                    slot_color = palette_dict[object2color_dict[s.strip('-0')]]
                    draw_bar.rectangle([start_time, start_height,
                                        start_time + relation_length / num_frame * chart_width, 
                                        start_height + bar_height], 
                                        fill = slot_color)
                except Exception as e:
                    import traceback
                    print("An error occurred:", str(e))
                    print("Here is the traceback:")
                    traceback.print_exc()
                    print(relation_duration)
                    import pdb; pdb.set_trace()
            
            relation_entry = f'{s} {r} {o}'
            text_width, _ = draw_bar.textsize(relation_entry)

            if text_start + text_width <= chart_width:
                draw_bar.text((text_start, start_height), relation_entry, 
                               fill=get_color_by_luminance(slot_color))
            else:
                draw_bar.text((chart_width-text_width, start_height), relation_entry, 
                              fill=get_color_by_luminance(slot_color))
        # Draw the time position indicator
        frame_id = int(pngfile.strip('.png'))
        indicator_x = frame_id / num_frame * chart_width
        draw_bar.line([indicator_x, 0, indicator_x, chart_height], 
                fill=(255, 0, 0), width=2)
        os.makedirs(f"./data/data_{data_dir}/relation_charts/{video_id}/", exist_ok=True)
        chart.save(f"./data/data_{data_dir}/relation_charts/{video_id}/{pngfile}")

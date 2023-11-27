# basic 
import numpy as np
from PIL import Image
from collections import defaultdict
from pathlib import Path
import pandas as pd
import re

# tools
from utils.file_helper import load_file, save_file, make_dir_if_not_exist, copy_folder_to_dir
from utils.annotator_helper import instance_decode, instance_decode_all_videos, get_video_metadata, process_dur, process_excel_status, process_excel_relations

def instance_decode(code, indexes2cates):
    # eg code = 1001 -> class=indexes2cates['1'], instance-id: 1
    code = int(code)
    category, attribute_id = None, None
    if code == 0:
        return category, attribute_id
    class_id = code % 1000
    category = indexes2cates[str(class_id)]
    attribute_id = code // 1000 # if attribute_id == 0 -> stuff
    return category, attribute_id  # return "adult-1" format; None: 'background'; category!=None, attr_id=0 -> stuff


def instance_decode_all_videos(id_map_result, indexes2cates):
    pass1_map = defaultdict(dict)
    for vid, id_map in id_map_result.items():
        for code, palette_id in id_map.items():
            code = int(code)
            category, attr_id = instance_decode(code, indexes2cates)
            pass1_map[vid][palette_id] = dict(category=category, attr_id=attr_id)
    return pass1_map

def get_video_metadata(vid, image_root):
    image_root = Path(image_root)
    vid_folder = image_root / vid
    images = list(vid_folder.rglob("*.png"))
    no_frames = len(images)
    duration = no_frames / 5
    first_frame = Image.open(str(images[0]))
    height, width = first_frame.height, first_frame.width
    return dict(no_frames=no_frames, height=height, width=width, fps=5, duration=duration)



def process_time_like_format(time_str):
    time_str = time_str.strip('0')
    time_tokens = re.split('[:.]+', time_str)
    if len(time_tokens) == 3: # [m, s.s]
        fid = int(time_tokens[0])*60*5 + round(float(time_tokens[1]+"."+time_tokens[2]) * 5)
    else: # s.s
        fid = round(float(time_tokens[0]+"."+time_tokens[1]) * 5)
    return fid

    

def process_dur(dur_str):
    # dur_str = "07.200-10.000" or "0010-0030"; return [10,30]
    start = dur_str.split("-")[0].strip()
    end = dur_str.split("-")[1].strip()
    if ":" in start or ":" in end:
        if ":" in start:
            start_id = process_time_like_format(start)
        else:
            start_id = round(float(start) * 5) 
        if ":" in end:
            end_id = process_time_like_format(end)
        else:
            end_id = round(float(end) * 5)

    else:
        if start != "0000" and type(eval(start.lstrip('0'))) == float:
            start_id = round(float(start) * 5)  # ??? frame id start from 0
            end_id = round(float(end) * 5) 
        else:
            start_id = int(start)
            end_id = int(end)
            return [start_id, end_id] # for frame_id format, no need -1, already same with frame id
    if start_id != 0:
        start_id = start_id - 1
    end_id = end_id -1
    return [start_id, end_id]  # modify here, indicate index, frame_id starts from 0!!! unfiy with no ":" case!
        

def process_excel_status(status_str, vid_metadata):
    status_processed = defaultdict(list)
    obj_statuses = status_str.strip().split("\n")
    for obj_status in obj_statuses:
        if not obj_status:
            continue
        if ":" not in obj_status: # whole length
            obj_action = obj_status.strip()
            obj = obj_action.split(" ")[0]
            action = obj_action.split(" ")[1]
            status_processed[obj].append(dict(action=action, dur=[0, vid_metadata['no_frames'] - 1]))
        else:
            tokens = obj_status.split(":", 1)  # remember to just split once, since there are time format
            obj_action = tokens[0].strip()
            dur = process_dur(tokens[1].strip().replace(" ", "")) 
            obj = obj_action.split(" ")[0]
            action = obj_action.split(" ")[1]
            status_processed[obj].append(dict(action=action, dur=dur))
    
    # merge same action
    status_final = dict()
    for obj, action_durs in status_processed.items():
        this_actions = defaultdict(list)
        for action_dur_pair in action_durs:
            this_actions[action_dur_pair['action']].append(action_dur_pair['dur'])
        status_final[obj] = this_actions

    return status_final

def process_excel_relations(relation_str, vid_metadata):
    relation_dict = defaultdict(list)
    all_relations = re.split('[\n]+', relation_str.strip()) # in case for \n\n
    for relation in all_relations:
        if not relation:
            continue
        if ":" not in relation:
            dur = [0, vid_metadata['no_frames'] - 1]
            relation_dict[relation.strip()].append(dur)
        else:
            relation_tokens = relation.split(":", 1)
            dur = process_dur(relation_tokens[1].strip())
            relation_dict[relation_tokens[0].strip()].append(dur)
    return relation_dict

def object_anno_map_instance_id(palette_map_vid):
    return {v['category']+"-"+str(v['attr_id']):k for k, v in palette_map_vid.items() if v['category'] is not None}


def split_relation_str(relation_triplet):
    tokens = relation_triplet.strip().split(" ")
    s = tokens[0]
    o = tokens[-1]
    p = " ".join(tokens[1:-1])
    p = p.replace(" the", "")  # drop 'the' manualy
    return s, o, p

def replace_relation_with_sop_id(relation_vid, obj_anno_map_vid):
    if relation_vid == None:
        return None
    relation_vid_replace_id = []
    for relation_triplet, durs in relation_vid.items():
        s, o, p = split_relation_str(relation_triplet)
        if s in obj_anno_map_vid.keys() and o in obj_anno_map_vid.keys():
            s, o = obj_anno_map_vid[s], obj_anno_map_vid[o]
            sop_dur = [s, o, p, durs]
            relation_vid_replace_id.append(sop_dur)
    return relation_vid_replace_id

# get video list
anno_df_pass = load_file("./PVSG-Annotation.csv", "csv")
anno_df_pass = anno_df_pass[anno_df_pass['Quality\nCheck\n(incomplete, torun, pass)'] == "TORUN"].reset_index()
pass_vids = list(anno_df_pass['Video_ID'])
pass_vids = [pass_vid.strip('\n') for pass_vid in pass_vids]

# # copy panoptic masks
# source_root = "./final_masks"
# # source_root = "./data/temporal_outs/pred_masks"
# target_root = "./pvsg_dataset/masks"
# for folder in pass_vids:
#     copy_folder_to_dir(folder, source_root, target_root)

# # copy raw extracted frames as 5fps
# source_root = "./frame"
# target_root = "./pvsg_dataset/images"
# for folder in pass_vids:
#     copy_folder_to_dir(folder, source_root, target_root)

# get palette_map
class_info = load_file("./data/class_info.json", "json")
class_info = class_info['indexes2cates']

pass_result = load_file("./data/results.pickle", "pickle")
pass_result = {x: pass_result[x]['id_map'] for x in pass_vids}

# palette panoptic mask color_id decode to "category-id"
pass_map = instance_decode_all_videos(pass_result, class_info)
save_file(pass_map, "./data/palette_map.json", "json")

# metadata
metadata = dict()
image_root = "./data/images"
for vid in pass_vids:
    metadata[vid] = get_video_metadata(vid, image_root)
save_file(metadata, "./data/metadata.json", "json")

# status
status = dict()
for i in range(len(anno_df_pass.index)):
    row = anno_df_pass.iloc[i]
    vid = row["Video_ID"]
    status_str = row["Status"]
    if pd.isnull(status_str):
        status[vid] = None
    else:
        status[vid] = process_excel_status(status_str, metadata[vid])
save_file(status, "./data/status.json", "json")

relations = dict()
for i in range(len(anno_df_pass.index)):
    row = anno_df_pass.iloc[i]
    vid = row["Video_ID"]
    if vid == "1007_6631583821":
        relations[vid] = None
        continue
    print(vid)
    relation_str = row['Relations']
    if relation_str is np.nan:
        relations[vid] = None
    else: 
        print(relation_str)
        relations[vid] = process_excel_relations(relation_str, metadata[vid])
save_file(relations, "./data/relations_pvsg_demo.json", "json")

# object_anno_map_instance_id
object_anno_map = dict()
for vid in pass_vids:
    object_anno_map[vid] = object_anno_map_instance_id(pass_map[vid])
save_file(object_anno_map, "./data/obj_anno_map.json", "json")


# merging all info
def get_objects_info_vid(palette_map_vid, status_vid):
    objects = []
    for key, instance_info in palette_map_vid.items():
        if key == 0:
            continue
        anno_obj = instance_info['category']+"-"+str(instance_info['attr_id'])
        this_obj = dict()
        this_obj['object_id'] = key
        this_obj['category'] = instance_info['category']
        this_obj['is_thing'] = instance_info['attr_id'] != 0
        if status_vid == None:
            this_obj['status'] = []  # some video got no status (all actions are included in relations)
        else:
            this_obj['status'] = status_vid.get(anno_obj, []) # some objects have no status (but others have)
        objects.append(this_obj)
    return objects

pvsg_objects = dict()
for vid in pass_vids:
    palette_map_vid = pass_map[vid]
    status_vid = status[vid]
    pvsg_objects[vid] = get_objects_info_vid(palette_map_vid, status_vid)
save_file(pvsg_objects, "./data/pvsg_objects.json", "json")

def split_relation_str(relation_triplet):
    tokens = relation_triplet.strip().split(" ")
    s = tokens[0]
    o = tokens[-1]
    p = " ".join(tokens[1:-1])
    p = p.replace(" the", "")  # drop 'the' manualy
    return s, o, p

def replace_relation_with_sop_id(relation_vid, obj_anno_map_vid):
    if relation_vid == None:
        return None
    relation_vid_replace_id = []
    for relation_triplet, durs in relation_vid.items():
        s, o, p = split_relation_str(relation_triplet)
        if s in obj_anno_map_vid.keys() and o in obj_anno_map_vid.keys():
            s, o = obj_anno_map_vid[s], obj_anno_map_vid[o]
            sop_dur = [s, o, p, durs]
            relation_vid_replace_id.append(sop_dur)
    return relation_vid_replace_id

pvsg_relations = dict()
for vid in pass_vids:
    relation_vid = relations[vid]
    object_anno_map_vid = object_anno_map[vid]
    pvsg_relations[vid] = replace_relation_with_sop_id(relation_vid, object_anno_map_vid)
save_file(pvsg_relations, "./data/relations.json", "json")

# merge all pvsg annotation
pvsg_full = []
for vid in pass_vids:
    vid_dict = dict()
    vid_dict['video_id'] = vid
    vid_dict['objects'] = pvsg_objects[vid]
    vid_dict['meta'] = metadata[vid]
    vid_dict['relations'] = pvsg_relations[vid]
    pvsg_full.append(vid_dict)

save_file(pvsg_full, "./pvsg_dataset/pvsg.json", "json")

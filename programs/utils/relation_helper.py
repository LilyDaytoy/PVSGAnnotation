import numpy as np
from PIL import Image
from collections import defaultdict
from pathlib import Path
import pandas as pd
import re

from .file_helper import load_file, save_file, make_dir_if_not_exist, copy_folder_to_dir
from .annotator_helper import instance_decode, process_dur, process_excel_status, process_excel_relations

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

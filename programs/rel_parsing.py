import os
import numpy as np
from PIL import Image
from collections import defaultdict
from pathlib import Path
import pandas as pd
import re
from utils.file_helper import load_file, save_file
from utils.relation_helper import process_excel_status, \
                                  process_excel_relations

# srun -p regular python rel_parsing.py

task_id = 'EpicKitchen' # 'Task_0129','Task_0205','Task_0219', 'val', 'Pipeline', 'Teaser', 'Ego4D', 'EpicKitchen'
for task_subid in [1,2,3,4,5]:
    print(task_subid, 'starts......')
    working_dir = os.path.join('../data', f'data_{task_id}_v17_{task_subid}')
    # df_full = load_file(os.path.join(working_dir, 'val_v8.csv'), "csv")

    df_pass = load_file(f'{working_dir}/{task_id}.csv', "csv")
    # df_pass = df_full[df_full['task_id']==task_id]
    video_list = list(df_pass['video_id'])
    video_list = [video_name.strip('\n') for video_name in video_list 
                if isinstance(video_name,str)]

    video_list = os.listdir(os.path.join(working_dir, 'masks'))
    df_pass = df_pass[df_pass['video_id'].isin(video_list)]

    from utils.annotator_helper import instance_decode_all_videos, \
                                    get_video_metadata, \
                                    object_anno_map_instance_id

    # get palette_map
    class_info = load_file(f"{working_dir}/class_info.json", "json")
    class_info = class_info['indexes2cates']

    pass_result = load_file(f"{working_dir}/results.pickle", "pickle")
    pass_result = {x: pass_result[x]['id_map'] for x in video_list}

    # palette panoptic mask color_id decode to "category-id"
    pass_map = instance_decode_all_videos(pass_result, class_info)
    save_file(pass_map, f"{working_dir}/palette_map.json", "json")

    # metadata
    metadata = dict()
    image_root = f"{working_dir}/images"
    for vid in video_list:
        metadata[vid] = get_video_metadata(vid, image_root)
    save_file(metadata, f"{working_dir}/metadata.json", "json")

    # relation
    relations = dict()
    status = dict()
    for i in range(len(df_pass.index)):
        row = df_pass.iloc[i]
        vid = row["video_id"]
        relation_str = row['relation']
        status_str = '' # always empty in this version
        status[vid] = process_excel_status(status_str, metadata[vid])
        if relation_str is np.nan:
            relations[vid] = None
        else:
            try:
                relations[vid] = process_excel_relations(relation_str, metadata[vid])
            except Exception as e:
                print(vid)
                print(relation_str)
                print("An error occurred:", e)

    # object_anno_map_instance_id
    object_anno_map = dict()
    for vid in video_list:
        object_anno_map[vid] = object_anno_map_instance_id(pass_map[vid])
    save_file(object_anno_map, f"{working_dir}/obj_anno_map.json", "json")

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
    for vid in video_list:
        palette_map_vid = pass_map[vid]
        status_vid = status[vid]
        pvsg_objects[vid] = get_objects_info_vid(palette_map_vid, status_vid)
    save_file(pvsg_objects, f"{working_dir}/pvsg_objects.json", "json")


    relation_classes = []
    # Open the file in read-only mode
    with open('../relation.txt', 'r') as file:
        # Read the entire contents of the file
        for line in file.readlines():
            relation_classes.append(line.strip('\n'))

    stuff = ["floor", "ground", "grass", "rock", "tree", "ceiling", \
            "wall", "snow", "sky", "water", "sand"]

    def split_relation_str(relation_triplet):
        tokens = relation_triplet.strip().split(" ")
        s = tokens[0]
        o = tokens[-1]
        p = " ".join(tokens[1:-1])
        p = p.replace(" the", "")  # drop 'the' manualy
        return s, o, p

    def replace_relation_with_sop_id(vid, relation_vid, obj_anno_map_vid):
        if relation_vid == None:
            return None
        relation_vid_replace_id = []
        relation_vid_with_word = []
        for relation_triplet, durs in relation_vid.items():
            s, o, r = split_relation_str(relation_triplet)
            
            # ignore id when meeting s and o
            for item in stuff:
                if item in s:
                    s = item.split('-')[0] + '-0'
                    
                if item in o:
                    o = item.split('-')[0] + '-0'
            
            # ignore triplet if s or o is wrong
            if s in obj_anno_map_vid.keys() and o in obj_anno_map_vid.keys():
                s_id, o_id = obj_anno_map_vid[s], obj_anno_map_vid[o]
                
                if r not in relation_classes:
                    print(vid, relation_triplet)
                
                sop_dur = [s_id, o_id, r, durs]
                relation_vid_replace_id.append(sop_dur)
                
                sop_str = [s, o, r, durs]
                relation_vid_with_word.append(sop_str)

            else:
                print(relation_triplet, durs)
        
        return relation_vid_replace_id, relation_vid_with_word

    pvsg_relations = dict()
    pvsg_relations_str = dict()
    for vid in video_list:
        relation_vid = relations[vid]
        object_anno_map_vid = object_anno_map[vid]
        pvsg_relations[vid], pvsg_relations_str[vid] = \
                replace_relation_with_sop_id(vid, relation_vid, object_anno_map_vid)
    save_file(pvsg_relations, f"{working_dir}/relations.json", "json")
    save_file(pvsg_relations_str, f"{working_dir}/relations_str.json", "json")

    df_pass['Revised Relation'] = ''

    for video_id in video_list:
        row_index = df_pass.loc[df_pass['video_id'] == video_id].index[0]
        full_rel_str = ''
        for triplet_list in pvsg_relations_str[video_id]:
            s, o, r, durs = triplet_list
            for dur in durs:
                # make sure the time is good
                if dur[0] >= dur[1]:
                    print('incorrect time for', video_id, triplet_list)
                
                if 'behind' in r:
                    rel_str = f'{o} in front of {s}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'in front of'
                
                elif 'under' in r:
                    rel_str = f'{o} over {s}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'over'
                    
                elif r in ['hugging', 'patting', 'hugging with', 'petting']:
                    rel_str = f'{s} caressing {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'caressing'
                    
                elif r in ['shaking with', 'holding hands with']:
                    rel_str = f'{s} shaking hand with {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'shaking hand with'
                    
                elif r in ['besides']:
                    rel_str = f'{s} beside {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'beside'
                    
                elif r in ['towards', 'walking to', 'walking towards', 'running to', 'jumping to']:
                    rel_str = f'{s} towards {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'toward'
                    
                elif r in ['talking with']:
                    rel_str = f'{s} talking to {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'talking to'
                    
                elif r in ['on top of']:
                    rel_str = f'{s} on {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'on'
                    
                elif r in ['picking up']:
                    rel_str = f'{s} picking {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'picking'
                    
                elif r in ['tossing&biting']:
                    rel_str = f'{s} biting {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'biting'
                
                elif r in ['waving']:
                    rel_str = f'{s} swinging {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'swinging'

                elif r in ['reading', 'smiling to', 'clapping to', 'wathching', 'watching']:
                    rel_str = f'{s} looking at {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'looking at'
                    
                elif 'beside' in r:
                    rel_str = f'{s} beside {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                    r = 'beside'
                    
                else:
                    rel_str = f'{s} {r} {o}: {dur[0]:04d}-{dur[1]:04d}\n'
                
                if r in relation_classes:
                    full_rel_str = full_rel_str + rel_str
                    
        df_pass.loc[row_index, 'Revised Relation'] = full_rel_str

    df_pass.to_csv(f"{working_dir}/updated_relation_{task_id}.csv", index=False)

    len(df_pass)

    def replace_with_number(match, mapping_dict):
        if ',' in match.group(1):
            elements = match.group(1).split(',')
            replaced = ','.join([str(mapping_dict.get(e, e)) for e in elements])
            return '(' + replaced + ')'
        else:
            return '(' + str(mapping_dict.get(match.group(1), match.group(1))) + ')'

    def convert_dc_list(dc_str, mapping_dict):
        dc_list = []
        for entry in dc_str.split('\n'):
            if not entry.strip():  # Skip empty entries
                continue
            time, description = entry.split(':', 1)
            description = re.sub(r'\(([^)]+)\)', lambda m: replace_with_number(m, mapping_dict), description)
            dc_list.append({
                "time": time, 
                "description": description.strip()
            })

        return dc_list

    def convert_qa_list(qa_str, mapping_dict):
        formatted_data = []
        for entry in qa_str.strip().split("\n"):
            if not entry.strip():  # Skip empty entries
                continue
            time, qa_pairs = entry.split(':', 1)
            question_str, answer_str = qa_pairs.split('Q:', 1)[-1].split('A:', 1)
            question_str = re.sub(r'\(([^)]+)\)', lambda m: replace_with_number(m, mapping_dict), question_str)
            answer_str = re.sub(r'\(([^)]+)\)', lambda m: replace_with_number(m, mapping_dict), answer_str)
            formatted_data.append({
                    'time': time,
                    'question': question_str.strip(),
                    'answer': answer_str.strip()
                })
        return formatted_data

    # # description
    # dc_dict = dict()
    # qa_dict = dict()
    # sm_dict = dict()
    # for i in range(len(df_pass.index)):
    #     row = df_pass.iloc[i]
    #     vid = row["video_id"]
    #     print(vid)
    #     mapping_dict = object_anno_map[vid]
    #     dc_dict[vid] = convert_dc_list(row['阶段性描述'], mapping_dict)
    #     qa_dict[vid] = convert_qa_list(row['问答标注'], mapping_dict)
    #     sm_dict[vid] = row['概述']

    # description
    dc_dict = dict()
    qa_dict = dict()
    sm_dict = dict()
    for i in range(len(df_pass.index)):
        row = df_pass.iloc[i]
        vid = row["video_id"]
        print(vid)
        mapping_dict = object_anno_map[vid]
        dc_dict[vid] = convert_dc_list(row['description'], mapping_dict)
        qa_dict[vid] = convert_qa_list(row['QA'], mapping_dict)
        sm_dict[vid] = row['summary']

    print(metadata[vid])

    # merge all pvsg annotation
    pvsg_full = []
    for vid in video_list:
        vid_dict = dict()
        vid_dict['video_id'] = vid
        metadata[vid]['num_frames'] = metadata[vid]['no_frames']
        del metadata[vid]['no_frames']
        vid_dict['meta'] = metadata[vid]
        vid_dict['objects'] = pvsg_objects[vid]
        vid_dict['relations'] = pvsg_relations[vid]
        vid_dict['captions'] = dc_dict[vid]
        vid_dict['qa_pairs'] = qa_dict[vid]
        vid_dict['summary'] = sm_dict[vid]
        pvsg_full.append(vid_dict)

    import json
    with open(f"{working_dir}/pvsg_{task_id}.json", "w") as outfile:
        json.dump(pvsg_full, outfile, indent=4)

    print(task_id)

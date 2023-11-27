# basic packages
import os
import os.path as osp
from turtle import pd
from tqdm import tqdm
from PIL import Image
import shutil
import argparse
# helper functions
from utils.file_helper import make_dir_if_not_exist, load_json, save_json, load_csv, save_pickle
from utils.sa_postprocessor import _palette, map_ids_to_palette_range_singel_frame, \
                  get_pan_masks_all_key_frames, get_id_map_all_key_frames



def sa_to_palette(csv_dir, sa_folderpath, work_dir, frame_root):
    make_dir_if_not_exist(work_dir)

    # link images -- prepare aot folder
    print("Start preparing aot input image folder...")
    save_root = os.path.abspath(osp.join(work_dir, "images"))

    if 'Epic' in work_dir:
        os.system(f'ln -s /mnt/lustre/jkyang/CVPR23/openpvsg/data/epic_kitchen/frames/ {save_root}')
    elif 'Ego4D' in work_dir:
        os.system(f'ln -s /mnt/lustre/jkyang/CVPR23/openpvsg/data/ego4d/frames/ {save_root}')
    else:
        os.system(f'ln -s /mnt/lustre/jkyang/CVPR23/openpvsg/data/vidor/frames/ {save_root}')

    # load excel annotation notes
    if csv_dir == 'none':
        subfolders = [d for d in os.listdir(sa_folderpath) 
                      if os.path.isdir(os.path.join(sa_folderpath, d)) and d not in ['cat_teaser', 'classes']]
        frames = dict()
        for subfolder in subfolders:
            frame_ids = [f.split('_')[0] for f in os.listdir(os.path.join(sa_folderpath, subfolder)) if f.endswith('.png')]
            frames[subfolder] = sorted(frame_ids)
    else:
        pvsg_df = load_csv(csv_dir)
        pvsg_torun = pvsg_df[pvsg_df['Quality\nCheck\n(incomplete, torun, pass)'] == "TORUN"].reset_index()
        # get vid & fid annotations
        frames = dict()
        for i in list(pvsg_torun.index):
            row = pvsg_torun.iloc[i]
            vid = row['Video_ID']
            frame_ids = [x.split(":")[0] + '.png' for x in row['Frame ID (from back to front)'].strip().split('\n')]
            frames[vid] = frame_ids
        
    save_json(frames, osp.join(work_dir, "frames.json"))
    # frames = load_json(osp.join(work_dir, "frames.json"))
    # import pdb; pdb.set_trace();

    # classes
    classes = load_json(osp.join(sa_folderpath, "classes/classes.json"))
    id2cates = {x['id']: x['name'] for x in classes}
    classes_ids = [x['id'] for x in classes]
    classes_ids2indexes = dict(zip(classes_ids, range(1, len(classes_ids) + 1)))
    indexes2cates = {classes_ids2indexes[x]: id2cates[x] for x in classes_ids}
    class_info = dict(classe=classes, indexes2cates=indexes2cates)
    save_json(class_info, osp.join(work_dir, "class_info.json"))

    # prepare "large number" pan_mask + id_map for all sa annotations
    print("Start preparing 'large number' pan_mask for sa annotations..")
    results = dict()
    for vid, fids in frames.items():
        print("processing framse for video {}".format(vid))
        anno_folder = osp.join(sa_folderpath, vid)
        pan_masks = get_pan_masks_all_key_frames(fids, anno_folder, classes_ids2indexes)
        id_map = get_id_map_all_key_frames(pan_masks)
        results[vid] = dict(pan_masks=pan_masks, id_map=id_map)
    save_pickle(results, osp.join(work_dir, "results.pickle"))

    # save mask palette images
    print("Start preparing palette mask images...")
    save_root = osp.join(work_dir, "masks")
    make_dir_if_not_exist(save_root)
    for vid, vid_results in tqdm(results.items()):
        save_folder = osp.join(save_root, vid)
        make_dir_if_not_exist(save_folder)
        
        id_map = vid_results['id_map']
        pan_masks = vid_results['pan_masks']
        for frame_name, pan_mask in pan_masks.items():
            save_dir = osp.join(save_folder, frame_name)
            pan_mask_P = map_ids_to_palette_range_singel_frame(pan_mask, id_map)
            mask_img = Image.fromarray(pan_mask_P).convert("P")
            mask_img.putpalette(_palette)
            mask_img.save(save_dir)

    # # copy images -- prepare aot folder
    # print("Start preparing aot input image folder...")
    # save_root = os.path.abspath(osp.join(work_dir, "images"))
    # import pdb; pdb.set_trace();
    # os.system(f'ln -s /mnt/lustre/jkyang/CVPR23/openpvsg/data/vidor/frames/ /mnt/lustre/jkyang/CVPR23/annotation_fine/data/data_Task_0205_v3/images)


    # make_dir_if_not_exist(save_root)

    # import pdb; pdb.set_trace();
    # os.system('ln -s ')

    # for vid in tqdm(frames.keys()):
    #     src = osp.join(frame_root, vid)
    #     dst = osp.join(save_root, vid)
    #     # shutil.copytree(src, dst)
    #     if not os.path.exists(dst):
    #         os.symlink(src, dst)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='sa to palette')
    parser.add_argument('--csv_dir', type=str, default='none', help='annotation csv file path')
    parser.add_argument('--sa_folderpath', type=str, help='the path of the downloaded superannotate folder')
    parser.add_argument('--work_dir', type=str, default='./data', help='where to save all your results')
    parser.add_argument('--frame_root', type=str, default='./frame', help='where to save all your results')

    args = parser.parse_args()
    sa_to_palette(args.csv_dir, args.sa_folderpath, args.work_dir, args.frame_root)

import cv2
import os
import argparse
from PIL import Image
import numpy as np
import os.path as osp
from tqdm import tqdm
from skimage.morphology.binary import binary_dilation

from utils.sa_postprocessor import _palette
from utils.file_helper import load_file, load_json, make_dir_if_not_exist

import multiprocessing

color_palette = np.array(_palette).reshape(-1, 3)

def overlay(image, mask, colors=[255, 0, 0], cscale=1, alpha=0.4):
    colors = np.atleast_2d(colors) * cscale

    im_overlay = image.copy()
    object_ids = np.unique(mask)

    for object_id in object_ids[1:]:
        # Overlay color on  binary mask

        foreground = image * alpha + np.ones(
            image.shape) * (1 - alpha) * np.array(colors[object_id])
        binary_mask = mask == object_id

        # Compose image
        im_overlay[binary_mask] = foreground[binary_mask]

        countours = binary_dilation(binary_mask) ^ binary_mask
        im_overlay[countours, :] = 0

    return im_overlay.astype(image.dtype)


def overlay_mask_to_video(vid, 
                          image_folder,
                          mask_folder,
                          chart_folder,
                          output_folder,
                          video_fps=5,
                         ):
    make_dir_if_not_exist(output_folder)

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    output_video_path = os.path.join(
            output_folder, '{}_with_mask_chart.mp4'.format(vid))    
    
    # specific video folder
    vid_image_folder = osp.join(image_folder, vid)
    vid_mask_folder = osp.join(mask_folder, vid)
    vid_chart_folder = osp.join(chart_folder, vid)
    # height, width
    sample_img = Image.open(osp.join(vid_image_folder, "0000.png"))
    sample_chart = Image.open(osp.join(vid_chart_folder, "0000.png"))
    assert sample_img.width == sample_img.width; 'Width should be the same'
    output_height = sample_img.height + sample_chart.height
    output_width = sample_img.width
    videoWriter = cv2.VideoWriter(
                        output_video_path, fourcc, video_fps,
                        (int(output_width), int(output_height)))
    imgs = sorted(os.listdir(vid_image_folder))
    for img in imgs:
        img_dir = os.path.join(vid_image_folder, img)
        mask_dir = os.path.join(vid_mask_folder, img)
        chart_dir = os.path.join(vid_chart_folder, img)
        image = Image.open(img_dir)
        mask = Image.open(mask_dir)
        chart = Image.open(chart_dir)
        overlayed_image = overlay(
                        np.array(image, dtype=np.uint8),
                        np.array(mask, dtype=np.uint8), color_palette, alpha=0.4)
        # videoWriter.write(overlayed_image[..., [2, 1, 0]])
        chart = np.array(chart, dtype=np.uint8)
        concat_img = np.concatenate([overlayed_image, chart], axis=0)
        videoWriter.write(concat_img[..., [2, 1, 0]])

    videoWriter.release()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='process masks and images to generate mask-overlayed video')
    parser.add_argument('--frames_dir', type=str, help='where you save your frames.json')
    parser.add_argument('--image_folder', type=str, default="/mnt/lustre/jkyang/wxpeng/mask2former/pvsg_v2/images")
    parser.add_argument('--mask_folder', type=str, default="/mnt/lustre/jkyang/wxpeng/mask2former/pvsg_v2/final_masks")
    parser.add_argument('--chart_folder', type=str, default="/mnt/lustre/jkyang/wxpeng/mask2former/pvsg_v2/relation_charts")
    parser.add_argument('--output_folder', type=str, default="/mnt/lustre/jkyang/wxpeng/mask2former/pvsg_v2/result_videos")
    parser.add_argument('--video_fps', type=int, default=5)
    args = parser.parse_args()

    all_frames = load_json(args.frames_dir)
    make_dir_if_not_exist(args.output_folder)
    
    frames_list = list(all_frames.keys())
    completed_list = [file.split('_with')[0] for file in os.listdir(args.output_folder)]
    frames_list = list(set(frames_list) - set(completed_list))
    print('Number of videos to run: ', len(frames_list))

    num_processes = 10

    with multiprocessing.Pool(num_processes) as pool:
        results = []
        for vid in tqdm(frames_list):
            result = pool.apply_async(overlay_mask_to_video, (vid, args.image_folder, args.mask_folder, args.chart_folder, args.output_folder, args.video_fps))
            results.append(result)
        pool.close()

        for result in results:
            result.wait()
        pool.join()

    print("done")
    print('Number of videos completed: ', len(os.listdir(args.output_folder)))

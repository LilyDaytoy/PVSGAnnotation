# sh scripts/generate_overlayed_video_tag.sh
name=$1
data=data/data_${name}

FRAMES_DIR=$data/frames.json
IMAGE_FOLDER=$data/images
MASK_FOLDER=$data/caption_masks
OUTPUT_FOLDER=$data/tag_videos_${name}

srun -p priority -x SG-IDC2-10-51-5-39 \
python programs/img2video_overlay_mask.py \
--frames_dir ${FRAMES_DIR} \
--image_folder ${IMAGE_FOLDER} \
--mask_folder ${MASK_FOLDER} \
--output_folder ${OUTPUT_FOLDER}

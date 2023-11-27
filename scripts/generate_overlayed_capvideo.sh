FRAMES_DIR=data/frames.json
IMAGE_FOLDER=data/images
MASK_FOLDER=data/caption_masks
OUTPUT_FOLDER=data/result_capvideos

python img2video_overlay_mask.py \
--frames_dir ${FRAMES_DIR} \
--image_folder ${IMAGE_FOLDER} \
--mask_folder ${MASK_FOLDER} \
--output_folder ${OUTPUT_FOLDER}

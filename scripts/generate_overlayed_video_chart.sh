# sh scripts/generate_overlayed_video_chart.sh
name=$1
data=data/data_${name}

FRAMES_DIR=$data/frames.json
IMAGE_FOLDER=$data/images
MASK_FOLDER=$data/caption_masks
CHART_FOLDER=$data/relation_charts
OUTPUT_FOLDER=$data/chart_videos_${name}

srun -p regular -x SG-IDC2-10-51-5-39 \
python programs/img2video_overlay_with_chart.py \
--frames_dir ${FRAMES_DIR} \
--image_folder ${IMAGE_FOLDER} \
--mask_folder ${MASK_FOLDER} \
--chart_folder ${CHART_FOLDER} \
--output_folder ${OUTPUT_FOLDER}

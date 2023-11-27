name=$1
WORK_DIR=./data/data_${name}

SA_FOLDER=$WORK_DIR/sa_$name
FRAME_ROOT=../OpenPVSG/data/vidor/frames

python programs/sa2palette.py \
--sa_folderpath ${SA_FOLDER} \
--work_dir ${WORK_DIR} \
--frame_root ${FRAME_ROOT}

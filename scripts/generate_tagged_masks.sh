name=$1
data_dir=./data/data_${name}

srun -p regular -x SG-IDC2-10-51-5-39 \
python programs/generate_tagged_masks.py \
--data_dir ${data_dir}

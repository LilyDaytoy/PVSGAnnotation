# time sh run_ego.sh
# sleep 30m && ls
# remove the images created in the-previous-run
# curl -o zip_files/EpicKitchen_v17.zip https://files.superannotate.com/18049/122977/1699294151775_c53820b1-22d4-4232-9573-0e822dcf0814
# curl -o zip_files/Ego4D_v17.zip https://files.superannotate.com/18049/123595/1699341720283_3c95f34f-532e-4b7e-bdce-345a6290d259
# name=EpicKitchen_v17_1
name=Ego4D_v17_4
# name=EpicKitchen_v17

workdir=./data/data_$name

# srun -p regular python programs/split_dir.py $name

# if [[ ! $name =~ _v[0-9]+(_[0-9]+)*$ ]]; then
#     # :<<'END_COMMENT'
#     rm -rf $workdir
#     mkdir $workdir
#     srun -p regular unzip -qq ./zip_files/$name.zip -d $workdir/sa_$name
#     # END_COMMENT
# fi

# python programs/temp_rebase.py $name
# python programs/quality_check.py $name
# python programs/paste_id.py $name
# sh scripts/sa2palette.sh $name

if [[ ! $name == val* ]] && [[ ! $name == Teaser* ]] && [[ ! $name == Pipeline* ]]; then
cd aot-benchmark/tools
srun -p priority --mpi=pmi2 --gres=gpu:1 -n1 --ntasks-per-node=1 python pvsg_demo_mf.py $name
cd ../..
fi

desired_path="/mnt/lustre/jkyang/CVPR23/annotation_fine"
current_path=$(pwd)
while [[ $current_path != $desired_path* ]]; do
    echo "Current path: $current_path"
    echo "Changing directory..."
    cd $desired_path
    current_path=$(pwd)
done

# merge masks and generate videos
sh scripts/generate_tagged_masks.sh $name
sh scripts/generate_overlayed_video_tag.sh $name

# merge relation
srun -p regular python programs/generate_rel_chart.py $name
sh scripts/generate_overlayed_video_chart.sh $name

# srun -p ntu --mpi=pmi2 --gres=gpu:1 -n1 --ntasks-per-node=1 python generate_tagged_masks.py
# sh scripts/generate_overlayed_video_tag.sh

# sh scripts/generate_overlayed_video.sh
# srun -p regular python pvsg_vps_parsing.py
# END_COMMENT

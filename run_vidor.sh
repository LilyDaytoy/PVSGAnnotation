# time sh run_vidor.sh
# sleep 30m && ls
# remove the images created in the-previous-run
# curl -o zip_files/Task_0205_v18.zip https://files.superannotate.com/18049/124127/1700500495749_1c2de68a-c807-466e-bd36-cd4749064d93
# curl -o zip_files/Teaser_v14.zip https://files.superannotate.com/18049/110621/1697742333270_f8a615f2-1c3b-4662-931c-9979a9c4fc7b
name=Task_0219_v18 # Task_0129_v17, Task_0205_v17, Task_0219_v17, val_v17, Pipeline_v14, Teaser_v14

workdir=./data/data_$name

# :<<'END_COMMENT'
rm -rf $workdir
mkdir $workdir
unzip -qq ./zip_files/$name.zip -d $workdir/sa_$name

python programs/temp_rebase.py $name

# :<<'END_COMMENT'
python programs/quality_check.py $name
python programs/paste_id.py $name
# END_COMMENT

# :<<'END_COMMENT'
# prepare for masks
sh scripts/sa2palette.sh $name
# END_COMMENT

# :<<'END_COMMENT'
if [[ ! $name == val* ]] && [[ ! $name == Teaser* ]] && [[ ! $name == Pipeline* ]]; then
# aot propagation
cd aot-benchmark/tools
srun -p priority --mpi=pmi2 --gres=gpu:1 -n1 --ntasks-per-node=1 --quotatype auto python pvsg_demo_mf.py $name
cd ../..
fi
# END_COMMENT

# :<<'END_COMMENT'
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
# END_COMMENT

# ffmpeg -framerate 5 -pattern_type glob -i '*.png' -c:v ffv1 -q:v 0 output.mkv
# ffmpeg -i output.mkv -q:v 0 frame_%04d.png

# cd /mnt/lustre/jkyang/CVPR23/annotation_fine/data/data_val_v12
# srun -p regular zip -r tag_videos_val_v12.zip tag_videos_val_v12/ 
# cd /mnt/lustre/jkyang/CVPR23/annotation_fine

# merge relation
srun -p regular python programs/generate_rel_chart.py $name
sh scripts/generate_overlayed_video_chart.sh $name

# srun -p regular python programs/generate_rel_chart.py Pipeline_v7
# sh scripts/generate_overlayed_video_chart.sh Teaser_v14

# srun -p ntu --mpi=pmi2 --gres=gpu:1 -n1 --ntasks-per-node=1 python generate_tagged_masks.py
# sh scripts/generate_overlayed_video_tag.sh

# sh scripts/generate_overlayed_video.sh
# srun -p ntu python pvsg_vps_parsing.py
# END_COMMENT

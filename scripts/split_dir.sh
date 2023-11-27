#!/bin/bash
# sh scripts/split_dir.sh

keyword=EpicKitchen_v9 # Ego4D_v9

src="./data/data_$keyword/sa_$keyword"
dst="./data/"

dirs=( "$src"/* )

dir_count=${#dirs[@]}

# Define the number of new directories you want to create.
# You should adjust this value according to your requirements.
num_new_dirs=5

dirs_per_new_dir=$(( (dir_count + num_new_dirs - 1) /- num_new_dirs ))

for (( i=0; i<"${dir_count}"; i+=dirs_per_new_dir )); do
    new_dir="${dst}/data_${keyword}_$(( i / dirs_per_new_dir + 1 ))/sa_${keyword}_$(( i / dirs_per_new_dir + 1 ))"
    mkdir -p "$new_dir"
    
    # Copy the "classes" directory to each new directory
    cp -r "${src}/classes" "$new_dir"
    
    for (( j=0; j<dirs_per_new_dir; j++ )); do
        if (( i + j < dir_count )); then
            cp -r "${dirs[i+j]}" "$new_dir"
        fi
    done
done

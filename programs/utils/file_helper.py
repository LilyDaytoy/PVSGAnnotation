import json
import os
import pandas as pd
import pickle
import shutil

def make_dir_if_not_exist(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def load_json(file):
     with open(file, "r") as f:
          return json.load(f)

def save_json(obj, file):
    with open(file, "w") as f:
        json.dump(obj, f)


def load_csv(file):
    with open(file, "r") as f:
        return pd.read_csv(f)

def save_pickle(obj, file):
    with open(file, "wb") as f:
        pickle.dump(obj,f)


def load_file(filepath, format):
    mode = 'r'
    if format == "pickle":
        mode = 'rb'

    result = None
    with open(filepath, mode) as f:
        if format == "json":
            result = json.load(f)
        elif format == "pickle":
            result = pickle.load(f)
        elif format == "csv":
            result = pd.read_csv(f)
        else:
            print("No such file format implemented in loading...")
    return result


def save_file(obj, savepath, format):
    mode = 'w'
    if format == "pickle":
        mode = 'wb'

    with open(savepath, mode) as f:
        if format == "json":
            json.dump(obj, f)
        elif format == "pickle":
            pickle.dump(obj, f)
        elif format == "csv":
            obj.to_csv(f)
        else:
            print("No such file format implemented in saving...")


def make_dir_if_not_exist(path):
    if not os.path.exists(path):
	    os.makedirs(path)


def copy_folder_to_dir(folder_name, src_dir, dst_dir):
    folder_dir = os.path.join(src_dir, folder_name)
    dst_dir = os.path.join(dst_dir, folder_name)
    make_dir_if_not_exist(dst_dir)
    files = sorted(os.listdir(folder_dir))
    for file in files:
        file_dir = os.path.join(folder_dir, file)
        shutil.copy(file_dir, dst_dir)

import json
import glob

import sys 

data_dir = sys.argv[1]

# stdoutOrigin=sys.stdout
# sys.stdout = open(f"./data/data_{data_dir}/quality.txt", "w")

classes = []
with open('classes.txt', 'r') as reader:
    for line in reader.readlines():
        classes.append(line.strip('\n'))

replace_dict = {
    'P01_10': ['spatula-2', 'knife-2'],
    'P01_13': ['others-1', 'bottle-2'],
    'P03_05': ['rag-1', 'towel-1'],
    'P04_16': ['vegetable-1', 'simmering-1'],
    'P04_26': ['rag-1', 'towel-1'],
    'P04_27': ['rag-1', 'towel-1'],
    'P04_32': ['rag-1', 'towel-1'],
    'P04_33': ['rag-1', 'towel-1'],
    'P05_05': ['others-1', 'beverage-1'],
    'P06_14': ['cake-1', 'cookie-1'],
    '29501ed1-77bb-4f53-aeb2-d062d5f568a9': ['carpet-2', 'carpet-1'],
    '3751590f-3a97-4024-845b-b800e5df6166': ['others-1', 'cover-1'],
    '8be918b2-c819-4a84-98dc-5fe24835a4ac': ['cloth-1', 'mat-1'],
    '92f8142a-25aa-444a-ae37-43fae4f95f18_1': ['bucket-1', 'basket-1'],
    '92f8142a-25aa-444a-ae37-43fae4f95f18_2': ['others-2', 'rock-0'],
    'b275f09c-5dd2-4e8c-97de-edc1f0c8222b': ['towel-1', 'tag-3'],
    'dbeb569a-b3ff-47db-8189-fee05064cf20': ['others-1', 'condiment-1']
}

    # '92f8142a-25aa-444a-ae37-43fae4f95f18_1': ['others-3', 'rock-0'],

def decompose_string(s):
    className, attrName = s.split('-')
    return className, attrName

def change(old_str, new_str, data):
    old_class, old_attr = decompose_string(old_str)
    new_class, new_attr = decompose_string(new_str)

    # Iterate through the data
    for item in data['instances']:
        # import pdb; pdb.set_trace();
        if item['className'] == old_class:
            for attr in item['attributes']:
                if attr['name'] == old_attr:
                    item['className'] = new_class
                    attr['name'] = new_attr
                    break
    return data

json_files = glob.glob(f"./data/data_{data_dir}/sa_{data_dir}/*/*.json")
incorrect_files = []
for json_file in json_files:
    video_id = json_file.split('/')[-2]
    if video_id in replace_dict.keys():
        with open(json_file, 'r') as reader:
            json_content = json.load(reader)
        old_str, new_str = replace_dict[video_id]
        json_content = change(old_str, new_str, json_content)
        print(json_file)
        print('save')
        with open(json_file, 'w') as json_file_io:
            json.dump(json_content, json_file_io)

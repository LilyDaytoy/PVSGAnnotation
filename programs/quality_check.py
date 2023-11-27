import json
import glob

import sys 

data_dir = sys.argv[1]

stdoutOrigin=sys.stdout
sys.stdout = open(f"./data/data_{data_dir}/quality.txt", "w")

classes = []
with open('classes.txt', 'r') as reader:
    for line in reader.readlines():
        classes.append(line.strip('\n'))

json_files = glob.glob(f"./data/data_{data_dir}/sa_{data_dir}/*/*.json")
incorrect_files = []
for json_file in json_files:
    if json_file == f'./data/data_{data_dir}/sa_{data_dir}/classes/classes.json':
        continue
    with open(json_file, 'r') as reader:
        json_content = json.load(reader)
        
        for instance in json_content['instances']:
            instance_class = instance['className']
            if instance_class not in classes:
                print(json_file)
                print('incorrect class: ', instance_class)
                incorrect_files.append(json_file.split('/')[4])

            if instance['attributes'] == []:
                if instance_class not in ['floor', 'ground', 'grass', 'rock', 'tree', 'ceiling', 'wall', 'snow', 'sky', 'water', 'sand']:
                    print(json_file)
                    print('missing id: ', instance_class)
                    incorrect_files.append(json_file.split('/')[4])
            
            else:
                if instance['attributes'][0]['name'] == "":
                    if instance_class not in ['floor', 'ground', 'grass', 'rock', 'tree', 'ceiling', 'wall', 'snow', 'sky', 'water', 'sand']:
                        print(json_file)
                        print('missing id: ', instance_class)
                        incorrect_files.append(json_file.split('/')[4])

print(set(incorrect_files))

sys.stdout.close()
sys.stdout=stdoutOrigin

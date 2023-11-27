# srun -p regular python programs/split_dir.py
import os, sys
import shutil
import zipfile

def unzip_file(zip_path, output_path):
    """
    Unzip the file to the given directory
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_path)

def split_directory(keyword, split_dict):
    """
    Split the directory into multiple directories according to the given dict
    """
    main_dir = f"./data/data_{keyword}/sa_{keyword}"
    for split_num, dir_names in split_dict.items():
        # Create a new directory for each split
        split_dir = f"./data/data_{keyword}_{split_num}/sa_{keyword}_{split_num}"
        os.makedirs(split_dir, exist_ok=True)

        # Move directories to new split directory
        for dir_name in dir_names:
            src_dir = os.path.join(main_dir, dir_name)
            if os.path.exists(src_dir):
                shutil.copytree(src_dir, os.path.join(split_dir, dir_name),
                                dirs_exist_ok=True)
            else:
                print(f"Directory {dir_name} not found in {main_dir}")

def main(keyword):
    # keyword = "Ego4D_v12" # "EpicKitchen_v12", "Ego4D_v12"
    zip_file_path = f"./zip_files/{keyword}.zip"
    output_dir = f"./data/data_{keyword}/sa_{keyword}"

    # Unzip the file
    unzip_file(zip_file_path, output_dir)

    if keyword[1] == 'g':
        # Define the split dict
        split_dict = {
            1: ['classes', '03f2ed96-1719-427d-acf4-8bf504f1d66d', '0be30efe-9d71-4698-8304-f1d441aeea58_1', '0be30efe-9d71-4698-8304-f1d441aeea58_2', '0cb2dd94-afb1-4e30-a62f-724f34d81777_1', '0cb2dd94-afb1-4e30-a62f-724f34d81777_2', '181a2c5e-5b2c-4436-ba8d-26c7d7db4bb8', '1bfe5ac2-cbf8-4364-8a30-60d97dd395df_1', '1bfe5ac2-cbf8-4364-8a30-60d97dd395df_2', '1bfe5ac2-cbf8-4364-8a30-60d97dd395df_3', '22cc4d54-34be-4580-983a-9e710e831c16'],
            2: ['classes', '29501ed1-77bb-4f53-aeb2-d062d5f568a9', '3751590f-3a97-4024-845b-b800e5df6166', '3b609b23-f91d-43da-9918-ce928181f53f', '43b0205a-4e3c-46a7-9d1c-c04ead730180', '45e463b2-bdd5-407a-ab5c-8a5c5534e078', '4e4f9d6e-7e27-4b14-81ab-60867cd418ad', '54097e7a-3a92-485e-a7d7-33d07b346d41', '5a163ffe-970a-4f67-a9e7-2ce340eaf6b1', '5c676dd6-d0d7-479d-b107-abf5857be8e0'],
            3: ['classes', '62a49b90-a91c-4263-8b4f-fb23879bd730', '6e0a6558-c212-4cab-b374-007671edb59c_1', '6e0a6558-c212-4cab-b374-007671edb59c_2', '6f874e09-ea55-460c-8796-0ceae180bebc', '725d6aca-b665-40cf-8b60-07d564c370aa', '760a2d62-d580-4422-b32f-2c4fc9a35c7c_1', '760a2d62-d580-4422-b32f-2c4fc9a35c7c_2', '85f21d37-73c8-42e8-bdda-1ff89dd6eb15', '8be918b2-c819-4a84-98dc-5fe24835a4ac', '90621e59-7800-49ab-aeb8-c7725f87a7d8', '92f8142a-25aa-444a-ae37-43fae4f95f18_1', '92f8142a-25aa-444a-ae37-43fae4f95f18_2', '97eb4a18-87f2-47f2-9a67-11fca6bdae64', 'a05683ad-b4a2-4af6-94ab-b32bc7c97b79', 'a383d099-5eef-48b5-9d1b-5e2d97632725'],
            4: ['classes', 'a906a4c6-a0ad-41a3-ba79-59f151d955e4', 'a95dcb11-e878-47c0-9a3a-c2252aae40ba', 'b0df76ae-085a-4e4e-869a-61062dbb717f', 'b275f09c-5dd2-4e8c-97de-edc1f0c8222b', 'c20407ac-83d6-4c84-88cb-63bced9d456b', 'c2e6d807-d903-4b64-98e1-2c07ca700c78_1', 'c2e6d807-d903-4b64-98e1-2c07ca700c78_2', 'c2e6d807-d903-4b64-98e1-2c07ca700c78_3', 'ceda965f-3f19-4b80-ae6b-5256fee5f6aa'],
            5: ['classes', 'd1d4a1b3-a651-4eb8-bb7f-8d66982854fa', 'd2222009-a717-4b16-91ce-6399c5bb798a', 'd62f9c1c-7d01-4350-a0fb-ec553dad8cf2', 'dbeb569a-b3ff-47db-8189-fee05064cf20', 'dfaa7536-3453-4eab-8d70-f1624d640060', 'e127fc34-0de5-41b0-ab68-7d5574bcf613', 'e2e4e68a-b464-4876-82ec-009b5a3cb257', 'e58a1cd6-cf82-4477-b8a3-8f749ebceffe_1', 'e58a1cd6-cf82-4477-b8a3-8f749ebceffe_2', 'ec2e69c1-fd07-48ec-adff-0b2cf3ab25b6', 'eed8d8d7-6773-493b-af21-880f0acb063a', 'f1085fc6-4c8f-4ad2-9cd9-caa9dafe1b11', 'ff5d68b9-8486-467d-ad87-93c31e7cdcca']
        }
    else:
        split_dict = {
            1: ['classes', 'P01_03', 'P01_10', 'P01_13', 'P02_10', 'P02_11', 'P02_13', 'P02_14', 'P03_05', 'P03_06', 'P04_07', 'P04_16'],
            2: ['classes', 'P04_26', 'P04_27', 'P04_32', 'P04_33', 'P05_05', 'P06_01', 'P06_12', 'P06_13', 'P06_14', 'P07_11', 'P08_07', 'P08_08'],
            3: ['classes', 'P08_14', 'P08_20', 'P09_07', 'P11_06', 'P11_11', 'P11_13', 'P11_19', 'P11_23', 'P13_02', 'P13_06', 'P13_10', 'P14_05'],
            4: ['classes', 'P14_06', 'P15_01', 'P15_05', 'P17_01', 'P18_02', 'P18_12', 'P19_02', 'P19_05', 'P19_06', 'P20_07', 'P25_01', 'P26_01'],
            5: ['classes', 'P26_02', 'P26_34', 'P26_36', 'P27_03', 'P28_10', 'P28_13', 'P28_19', 'P28_21']
        }


    # Split the directory
    split_directory(keyword, split_dict)

if __name__ == "__main__":
    main(sys.argv[1])
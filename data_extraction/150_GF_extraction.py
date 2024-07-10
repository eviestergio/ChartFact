# Grabs 50 data entries from ChartQA from Pew
# 50 data entries from FigureQA train
# 40 entries from PlotQA train, 5 from PlotQA test, 5 from PlotQA val
# No duplicate imgname or image_index
# Random selection 

# name the new dataset 1_extracted_data_150_GF

import os
import json
import random
import shutil
from collections import defaultdict

# Define the paths for the source (external hard drive) and destination (repository)
external_storage = '/Volumes/Backup'  # Path to the external hard drive
source_folder = 'seed_datasets'
destination_folder = '1_extracted_data_150_GF'
repository_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))  # Get one level up from the script's directory

# Define the full paths
source_path = os.path.join(external_storage, source_folder)
destination_path = os.path.join(repository_path, destination_folder)

# Create the destination folder if it does not exist
os.makedirs(destination_path, exist_ok=True)

# Function to copy folder structure and empty JSON files, excluding files in png and tables folders
def copy_structure(src, dst):
    for root, dirs, files in os.walk(src):
        # Create the corresponding directories in the destination
        relative_path = os.path.relpath(root, src)
        dest_dir = os.path.join(dst, relative_path)
        os.makedirs(dest_dir, exist_ok=True)

        for file in files:
            # Skip files in png and tables folders
            if 'png' in root.split(os.sep) or 'tables' in root.split(os.sep) or 'png-1' in root.split(os.sep) or 'png-2' in root.split(os.sep):
                continue

            file_path = os.path.join(root, file)
            dest_file_path = os.path.join(dest_dir, file)

            if file.endswith('.json'):
                # Create an empty JSON file
                with open(dest_file_path, 'w') as f:
                    json.dump({}, f)
            else:
                # Create an empty file
                open(dest_file_path, 'w').close()

# Function to copy selected entries and their corresponding files (PNG and tables if present)
def copy_selected_entries_and_files(src, dst, dataset, folder, file_pairs, num_entries, unique_identifiers):
    copied_files = set()
    selected_entries = []
    entries_available = True

    for qa_pairs_file, num in file_pairs:
        qa_pairs_path = os.path.join(src, dataset, folder, qa_pairs_file)
        png_folder_path = os.path.join(src, dataset, folder, 'png')
        tables_folder_path = os.path.join(src, dataset, folder, 'tables') if dataset == 'ChartQA' else None
        destination_qa_pairs_path = os.path.join(dst, dataset, folder, qa_pairs_file)
        destination_png_folder_path = os.path.join(dst, dataset, folder, 'png')
        destination_tables_folder_path = os.path.join(dst, dataset, folder, 'tables') if tables_folder_path else None

        # Check if necessary source folders exist
        if not os.path.exists(qa_pairs_path):
            print(f"The source file {qa_pairs_path} does not exist.")
            continue
        if not os.path.exists(png_folder_path):
            print(f"The source folder {png_folder_path} does not exist.")
            continue
        if tables_folder_path and not os.path.exists(tables_folder_path):
            print(f"The source folder {tables_folder_path} does not exist.")
            continue

        # Ensure the destination folders exist
        os.makedirs(destination_png_folder_path, exist_ok=True)
        if tables_folder_path:
            os.makedirs(destination_tables_folder_path, exist_ok=True)

        # Load the JSON data
        with open(qa_pairs_path, 'r') as f:
            qa_pairs = json.load(f)

        # Ensure qa_pairs is a list
        if isinstance(qa_pairs, dict) and 'qa_pairs' in qa_pairs:
            qa_pairs = qa_pairs['qa_pairs']

        print(f"Loaded {len(qa_pairs)} entries from {qa_pairs_path}")

        if dataset == 'ChartQA':
            imgname_dict = defaultdict(list)
            for entry in qa_pairs:
                if 'imgname' in entry and len(entry['imgname']) <= 9:
                    imgname_dict[entry['imgname']].append(entry)

            if len(imgname_dict) == 0:
                print(f"No valid entries found in {qa_pairs_path}.")
                continue

            all_entries = []
            for imgname, entries in imgname_dict.items():
                all_entries.extend(entries)

            if len(all_entries) < num:
                print(f"Not enough valid entries in {qa_pairs_path}. Required: {num}, Found: {len(all_entries)}")
                entries_available = False

            selected_imgnames = set()
            while len(selected_entries) < num and all_entries:
                entry = random.choice(all_entries)
                if entry['imgname'] not in selected_imgnames:
                    selected_entries.append(entry)
                    selected_imgnames.add(entry['imgname'])
                    unique_identifiers.add(entry['imgname'])
                    all_entries.remove(entry)

            print(f"Selected {len(selected_entries)} entries from {qa_pairs_path}")

        else:
            image_index_dict = defaultdict(list)
            for entry in qa_pairs:
                if 'image_index' in entry:
                    image_index_dict[entry['image_index']].append(entry)

            if len(image_index_dict) == 0:
                print(f"No valid entries found in {qa_pairs_path}.")
                continue

            all_entries = []
            for image_index, entries in image_index_dict.items():
                all_entries.extend(entries)

            if len(all_entries) < num:
                print(f"Not enough valid entries in {qa_pairs_path}. Required: {num}, Found: {len(all_entries)}")
                entries_available = False

            selected_indices = set()
            while len(selected_entries) < num and all_entries:
                entry = random.choice(all_entries)
                if entry['image_index'] not in selected_indices:
                    selected_entries.append(entry)
                    selected_indices.add(entry['image_index'])
                    unique_identifiers.add(entry['image_index'])
                    all_entries.remove(entry)

            print(f"Selected {len(selected_entries)} entries from {qa_pairs_path}")

        with open(destination_qa_pairs_path, 'w') as f:
            json.dump(selected_entries, f, indent=4)

        for entry in selected_entries:
            if dataset == 'ChartQA' and 'imgname' in entry:
                imgname = entry['imgname']
                src_png_file = os.path.join(png_folder_path, imgname)
                dst_png_file = os.path.join(destination_png_folder_path, imgname)
                if os.path.exists(src_png_file):
                    shutil.copyfile(src_png_file, dst_png_file)
                    copied_files.add(dst_png_file)
                else:
                    print(f"PNG file {src_png_file} does not exist.")
                if tables_folder_path:
                    table_file = f"{imgname.replace('.png', '')}.csv"
                    src_table_file = os.path.join(tables_folder_path, table_file)
                    dst_table_file = os.path.join(destination_tables_folder_path, table_file)
                    if os.path.exists(src_table_file):
                        shutil.copyfile(src_table_file, dst_table_file)
            elif 'image_index' in entry:
                png_file = f"{entry['image_index']}.png"
                src_png_file = os.path.join(png_folder_path, png_file)
                dst_png_file = os.path.join(destination_png_folder_path, png_file)
                if os.path.exists(src_png_file):
                    shutil.copyfile(src_png_file, dst_png_file)
                    copied_files.add(dst_png_file)
                else:
                    print(f"PNG file {src_png_file} does not exist.")

    return len(selected_entries), len(copied_files), entries_available

# Function to handle special case for FigureQA test and val qa_pairs JSON files
def handle_figureqa_test_val(src, dst, folder):
    qa_pairs_files = [f for f in os.listdir(os.path.join(src, 'FigureQA', folder)) if f.startswith('qa_pairs') and f.endswith('.json')]
    png_folders_to_exclude = ['png-1', 'png-2']

    for qa_pairs_file in qa_pairs_files:
        qa_pairs_path = os.path.join(src, 'FigureQA', folder, qa_pairs_file)
        destination_qa_pairs_path = os.path.join(dst, 'FigureQA', folder, qa_pairs_file)

        if os.path.exists(qa_pairs_path):
            # Create an empty JSON file at the destination
            with open(destination_qa_pairs_path, 'w') as f:
                json.dump({}, f)

    for root, dirs, files in os.walk(os.path.join(src, 'FigureQA', folder)):
        for dir in dirs:
            if dir in png_folders_to_exclude:
                destination_dir = os.path.join(dst, 'FigureQA', folder, dir)
                os.makedirs(destination_dir, exist_ok=True)
                # Ensure folders png-1 and png-2 are empty
                for file in os.listdir(os.path.join(root, dir)):
                    file_path = os.path.join(root, dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

# Execute the function to copy structure without files and to copy selected entries and corresponding files
copy_structure(source_path, destination_path)

datasets = ['PlotQA', 'FigureQA', 'ChartQA']
folders = ['train', 'test', 'val']
num_entries = {'train': {'PlotQA': 40, 'FigureQA': 50, 'ChartQA': 40}, 'test': {'PlotQA': 5, 'ChartQA': 5}, 'val': {'PlotQA': 5, 'ChartQA': 5}}
file_counts = {'train': {'FigureQA': [('qa_pairs.json', 50)], 'ChartQA': [('train_human.json', 40)], 'PlotQA': [('qa_pairs.json', 40)]},
               'test': {'FigureQA': [('qa_pairs-1.json', 0), ('qa_pairs-2.json', 0)], 'ChartQA': [('test_human.json', 5)], 'PlotQA': [('qa_pairs.json', 5)]},
               'val': {'FigureQA': [('qa_pairs-1.json', 0), ('qa_pairs-2.json', 0)], 'ChartQA': [('val_human.json', 5)], 'PlotQA': [('qa_pairs.json', 5)]}}

results = {}
unique_identifiers = set()

for dataset in datasets:
    results[dataset] = {}
    for folder in folders:
        if dataset == 'FigureQA' and folder in ['test', 'val']:
            handle_figureqa_test_val(source_path, destination_path, folder)
            results[dataset][folder] = (0, 0)  # No entries or files copied
        else:
            file_pairs = file_counts[folder][dataset]
            num, copied, entries_available = copy_selected_entries_and_files(
                source_path, destination_path, dataset, folder, file_pairs, num_entries[folder][dataset], unique_identifiers)
            if not entries_available:
                print(f"Could not fill {num_entries[folder][dataset]} entries for {dataset}/{folder}")
            results[dataset][folder] = (num, copied)

print(f"The new folder has been created.")
for dataset in results:
    for folder in results[dataset]:
        num_entries, num_files = results[dataset][folder]
        print(f"{dataset}/{folder}: {num_entries} JSON entries, {num_files} PNG files")

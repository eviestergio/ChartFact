import os
import json
import random
import shutil
from collections import defaultdict

# Define the paths for the source (external hard drive) and destination (repository)
external_storage = '/Volumes/Backup'  # Path to the external hard drive
source_folder = 'seed_datasets'
destination_folder = 'seed_datasets-new'
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
            if 'png' in root.split(os.sep) or 'tables' in root.split(os.sep):
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
def copy_selected_entries_and_files(src, dst, dataset, folder, file_pairs, num_entries, duplicate_count):
    copied_files = set()
    selected_entries = []

    for qa_pairs_file, num in file_pairs:
        qa_pairs_path = os.path.join(src, dataset, folder, qa_pairs_file)
        png_folder_path = os.path.join(src, dataset, folder, 'png')
        tables_folder_path = os.path.join(src, dataset, folder, 'tables') if dataset == 'ChartQA' else None
        destination_qa_pairs_path = os.path.join(dst, dataset, folder, qa_pairs_file)
        destination_png_folder_path = os.path.join(dst, dataset, folder, 'png')
        destination_tables_folder_path = os.path.join(dst, dataset, folder, 'tables') if tables_folder_path else None

        # Check if necessary source folders exist
        if not os.path.exists(qa_pairs_path) or not os.path.exists(png_folder_path) or (tables_folder_path and not os.path.exists(tables_folder_path)):
            print(f"The source folder {qa_pairs_path}, {png_folder_path}, or {tables_folder_path} does not exist.")
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

        if dataset == 'ChartQA':
            imgname_dict = defaultdict(list)
            for entry in qa_pairs:
                if 'imgname' in entry:
                    imgname_dict[entry['imgname']].append(entry)

            if len(imgname_dict) == 0:
                print(f"No valid entries found in {qa_pairs_path}.")
                continue

            entries_for_file = []
            while len(entries_for_file) < duplicate_count * 2:
                imgname = random.choice(list(imgname_dict.keys()))
                entries = imgname_dict[imgname]
                if len(entries) >= 2:
                    sample_entries = random.sample(entries, 2)
                else:
                    sample_entries = entries * 2

                if all(entry['imgname'] not in copied_files for entry in sample_entries):
                    entries_for_file.extend(sample_entries)
                    copied_files.update(entry['imgname'] for entry in sample_entries)

            remaining_entries = num - len(entries_for_file)
            all_entries = [entry for entry in qa_pairs if entry not in entries_for_file]
            non_duplicate_entries = []
            while len(non_duplicate_entries) < remaining_entries and all_entries:
                entry = random.choice(all_entries)
                all_entries.remove(entry)
                imgname = entry['imgname']
                if imgname not in copied_files:
                    non_duplicate_entries.append(entry)
                    copied_files.add(imgname)
            entries_for_file.extend(non_duplicate_entries)
        else:
            image_index_dict = defaultdict(list)
            for entry in qa_pairs:
                if 'image_index' in entry:
                    image_index_dict[entry['image_index']].append(entry)

            if len(image_index_dict) == 0:
                print(f"No valid entries found in {qa_pairs_path}.")
                continue

            entries_for_file = []
            while len(entries_for_file) < duplicate_count * 2:
                image_index = random.choice(list(image_index_dict.keys()))
                entries = image_index_dict[image_index]
                if len(entries) >= 2:
                    sample_entries = random.sample(entries, 2)
                else:
                    sample_entries = entries * 2

                if all(f"{entry['image_index']}.png" not in copied_files for entry in sample_entries):
                    entries_for_file.extend(sample_entries)
                    copied_files.update(f"{entry['image_index']}.png" for entry in sample_entries)

            remaining_entries = num - len(entries_for_file)
            all_entries = [entry for entry in qa_pairs if entry not in entries_for_file]
            non_duplicate_entries = []
            while len(non_duplicate_entries) < remaining_entries and all_entries:
                entry = random.choice(all_entries)
                all_entries.remove(entry)
                png_file = f"{entry['image_index']}.png"
                if png_file not in copied_files:
                    non_duplicate_entries.append(entry)
                    copied_files.add(png_file)
            entries_for_file.extend(non_duplicate_entries)

        with open(destination_qa_pairs_path, 'w') as f:
            json.dump(entries_for_file, f, indent=4)

        for entry in entries_for_file:
            if dataset == 'ChartQA' and 'imgname' in entry:
                imgname = entry['imgname']
                src_png_file = os.path.join(png_folder_path, imgname)
                dst_png_file = os.path.join(destination_png_folder_path, imgname)
                if os.path.exists(src_png_file):
                    shutil.copyfile(src_png_file, dst_png_file)
                else:
                    print(f"PNG file {src_png_file} does not exist.")
                if tables_folder_path:
                    table_file = f"{imgname.replace('.png', '')}.csv"
                    src_table_file = os.path.join(tables_folder_path, table_file)
                    dst_table_file = os.path.join(destination_tables_folder_path, table_file)
                    if os.path.exists(src_table_file):
                        shutil.copyfile(src_table_file, dst_table_file)
                    else:
                        print(f"Table file {src_table_file} does not exist.")
            elif 'image_index' in entry:
                png_file = f"{entry['image_index']}.png"
                src_png_file = os.path.join(png_folder_path, png_file)
                dst_png_file = os.path.join(destination_png_folder_path, png_file)
                if os.path.exists(src_png_file):
                    shutil.copyfile(src_png_file, dst_png_file)
                else:
                    print(f"PNG file {src_png_file} does not exist.")

        selected_entries.extend(entries_for_file)

    return len(selected_entries), len(copied_files)

# Function to handle special case for FigureQA test and val qa_pairs JSON files
def handle_figureqa_test_val(src, dst, folder, num_entries):
    qa_pairs_files = [f for f in os.listdir(os.path.join(src, 'FigureQA', folder)) if f.startswith('qa_pairs') and f.endswith('.json')]
    total_entries = 0
    total_files = 0

    for qa_pairs_file in qa_pairs_files:
        qa_pairs_path = os.path.join(src, 'FigureQA', folder, qa_pairs_file)
        destination_qa_pairs_path = os.path.join(dst, 'FigureQA', folder, qa_pairs_file)
        png_folder_name = qa_pairs_file.replace('qa_pairs', 'png').replace('.json', '')
        png_folder_path = os.path.join(src, 'FigureQA', folder, png_folder_name)
        destination_png_folder_path = os.path.join(dst, 'FigureQA', folder, png_folder_name)

        # Ensure the destination png folder is initially empty
        if os.path.exists(destination_png_folder_path):
            shutil.rmtree(destination_png_folder_path)
        os.makedirs(destination_png_folder_path, exist_ok=True)

        # Check if necessary source folders exist
        if not os.path.exists(qa_pairs_path):
            print(f"The source file {qa_pairs_path} does not exist.")
            continue

        # Load the JSON data
        with open(qa_pairs_path, 'r') as f:
            qa_pairs = json.load(f)

        # Ensure qa_pairs is a list
        if isinstance(qa_pairs, dict) and 'qa_pairs' in qa_pairs:
            qa_pairs = qa_pairs['qa_pairs']

        if not qa_pairs:
            print(f"There are no entries in {qa_pairs_path}")
            continue

        # Select random entries, ensuring duplicates
        image_index_dict = defaultdict(list)
        for entry in qa_pairs:
            if 'image_index' in entry:
                image_index_dict[entry['image_index']].append(entry)

        entries_for_file = []
        while len(entries_for_file) < 2 * num_entries:
            if len(entries_for_file) < 2:
                image_index = random.choice(list(image_index_dict.keys()))
                entries = image_index_dict[image_index]
                if len(entries) >= 2:
                    sample_entries = random.sample(entries, 2)
                else:
                    sample_entries = entries * 2
                entries_for_file.extend(sample_entries)
            else:
                image_index = random.choice(list(image_index_dict.keys()))
                entries = image_index_dict[image_index]
                entry = random.choice(entries)
                if entry not in entries_for_file:
                    entries_for_file.append(entry)

        selected_file_entries = random.sample(entries_for_file, num_entries)

        # Write the selected entries to the new JSON file
        with open(destination_qa_pairs_path, 'w') as f:
            json.dump(selected_file_entries, f, indent=4)

        # Copy the corresponding PNG files
        copied_files = set()
        for entry in selected_file_entries:
            if 'image_index' in entry:
                png_file = f"{entry['image_index']}.png"
                src_png_file = os.path.join(png_folder_path, png_file)
                dst_png_file = os.path.join(destination_png_folder_path, png_file)
                if os.path.exists(src_png_file) and png_file not in copied_files:
                    shutil.copyfile(src_png_file, dst_png_file)
                    copied_files.add(png_file)
                else:
                    print(f"PNG file {src_png_file} does not exist or is a duplicate.")

        total_entries += len(selected_file_entries)
        total_files += len(copied_files)

    return total_entries, total_files

# Execute the function to copy structure without files and to copy selected entries and corresponding files
copy_structure(source_path, destination_path)

datasets = ['PlotQA', 'FigureQA', 'ChartQA']
folders = ['train', 'test', 'val']
num_entries = {'train': 80, 'test': 10, 'val': 10}
duplicate_counts = {'train': {'PlotQA': 3, 'FigureQA': 3, 'ChartQA': 3},
                    'test': {'PlotQA': 2, 'FigureQA': 2, 'ChartQA': 2},
                    'val': {'PlotQA': 2, 'FigureQA': 2, 'ChartQA': 2}}

results = {}

figureqa_files = {
    'train': [('qa_pairs.json', 80)],
    'test': [('qa_pairs-1.json', 5), ('qa_pairs-2.json', 5)],
    'val': [('qa_pairs-1.json', 5), ('qa_pairs-2.json', 5)]
}

chartqa_files = {
    'train': [('train_augmented.json', 40), ('train_human.json', 40)],
    'test': [('test_augmented.json', 5), ('test_human.json', 5)],
    'val': [('val_augmented.json', 5), ('val_human.json', 5)]
}

for dataset in datasets:
    results[dataset] = {}
    for folder in folders:
        if dataset == 'FigureQA' and folder in ['test', 'val']:
            num, copied = handle_figureqa_test_val(source_path, destination_path, folder, 5)
        else:
            if dataset == 'FigureQA':
                file_pairs = figureqa_files[folder]
            elif dataset == 'ChartQA':
                file_pairs = chartqa_files[folder]
            else:
                file_pairs = [('qa_pairs.json', num_entries[folder])]

            num, copied = copy_selected_entries_and_files(
                source_path, destination_path, dataset, folder, file_pairs, num_entries[folder], duplicate_counts[folder][dataset])
        results[dataset][folder] = (num, copied)

print(f"The new folder has been created.")
for dataset in results:
    for folder in results[dataset]:
        num_entries, num_files = results[dataset][folder]
        if dataset == 'ChartQA':
            print(f"{dataset}/{folder}: {num_entries} JSON entries, {num_files // 2} PNG files, {num_files // 2} Table files")
        else:
            print(f"{dataset}/{folder}: {num_entries} JSON entries, {num_files} PNG files")

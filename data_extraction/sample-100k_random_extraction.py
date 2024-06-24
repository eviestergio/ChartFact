# Test final 100K data extraction script on the smaller 300 sample
# Creates 244 data entries

import os
import json
import shutil

# Define the paths for the source and destination
source_folder = '/Users/angwang/ChartFC/random_sample_300'  # Absolute path to the source folder
destination_folder = 'sampleseed_datasets-new'  # Updated destination folder name
repository_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))  # Get one level up from the script's directory

# Define the full paths
source_path = source_folder
destination_path = os.path.join(repository_path, destination_folder)

# Debugging: Print paths to ensure they are correct
print(f"Source Path: {source_path}")
print(f"Destination Path: {destination_path}")

# Create the destination folder if it does not exist
os.makedirs(destination_path, exist_ok=True)

def copy_structure(src, dst, exclude_dirs=None):
    """
    Copy the folder structure from src to dst, excluding specified directories.

    Args:
    src (str): Source directory.
    dst (str): Destination directory.
    exclude_dirs (list): List of directories to exclude.
    """
    if exclude_dirs is None:
        exclude_dirs = []

    for root, dirs, files in os.walk(src):
        relative_path = os.path.relpath(root, src)
        if any(excluded in root for excluded in exclude_dirs):
            continue
        dest_dir = os.path.join(dst, relative_path)
        os.makedirs(dest_dir, exist_ok=True)

def copy_chartqa_files(src, dst, folder):
    """
    Copy all JSON entries and their corresponding files (PNG and tables) for ChartQA dataset from src to dst.

    Args:
    src (str): Source directory.
    dst (str): Destination directory.
    folder (str): Folder name within the dataset.
    """
    qa_pairs_files = ['train_augmented.json', 'train_human.json', 'test_augmented.json', 'test_human.json', 'val_augmented.json', 'val_human.json']
    for qa_pairs_file in qa_pairs_files:
        qa_pairs_path = os.path.join(src, 'ChartQA', folder, qa_pairs_file)
        png_folder_path = os.path.join(src, 'ChartQA', folder, 'png')
        tables_folder_path = os.path.join(src, 'ChartQA', folder, 'tables')
        destination_qa_pairs_path = os.path.join(dst, 'ChartQA', folder, qa_pairs_file)
        destination_png_folder_path = os.path.join(dst, 'ChartQA', folder, 'png')
        destination_tables_folder_path = os.path.join(dst, 'ChartQA', folder, 'tables')

        # Check if necessary source folders exist
        if not os.path.exists(qa_pairs_path) or not os.path.exists(png_folder_path) or not os.path.exists(tables_folder_path):
            print(f"The source folder {qa_pairs_path}, {png_folder_path}, or {tables_folder_path} does not exist.")
            continue

        # Ensure the destination folders exist
        os.makedirs(destination_png_folder_path, exist_ok=True)
        os.makedirs(destination_tables_folder_path, exist_ok=True)

        # Load the JSON data
        with open(qa_pairs_path, 'r') as f:
            qa_pairs = json.load(f)

        # Ensure qa_pairs is a list
        if isinstance(qa_pairs, dict) and 'qa_pairs' in qa_pairs:
            qa_pairs = qa_pairs['qa_pairs']

        # Filter valid entries: ensure each entry has a corresponding PNG and CSV file
        valid_entries = []
        for entry in qa_pairs:
            if 'imgname' in entry:
                imgname = entry['imgname']
                src_png_file = os.path.join(png_folder_path, imgname)
                table_file = f"{imgname.replace('.png', '')}.csv"
                src_table_file = os.path.join(tables_folder_path, table_file)
                if os.path.exists(src_png_file) and os.path.exists(src_table_file):  # Validity check
                    valid_entries.append(entry)

        # Write the valid entries to the new JSON file
        with open(destination_qa_pairs_path, 'w') as f:
            json.dump(valid_entries, f, indent=4)

        # Copy the corresponding PNG and table files for valid entries
        for entry in valid_entries:
            imgname = entry['imgname']
            src_png_file = os.path.join(png_folder_path, imgname)
            dst_png_file = os.path.join(destination_png_folder_path, imgname)
            shutil.copyfile(src_png_file, dst_png_file)
            table_file = f"{imgname.replace('.png', '')}.csv"
            src_table_file = os.path.join(tables_folder_path, table_file)
            dst_table_file = os.path.join(destination_tables_folder_path, table_file)
            shutil.copyfile(src_table_file, dst_table_file)

def copy_figureqa_files(src, dst, folder, num_entries):
    """
    Copy selected entries and their corresponding PNG files for FigureQA dataset from src to dst, excluding specific folders.

    Args:
    src (str): Source directory.
    dst (str): Destination directory.
    folder (str): Folder name within the dataset.
    num_entries (int): Number of entries to select.
    """
    qa_pairs_path = os.path.join(src, 'FigureQA', folder, 'qa_pairs.json')
    destination_qa_pairs_path = os.path.join(dst, 'FigureQA', folder, 'qa_pairs.json')
    png_folder_path = os.path.join(src, 'FigureQA', folder, 'png')
    destination_png_folder_path = os.path.join(dst, 'FigureQA', folder, 'png')

    # Check if necessary source folders exist
    if not os.path.exists(qa_pairs_path) or not os.path.exists(png_folder_path):
        print(f"The source folder {qa_pairs_path} or {png_folder_path} does not exist.")
        return 0, 0

    # Ensure the destination folders exist
    os.makedirs(destination_png_folder_path, exist_ok=True)

    # Exclude png-1 and png-2 folders for test and val
    if folder in ['test', 'val']:
        os.makedirs(os.path.join(destination_png_folder_path, 'png-1'), exist_ok=True)
        os.makedirs(os.path.join(destination_png_folder_path, 'png-2'), exist_ok=True)
        with open(os.path.join(dst, 'FigureQA', folder, 'qa_pairs-1.json'), 'w') as f:
            json.dump([], f)
        with open(os.path.join(dst, 'FigureQA', folder, 'qa_pairs-2.json'), 'w') as f:
            json.dump([], f)
        return 0, 0

    # Load the JSON data
    with open(qa_pairs_path, 'r') as f:
        qa_pairs = json.load(f)

    # Ensure qa_pairs is a list
    if isinstance(qa_pairs, dict) and 'qa_pairs' in qa_pairs:
        qa_pairs = qa_pairs['qa_pairs']

    if not qa_pairs:
        print(f"There are no entries in {qa_pairs_path}")
        return 0, 0

    # Select and filter valid entries: ensure each entry has a corresponding PNG file
    valid_entries = []
    copied_files = set()
    for entry in qa_pairs:
        if 'image_index' in entry and len(valid_entries) < num_entries:
            png_file = f"{entry['image_index']}.png"
            src_png_file = os.path.join(png_folder_path, png_file)
            if os.path.exists(src_png_file):  # Validity check
                valid_entries.append(entry)
                copied_files.add(png_file)

    # Write the valid entries to the new JSON file
    with open(destination_qa_pairs_path, 'w') as f:
        json.dump(valid_entries, f, indent=4)

    # Copy the corresponding PNG files for valid entries
    for png_file in copied_files:
        src_png_file = os.path.join(png_folder_path, png_file)
        dst_png_file = os.path.join(destination_png_folder_path, png_file)
        shutil.copyfile(src_png_file, dst_png_file)

    return len(valid_entries), len(copied_files)

def copy_plotqa_files(src, dst, folder, num_entries):
    """
    Copy selected entries and their corresponding PNG files for PlotQA dataset from src to dst.

    Args:
    src (str): Source directory.
    dst (str): Destination directory.
    folder (str): Folder name within the dataset.
    num_entries (int): Number of entries to select.
    """
    qa_pairs_path = os.path.join(src, 'PlotQA', folder, 'qa_pairs.json')
    destination_qa_pairs_path = os.path.join(dst, 'PlotQA', folder, 'qa_pairs.json')
    png_folder_path = os.path.join(src, 'PlotQA', folder, 'png')
    destination_png_folder_path = os.path.join(dst, 'PlotQA', folder, 'png')

    # Check if necessary source folders exist
    if not os.path.exists(qa_pairs_path) or not os.path.exists(png_folder_path):
        print(f"The source folder {qa_pairs_path} or {png_folder_path} does not exist.")
        return 0, 0

    # Ensure the destination folders exist
    os.makedirs(destination_png_folder_path, exist_ok=True)

    # Load the JSON data
    with open(qa_pairs_path, 'r') as f:
        qa_pairs = json.load(f)

    # Ensure qa_pairs is a list
    if isinstance(qa_pairs, dict) and 'qa_pairs' in qa_pairs:
        qa_pairs = qa_pairs['qa_pairs']

    if not qa_pairs:
        print(f"There are no entries in {qa_pairs_path}")
        return 0, 0

    # Select and filter valid entries: ensure each entry has a corresponding PNG file
    valid_entries = []
    copied_files = set()
    for entry in qa_pairs:
        if 'image_index' in entry and len(valid_entries) < num_entries:
            png_file = f"{entry['image_index']}.png"
            src_png_file = os.path.join(png_folder_path, png_file)
            if os.path.exists(src_png_file):  # Validity check
                valid_entries.append(entry)
                copied_files.add(png_file)

    # Write the valid entries to the new JSON file
    with open(destination_qa_pairs_path, 'w') as f:
        json.dump(valid_entries, f, indent=4)

    # Copy the corresponding PNG files for valid entries
    for png_file in copied_files:
        src_png_file = os.path.join(png_folder_path, png_file)
        dst_png_file = os.path.join(destination_png_folder_path, png_file)
        shutil.copyfile(src_png_file, dst_png_file)

    return len(valid_entries), len(copied_files)

def main():
    """
    Main function to execute the script logic.
    Copy folder structure and selected entries with corresponding files.
    """
    # Exclude specific folders for FigureQA
    exclude_dirs = [
        os.path.join('FigureQA', 'test', 'png-1'),
        os.path.join('FigureQA', 'test', 'png-2'),
        os.path.join('FigureQA', 'val', 'png-1'),
        os.path.join('FigureQA', 'val', 'png-2')
    ]
    copy_structure(source_path, destination_path, exclude_dirs=exclude_dirs)

    results = {}

    # Copy all ChartQA entries
    results['ChartQA'] = {}
    for folder in ['train', 'test', 'val']:
        copy_chartqa_files(source_path, destination_path, folder)
        results['ChartQA'][folder] = ('all', 'all')

    # FigureQA
    results['FigureQA'] = {}
    results['FigureQA']['train'] = copy_figureqa_files(source_path, destination_path, 'train', 64)
    
    # Ensure FigureQA test and val folders have empty png-1 and png-2 folders and empty qa_pairs-1.json and qa_pairs-2.json files
    results['FigureQA']['test'] = (0, 0)
    os.makedirs(os.path.join(destination_path, 'FigureQA', 'test', 'png-1'), exist_ok=True)
    os.makedirs(os.path.join(destination_path, 'FigureQA', 'test', 'png-2'), exist_ok=True)
    with open(os.path.join(destination_path, 'FigureQA', 'test', 'qa_pairs-1.json'), 'w') as f:
        json.dump([], f)
    with open(os.path.join(destination_path, 'FigureQA', 'test', 'qa_pairs-2.json'), 'w') as f:
        json.dump([], f)
    
    results['FigureQA']['val'] = (0, 0)
    os.makedirs(os.path.join(destination_path, 'FigureQA', 'val', 'png-1'), exist_ok=True)
    os.makedirs(os.path.join(destination_path, 'FigureQA', 'val', 'png-2'), exist_ok=True)
    with open(os.path.join(destination_path, 'FigureQA', 'val', 'qa_pairs-1.json'), 'w') as f:
        json.dump([], f)
    with open(os.path.join(destination_path, 'FigureQA', 'val', 'qa_pairs-2.json'), 'w') as f:
        json.dump([], f)

    # PlotQA
    results['PlotQA'] = {}
    results['PlotQA']['train'] = copy_plotqa_files(source_path, destination_path, 'train', 64)
    results['PlotQA']['test'] = copy_plotqa_files(source_path, destination_path, 'test', 8)
    results['PlotQA']['val'] = copy_plotqa_files(source_path, destination_path, 'val', 8)

    print(f"The new folder has been created.")
    for dataset in results:
        for folder in results[dataset]:
            num_entries, num_files = results[dataset][folder]
            if dataset == 'ChartQA':
                print(f"{dataset}/{folder}: All JSON entries and corresponding PNG/Table files copied.")
            elif dataset == 'FigureQA' and folder in ['test', 'val']:
                print(f"{dataset}/{folder}: JSON files and PNG folders are empty as specified.")
            else:
                print(f"{dataset}/{folder}: {num_entries} JSON entries, {num_files} PNG files")

if __name__ == "__main__":
    main()

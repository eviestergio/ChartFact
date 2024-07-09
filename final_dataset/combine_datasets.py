# Script to combine all datasets into final dataset, remove seed dataset folders
# Combine/copy all jsons into one json file for each split 
# Combine/copy all pngs into one png folder for each split
# Combine/copy all tables into one tables folder for each split
# Name final folder :5_final_dataset 

import os
import shutil
import json

# Define directories
base_dir = '../4_prompted_data_10'
dest_dir = '5_final_dataset'
data_types = ['train', 'test', 'val']
sources = ['ChartQA', 'FigureQA', 'PlotQA']
file_types = ['png', 'tables']

# Define specific subdirectory paths for ChartQA, FigureQA, and PlotQA
specific_subdirs = {
    'ChartQA': {
        'train': {
            'png': 'train/png',
            'tables': 'train/tables'
        },
        'test': {
            'png': 'test/png',
            'tables': 'test/tables'
        },
        'val': {
            'png': 'val/png',
            'tables': 'val/tables'
        }
    },
    'FigureQA': {
        'train': {
            'png': 'train/png',
            'tables': 'train/tables'
        },
        'test': {
            'png': 'test/png',
            'tables': 'test/tables'
        },
        'val': {
            'png': 'val/png',
            'tables': 'val/tables'
        }
    },
    'PlotQA': {
        'train': {
            'png': 'train/png',
            'tables': 'train/tables'
        },
        'test': {
            'png': 'test/png',
            'tables': 'test/tables'
        },
        'val': {
            'png': 'val/png',
            'tables': 'val/tables'
        }
    }
}

# Create the final dataset directory structure
os.makedirs(dest_dir, exist_ok=True)
for data_type in data_types:
    for file_type in file_types:
        os.makedirs(os.path.join(dest_dir, data_type, file_type), exist_ok=True)

# Create empty JSON files
for data_type in data_types:
    json_file_path = os.path.join(dest_dir, data_type, f'converted_{data_type}.json')
    with open(json_file_path, 'w') as f:
        json.dump([], f)

# Function to copy files from source to destination
def copy_files(source_dir, dest_dir):
    if os.path.exists(source_dir):
        for file_name in os.listdir(source_dir):
            source_file = os.path.join(source_dir, file_name)
            if os.path.isfile(source_file):
                shutil.copy(source_file, dest_dir)
                print(f"Copied {file_name} to {dest_dir}")
    else:
        print(f"Source directory {source_dir} does not exist")

# Copy data to the final dataset structure and combine JSON files
for data_type in data_types:
    combined_json_data = []
    for source in sources:
        # Determine the source directories
        source_png_dir = os.path.join(base_dir, source, specific_subdirs[source][data_type]['png'])
        source_table_dir = os.path.join(base_dir, source, specific_subdirs[source][data_type]['tables'])
        
        dest_png_dir = os.path.join(dest_dir, data_type, 'png')
        dest_table_dir = os.path.join(dest_dir, data_type, 'tables')
        
        # Copy png files
        print(f"Copying PNG files from {source_png_dir} to {dest_png_dir}")
        copy_files(source_png_dir, dest_png_dir)
        
        # Copy table files
        print(f"Copying table files from {source_table_dir} to {dest_table_dir}")
        copy_files(source_table_dir, dest_table_dir)
        
        # Combine JSON files
        source_json_file = os.path.join(base_dir, source, data_type, f'converted_{source.lower()}_{data_type}.json')
        if os.path.exists(source_json_file):
            with open(source_json_file, 'r') as f:
                source_data = json.load(f)
            print(f"Loaded {len(source_data)} entries from {source_json_file}")
            combined_json_data.extend(source_data)
            print(f"Combined data from {source_json_file} for {data_type}")
        else:
            print(f"Source JSON file {source_json_file} does not exist")

    # Write combined JSON data to the final JSON file with indentation
    dest_json_file = os.path.join(dest_dir, data_type, f'converted_{data_type}.json')
    with open(dest_json_file, 'w') as f:
        json.dump(combined_json_data, f, indent=4)
    print(f"Written {len(combined_json_data)} entries to {dest_json_file}")

print("Data organization complete.")

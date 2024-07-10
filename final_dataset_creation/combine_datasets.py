import os
import shutil
import json
import random
import sys

def create_final_dataset(src, dst):
    # Define directories
    data_splits = ['train', 'test', 'val']
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
    os.makedirs(dst, exist_ok=True)
    for data_split in data_splits:
        for file_type in file_types:
            os.makedirs(os.path.join(dst, data_split, file_type), exist_ok=True)

    # Create empty JSON files
    for data_split in data_splits:
        json_file_path = os.path.join(dst, data_split, f'fc_entries.json')
        with open(json_file_path, 'w') as f:
            json.dump([], f)

    # Function to copy files from source to destination
    def copy_files(source_dir, dst):
        if os.path.exists(source_dir):
            for file_name in os.listdir(source_dir):
                source_file = os.path.join(source_dir, file_name)
                if os.path.isfile(source_file):
                    shutil.copy(source_file, dst)
                    print(f"Copied {file_name} to {dst}")
        else:
            print(f"Source directory {source_dir} does not exist")

    # Copy data to the final dataset structure and combine JSON files
    for data_split in data_splits:
        combined_json_data = []
        for source in sources:
            # Determine the source directories
            source_png_dir = os.path.join(src, source, specific_subdirs[source][data_split]['png'])
            source_table_dir = os.path.join(src, source, specific_subdirs[source][data_split]['tables'])
            
            dest_png_dir = os.path.join(dst, data_split, 'png')
            dest_table_dir = os.path.join(dst, data_split, 'tables')
            
            # Copy png files
            print(f"Copying PNG files from {source_png_dir} to {dest_png_dir}")
            copy_files(source_png_dir, dest_png_dir)
            
            # Copy table files
            print(f"Copying table files from {source_table_dir} to {dest_table_dir}")
            copy_files(source_table_dir, dest_table_dir)
            
            # Combine JSON files
            source_json_file = os.path.join(src, source, data_split, f'converted_{source.lower()}_{data_split}.json')
            if os.path.exists(source_json_file):
                with open(source_json_file, 'r') as f:
                    source_data = json.load(f)
                print(f"Loaded {len(source_data)} entries from {source_json_file}")
                combined_json_data.extend(source_data)
                print(f"Combined data from {source_json_file} for {data_split}")
            else:
                print(f"Source JSON file {source_json_file} does not exist")

        # Shuffle combined data
        random.shuffle(combined_json_data)

        # Write combined JSON data to the final JSON file with indentation
        dest_json_file = os.path.join(dst, data_split, f'fc_entries.json')
        with open(dest_json_file, 'w') as f:
            json.dump(combined_json_data, f, indent=4)
        print(f"Written {len(combined_json_data)} entries to {dest_json_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python final_dataset/main.py <from_path> <to_path>")
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2]
    create_final_dataset(src, dst)
    print("Final dataset creation complete.")

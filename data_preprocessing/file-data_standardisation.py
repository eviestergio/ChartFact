import os
import json
import shutil
import sys

def preprocess_chartQA(entry, postfix): 
    ''' Preprocess a ChartQA entry by renaming image keys and converting answers to strings. '''
    return {
        "image": f"chartQA_{entry['imgname'].split('.')[0]}-{postfix}.png",
        "question": entry["query"],
        "answer": str(entry["label"])
    }

def preprocess_figureQA(entry, postfix):
    ''' Preprocess a FigureQA entry by extracting relevant information, renaming image keys, and converting binary answers. '''
    binary_answer = entry["answer"]
    if binary_answer == 0:
        answer_str = "No"
    elif binary_answer == 1:
        answer_str = "Yes"
    return {
        "image": f"figureQA_{entry['image_index']}-{postfix}.png",
        "question": entry["question_string"],
        "answer": answer_str
    }

def preprocess_plotQA(entry, postfix):
    ''' Preprocess a PlotQA entry by extracting relevant information, renaming image keys, and converting answers to strings. '''
    return {
        "image": f"plotQA_{entry['image_index']}-{postfix}.png",
        "question": entry["question_string"],
        "answer": str(entry["answer"])
    }

def remove_figureQA_syntax(folder_path):
    ''' Remove unnecessary syntax from FigureQA JSON files. '''
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = file.read()

            start_index = data.find("[")
            end_index = data.rfind("]")

            data = data[start_index:end_index+1]

            with open(file_path, 'w') as file:
                file.write(data)

def rename_images_with_number_prefix(folder_path, prefix):
    ''' Rename images in given folder with a number prefix. '''
    png_folder_path = os.path.join(folder_path, f"png-{prefix}")

    if not os.path.exists(png_folder_path):
        print(f"Skipping processing for folder {png_folder_path} because it does not exist.")
        return
    
    for filename in os.listdir(png_folder_path):
        if filename.endswith('.png'):
            src = os.path.join(png_folder_path, filename)
            dst = os.path.join(png_folder_path, f"{prefix}-{filename}")
            os.rename(src, dst)

def combine_png_folders(dataset_folder_path):
    ''' Combine multiple PNG folders into a single folder. '''
    png_folder_path = os.path.join(dataset_folder_path, 'png')
    if not os.path.exists(png_folder_path):
        os.mkdir(png_folder_path)
    
    folders_to_delete = [] 
    for subfolder in os.listdir(dataset_folder_path):
        subfolder_path = os.path.join(dataset_folder_path, subfolder)
        if os.path.isdir(subfolder_path) and subfolder.startswith('png-'):
            for filename in os.listdir(subfolder_path):
                if filename.endswith('.png'):
                    src = os.path.join(subfolder_path, filename)
                    dst = os.path.join(png_folder_path, filename)
                    shutil.move(src, dst)
            folders_to_delete.append(subfolder_path)  

    for folder_to_delete in folders_to_delete:
        shutil.rmtree(folder_to_delete)

def preprocess_figureQA_json_files(file_path, prefix):
    ''' Preprocess FigureQA JSON files by adding a prefix to image indices. '''
    with open(file_path, 'r') as file:
        data = json.load(file)

    for entry in data:
        if "image_index" in entry:
            entry["image_index"] = f"{prefix}-{entry['image_index']}"

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)
    
def combine_json_files(folder_path):
    ''' Combine multiple JSON files into a single JSON file. '''
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json') and f != 'qa_pairs.json']
    combined_data = []
    
    for json_file in json_files:
        json_file_path = os.path.join(folder_path, json_file)
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            combined_data.extend(data)
        os.remove(json_file_path) 

    combined_json_path = os.path.join(folder_path, "qa_pairs.json")
    with open(combined_json_path, 'w') as combined_json_file:
        json.dump(combined_data, combined_json_file, indent=2)
        
def rename_chartQA_tables(folder_path, prefix, postfix):
    ''' Rename ChartQA table files by adding prefixes and postfixes to match image names. '''
    tables_folder_path = os.path.join(folder_path, 'tables')
    if not os.path.exists(tables_folder_path):
        return
    
    for filename in os.listdir(tables_folder_path):
        if filename.endswith('.csv'):
            src = os.path.join(tables_folder_path, filename)
            dst = os.path.join(tables_folder_path, f"{prefix}_{filename.split('.')[0]}-{postfix}.csv")
            os.rename(src, dst)

def copy_folder_structure_and_files(src, dst):
    ''' Copy entire folder structure and contents of source folder to destination folder. '''
    if os.path.exists(dst):
        shutil.rmtree(dst) # Remove destination folder if it exists
        
    shutil.copytree(src, dst)
    print(f"Copied {src} to {dst}")

def remove_unnecessary_files_and_folders(folder_path):
    ''' Remove unnecessary files and folders from each dataset. '''
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            if dir == 'annotations':
                shutil.rmtree(os.path.join(root, dir))
                print(f"Removed folder: {os.path.join(root, dir)}")
        for filename in files:
            if filename in ['annotations.json', 'annotations_format.txt'] or 'license' in filename.lower():
                os.remove(os.path.join(root, filename))
                print(f"Removed file: {os.path.join(root, filename)}")

def process_dataset_in_folder(folder_path, preprocess_func, postfix):
    ''' Process a dataset in the given folder using the specified preprocessing function. '''
    json_file_path = os.path.join(folder_path, "qa_pairs.json")

    if not os.path.exists(json_file_path) or os.path.getsize(json_file_path) == 0:
        print(f"Skipping processing for {json_file_path} because it doesn't exist or is empty")
        return []
    
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        preprocessed_data = [preprocess_func(entry, postfix) for entry in data]

    with open(json_file_path, 'w') as json_file:
        json.dump(preprocessed_data, json_file, indent=2)
        
    return preprocessed_data

def rename_images_with_prefix(folder_path, prefix):
    ''' Rename images in given folder by adding a dataset name specific prefix. '''
    png_folder_path = os.path.join(folder_path, f"png")
    for filename in os.listdir(png_folder_path):
        if filename.endswith('.png'):
            src = os.path.join(png_folder_path, filename)
            dst = os.path.join(png_folder_path, f"{prefix}_{filename}")
            os.rename(src, dst)

def rename_images_with_postfix(folder_path, postfix):
    ''' Rename images in the given folder by adding a data split specific postfix. '''
    png_folder_path = os.path.join(folder_path, 'png')
    for filename in os.listdir(png_folder_path):
        if filename.endswith('.png'):
            src = os.path.join(png_folder_path, filename)
            dst = os.path.join(png_folder_path, f"{filename.split('.')[0]}-{postfix}.png")  
            os.rename(src, dst)

def process_dataset_and_rename_images(folder_path, preprocess_func, prefix, postfix):
    ''' Process dataset and rename images with specified prefixes and postfixes. '''
    rename_images_with_prefix(folder_path, prefix)
    rename_images_with_postfix(folder_path, postfix)
    preprocessed_data = process_dataset_in_folder(folder_path, preprocess_func, postfix)
    
    return preprocessed_data

def any_json_files_exist(folder_path):
    ''' Boolean check if any JSON files exist in given folder path. '''
    return any(os.path.exists(os.path.join(folder_path, f"qa_pairs-{i}.json")) and os.path.getsize(os.path.join(folder_path, f"qa_pairs-{i}.json")) > 0 for i in [1, 2])

def remove_old_json_files(base_path):
    ''' Remove old JSON files (qa_pairs.json, qa_pairs-1.json, and/or qa_pairs-2.json) in the given base path. '''
    for root, dirs, files in os.walk(base_path):
        for filename in files:
            if filename.startswith('qa_pairs') and filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                os.remove(file_path)
                print(f"Removed old JSON file: {file_path}")

def main(src, dst):
    # Copy entire source directory to destination directory
    copy_folder_structure_and_files(src, dst)

    # Remove unnecessary files and folders
    remove_unnecessary_files_and_folders(dst)

    # Base path for all datasets
    base_path = dst

    # Folder paths for each dataset
    chartQA_train_folder_path = os.path.join(base_path, "ChartQA/train")
    chartQA_test_folder_path = os.path.join(base_path, "ChartQA/test")
    chartQA_val_folder_path = os.path.join(base_path, "ChartQA/val")

    figureQA_train_folder_path = os.path.join(base_path, "FigureQA/train")
    figureQA_test_folder_path = os.path.join(base_path, "FigureQA/test")
    figureQA_val_folder_path = os.path.join(base_path, "FigureQA/val")

    plotQA_train_folder_path = os.path.join(base_path, "PlotQA/train")
    plotQA_test_folder_path = os.path.join(base_path, "PlotQA/test")
    plotQA_val_folder_path = os.path.join(base_path, "PlotQA/val")

    # FigureQA: Remove unnecessary syntax
    remove_figureQA_syntax(figureQA_test_folder_path)
    remove_figureQA_syntax(figureQA_train_folder_path)
    remove_figureQA_syntax(figureQA_val_folder_path)

    # FigureQA: Check if JSONs are empty for test and val splits
    for folder_path in [figureQA_test_folder_path, figureQA_val_folder_path]:
        for file_index in [1, 2]:
            file_path = os.path.join(folder_path, f"qa_pairs-{file_index}.json")
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                preprocess_figureQA_json_files(file_path, str(file_index))
            else:
                print(f"qa_pairs-{file_index}.json not found or is empty in the folder.")

    # FigureQA: Combine qa_pairs.json files if they are not empty
    if any_json_files_exist(figureQA_test_folder_path):
        combine_json_files(figureQA_test_folder_path)
    if any_json_files_exist(figureQA_val_folder_path):
        combine_json_files(figureQA_val_folder_path)

    # FigureQA: Check for existence of multiple PNG folders before renaming
    if os.path.exists(os.path.join(figureQA_test_folder_path, "png-1")):
        rename_images_with_number_prefix(figureQA_test_folder_path, "1")
    if os.path.exists(os.path.join(figureQA_test_folder_path, "png-2")):
        rename_images_with_number_prefix(figureQA_test_folder_path, "2")
    if os.path.exists(os.path.join(figureQA_val_folder_path, "png-1")):
        rename_images_with_number_prefix(figureQA_val_folder_path, "1")
    if os.path.exists(os.path.join(figureQA_val_folder_path, "png-2")):
        rename_images_with_number_prefix(figureQA_val_folder_path, "2")

    # FigureQA: Combine PNG folders if needed
    combine_png_folders(figureQA_test_folder_path)
    combine_png_folders(figureQA_val_folder_path)

    # ChartQA: Combine human and machine generated JSON files
    combine_json_files(chartQA_train_folder_path)
    combine_json_files(chartQA_test_folder_path)
    combine_json_files(chartQA_val_folder_path)

    # ChartQA: Rename tables with prefix and postfix to match image names
    rename_chartQA_tables(chartQA_train_folder_path, "chartQA", "train")
    rename_chartQA_tables(chartQA_test_folder_path, "chartQA", "test")
    rename_chartQA_tables(chartQA_val_folder_path, "chartQA", "val")

    # Process each dataset and rename images with prefixes and postfixes
    preprocessed_chartQA_train = process_dataset_and_rename_images(chartQA_train_folder_path, preprocess_chartQA, "chartQA", "train")
    preprocessed_chartQA_test = process_dataset_and_rename_images(chartQA_test_folder_path, preprocess_chartQA, "chartQA", "test")
    preprocessed_chartQA_val = process_dataset_and_rename_images(chartQA_val_folder_path, preprocess_chartQA, "chartQA", "val")
    preprocessed_figureQA_train = process_dataset_and_rename_images(figureQA_train_folder_path, preprocess_figureQA, "figureQA", "train")
    preprocessed_figureQA_test = process_dataset_and_rename_images(figureQA_test_folder_path, preprocess_figureQA, "figureQA", "test")
    preprocessed_figureQA_val = process_dataset_and_rename_images(figureQA_val_folder_path, preprocess_figureQA, "figureQA", "val")
    preprocessed_plotQA_train = process_dataset_and_rename_images(plotQA_train_folder_path, preprocess_plotQA, "plotQA", "train")
    preprocessed_plotQA_test = process_dataset_and_rename_images(plotQA_test_folder_path, preprocess_plotQA, "plotQA", "test")
    preprocessed_plotQA_val = process_dataset_and_rename_images(plotQA_val_folder_path, preprocess_plotQA, "plotQA", "val")

    # Save preprocessed datasets to new JSON files
    output_chartQA_train_filename = os.path.join(chartQA_train_folder_path, "preprocessed_chartQA_train.json")
    output_chartQA_test_filename = os.path.join(chartQA_test_folder_path, "preprocessed_chartQA_test.json")
    output_chartQA_val_filename = os.path.join(chartQA_val_folder_path, "preprocessed_chartQA_val.json")
    output_figureQA_train_filename = os.path.join(figureQA_train_folder_path, "preprocessed_figureQA_train.json")
    output_figureQA_test_filename = os.path.join(figureQA_test_folder_path, "preprocessed_figureQA_test.json")
    output_figureQA_val_filename = os.path.join(figureQA_val_folder_path, "preprocessed_figureQA_val.json")
    output_plotQA_train_filename = os.path.join(plotQA_train_folder_path, "preprocessed_plotQA_train.json")
    output_plotQA_test_filename = os.path.join(plotQA_test_folder_path, "preprocessed_plotQA_test.json")
    output_plotQA_val_filename = os.path.join(plotQA_val_folder_path, "preprocessed_plotQA_val.json")

    with open(output_chartQA_train_filename, 'w') as chartQA_train_output_file:
        json.dump(preprocessed_chartQA_train, chartQA_train_output_file, indent=2)

    with open(output_chartQA_test_filename, 'w') as chartQA_test_output_file:
        json.dump(preprocessed_chartQA_test, chartQA_test_output_file, indent=2)

    with open(output_chartQA_val_filename, 'w') as chartQA_val_output_file:
        json.dump(preprocessed_chartQA_val, chartQA_val_output_file, indent=2)

    with open(output_figureQA_train_filename, 'w') as figureQA_train_output_file:
        json.dump(preprocessed_figureQA_train, figureQA_train_output_file, indent=2)

    with open(output_figureQA_test_filename, 'w') as figureQA_test_output_file:
        json.dump(preprocessed_figureQA_test, figureQA_test_output_file, indent=2)

    with open(output_figureQA_val_filename, 'w') as figureQA_val_output_file:
        json.dump(preprocessed_figureQA_val, figureQA_val_output_file, indent=2)

    with open(output_plotQA_train_filename, 'w') as plotQA_train_output_file:
        json.dump(preprocessed_plotQA_train, plotQA_train_output_file, indent=2)

    with open(output_plotQA_test_filename, 'w') as plotQA_test_output_file:
        json.dump(preprocessed_plotQA_test, plotQA_test_output_file, indent=2)

    with open(output_plotQA_val_filename, 'w') as plotQA_val_output_file:
        json.dump(preprocessed_plotQA_val, plotQA_val_output_file, indent=2)

    # Remove old JSON files
    remove_old_json_files(base_path)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python data_preprocessing.py <from_path> <to_path>") # Indicate correct usage if wrong command line arguments
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2]
    main(src, dst)
    print("Preprocessed files saved successfully.")
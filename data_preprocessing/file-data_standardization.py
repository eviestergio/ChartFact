import os
import json
import shutil

def remove_figureQA_syntax(folder_path):
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
    png_folder_path = os.path.join(folder_path, f"png-{prefix}")
    for filename in os.listdir(png_folder_path):
        if filename.endswith('.png'):
            src = os.path.join(png_folder_path, filename)
            dst = os.path.join(png_folder_path, f"{prefix}-{filename}")
            os.rename(src, dst)

def combine_png_folders(dataset_folder_path):
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
    with open(file_path, 'r') as file:
        data = json.load(file)

    for entry in data:
        if "image_index" in entry:
            entry["image_index"] = f"{prefix}-{entry['image_index']}"

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)
    
def combine_json_files(folder_path):
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
        
''' Main dataset preprocessing '''
def preprocess_chartQA(entry, postfix): #postfix not used
    return {
        "image": "chartQA_" + entry["imgname"],
        "question": entry["query"],
        "answer": str(entry["label"])
    }

def preprocess_figureQA(entry, postfix):
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
    return {
        "image": f"plotQA_{entry['image_index']}-{postfix}.png",
        "question": entry["question_string"],
        "answer": str(entry["answer"])
    }

# process datasets in their respective folders (and rename image_index)
def process_dataset_in_folder(folder_path, preprocess_func, postfix):
    json_file_path = os.path.join(folder_path, "qa_pairs.json")
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        preprocessed_data = [preprocess_func(entry, postfix) for entry in data]
    return preprocessed_data

def rename_images_with_prefix(folder_path, prefix):
    png_folder_path = os.path.join(folder_path, f"png")
    for filename in os.listdir(png_folder_path):
        if filename.endswith('.png'):
            src = os.path.join(png_folder_path, filename)
            dst = os.path.join(png_folder_path, f"{prefix}_{filename}")
            os.rename(src, dst)

def rename_images_with_postfix(folder_path, postfix):
    png_folder_path = os.path.join(folder_path, 'png')
    for filename in os.listdir(png_folder_path):
        if filename.endswith('.png'):
            src = os.path.join(png_folder_path, filename)
            dst = os.path.join(png_folder_path, f"{filename.split('.')[0]}-{postfix}.png") #remove file extenstion in original filename (bc added later)
            os.rename(src, dst)

def process_dataset_and_rename_images(folder_path, preprocess_func, prefix, postfix):
    rename_images_with_prefix(folder_path, prefix)
    rename_images_with_postfix(folder_path, postfix)
    return process_dataset_in_folder(folder_path, preprocess_func, postfix)

def main():
    # folder paths for each dataset
    current_folder = os.path.dirname(os.path.abspath(__file__))

    chartQA_train_folder_path = os.path.join(current_folder, "../seed_datasets/ChartQA/train")
    chartQA_test_folder_path = os.path.join(current_folder, "../seed_datasets/ChartQA/test")
    chartQA_val_folder_path = os.path.join(current_folder, "../seed_datasets/ChartQA/val")

    figureQA_train_folder_path = os.path.join(current_folder, "../seed_datasets/FigureQA/train")
    figureQA_test_folder_path = os.path.join(current_folder, "../seed_datasets/FigureQA/test")
    figureQA_val_folder_path = os.path.join(current_folder, "../seed_datasets/FigureQA/val")

    plotQA_train_folder_path = os.path.join(current_folder, "../seed_datasets/PlotQA/train")
    plotQA_test_folder_path = os.path.join(current_folder, "../seed_datasets/PlotQA/test")
    plotQA_val_folder_path = os.path.join(current_folder, "../seed_datasets/PlotQA/val")

    ''' special figureQA pre-processing '''
    remove_figureQA_syntax(figureQA_test_folder_path)
    remove_figureQA_syntax(figureQA_train_folder_path)
    remove_figureQA_syntax(figureQA_val_folder_path)

    file1_path = os.path.join(figureQA_test_folder_path, "qa_pairs-1.json")
    if os.path.exists(file1_path):
        preprocess_figureQA_json_files(file1_path, "1")
    else:
        print("qa_pairs-1.json not found in the folder.")

    file2_path = os.path.join(figureQA_test_folder_path, "qa_pairs-2.json")
    if os.path.exists(file2_path):
        preprocess_figureQA_json_files(file2_path, "2")
    else:
        print("qa_pairs-2.json not found in the folder.")

    file1_path = os.path.join(figureQA_val_folder_path, "qa_pairs-1.json")
    if os.path.exists(file1_path):
        preprocess_figureQA_json_files(file1_path, "1")
    else:
        print("qa_pairs-1.json not found in the folder.")

    file2_path = os.path.join(figureQA_val_folder_path, "qa_pairs-2.json")
    if os.path.exists(file2_path):
        preprocess_figureQA_json_files(file2_path, "2")
    else:
        print("qa_pairs-2.json not found in the folder.")

    #combine qa_pairs.json files in figureQA dataset
    combine_json_files(figureQA_test_folder_path)
    combine_json_files(figureQA_val_folder_path)

    rename_images_with_number_prefix(figureQA_test_folder_path, "1")
    rename_images_with_number_prefix(figureQA_test_folder_path, "2")
    rename_images_with_number_prefix(figureQA_val_folder_path, "1")
    rename_images_with_number_prefix(figureQA_val_folder_path, "2")

    combine_png_folders(figureQA_test_folder_path)
    combine_png_folders(figureQA_val_folder_path)

    # combine qa_pairs.json files in chartQA dataset
    combine_json_files(chartQA_train_folder_path)
    combine_json_files(chartQA_test_folder_path)
    combine_json_files(chartQA_val_folder_path)

    # process each dataset and rename images with postfixes where necessary
    preprocessed_chartQA_train = process_dataset_and_rename_images(chartQA_train_folder_path, preprocess_chartQA, "chartQA", "")
    preprocessed_chartQA_test = process_dataset_and_rename_images(chartQA_test_folder_path, preprocess_chartQA, "chartQA", "")
    preprocessed_chartQA_val = process_dataset_and_rename_images(chartQA_val_folder_path, preprocess_chartQA, "chartQA", "")
    preprocessed_figureQA_train = process_dataset_and_rename_images(figureQA_train_folder_path, preprocess_figureQA, "figureQA", "train")
    preprocessed_figureQA_test = process_dataset_and_rename_images(figureQA_test_folder_path, preprocess_figureQA, "figureQA", "test")
    preprocessed_figureQA_val = process_dataset_and_rename_images(figureQA_val_folder_path, preprocess_figureQA, "figureQA", "val")
    preprocessed_plotQA_train = process_dataset_and_rename_images(plotQA_train_folder_path, preprocess_plotQA, "plotQA", "train")
    preprocessed_plotQA_test = process_dataset_and_rename_images(plotQA_test_folder_path, preprocess_plotQA, "plotQA", "test")
    preprocessed_plotQA_val = process_dataset_and_rename_images(plotQA_val_folder_path, preprocess_plotQA, "plotQA", "val")

    # save preprocessed datasets to new JSON files
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

    print("The preprocessed datasets have been saved.")

if __name__ == "__main__":
    main()
from transformers import Pix2StructProcessor, Pix2StructForConditionalGeneration
from PIL import Image
import torch
import glob
import csv
import os
import sys
import shutil

# Check for CREATE GPU availability and set as device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device {device}")

# Load model and processor from pretrained DePlot model
model_name = 'google/deplot'
model = Pix2StructForConditionalGeneration.from_pretrained(model_name).to(device) # move to GPU
processor = Pix2StructProcessor.from_pretrained(model_name)
print("Model and processor loaded successfully")

def copy_folder_structure_and_files(src, dst):
    ''' Copy entire folder structure and contents of source folder to destination folder. '''
    if os.path.exists(dst):
        shutil.rmtree(dst)  # Remove destination folder if it exists

    shutil.copytree(src, dst)
    print(f"Copied {src} to {dst}")

def process_images_in_folder(folder_path):
    ''' Process images in specified folder and generate CSV files with extracted tables. '''
    for file_path in glob.glob(f"{folder_path}/**/*.png", recursive=True):
        parent_dir = os.path.dirname(file_path)
        grandparent_dir = os.path.dirname(parent_dir)  # Parent dir of PNG folder
        file_name = os.path.basename(file_path)

        csv_directory = os.path.join(grandparent_dir, 'tables')
        base_name = os.path.splitext(file_name)[0]
        csv_file_path = os.path.join(csv_directory, f"{base_name}-dp.csv")

        # Skip if CSV already exists for image
        if os.path.exists(csv_file_path):
            print(f"Skipping because CSV already exists for {file_path}.")
            continue

        os.makedirs(csv_directory, exist_ok=True)

        # Load and process image
        image = Image.open(file_path)
        inputs = processor(images=image, text="Generate underlying data table of the figure below:", return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}  # Move to GPU
        predictions = model.generate(**inputs, max_new_tokens=512)
        decoded_predictions = processor.decode(predictions[0], skip_special_tokens=True)

        print(f"Extracted table for {file_path}:\n{decoded_predictions}\n")

        # Save extracted table to CSV file
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([decoded_predictions])
        print(f"CSV file saved for {file_path}")

def main(src, dst):
    # Copy folder structure and files from source to destination
    copy_folder_structure_and_files(src, dst)
    
    figureqa_folder = os.path.join(dst, 'FigureQA')
    plotqa_folder = os.path.join(dst, 'PlotQA')

    # Process images in given FigureQA and PlotQA folders
    process_images_in_folder(figureqa_folder)
    process_images_in_folder(plotqa_folder)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python deplot_translation.py <from_folder> <to_folder>") # Indicate correct usage if wrong command line arguments
        sys.exit(1)
    src = os.path.expanduser(sys.argv[1])
    dst = os.path.expanduser(sys.argv[2])
    main(src, dst)
    print("Generated DePlot tables saved successfully.")
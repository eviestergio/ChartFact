from transformers import Pix2StructProcessor, Pix2StructForConditionalGeneration
from PIL import Image
import torch
import glob
import csv
import os

# Check for CREATE GPU availability and set as device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device {device}")

model_name = 'google/deplot'
model = Pix2StructForConditionalGeneration.from_pretrained(model_name).to(device) # move to GPU
processor = Pix2StructProcessor.from_pretrained(model_name)
print("Model and processor loaded successfully")

# Paths to FigureQA and PlotQA datasets
# figureqa_pattern = '../seed_datasets_100-2/FigureQA/**/*.png'
# plotqa_pattern = '../seed_datasets_100-2/PlotQA/**/*.png'
figureqa_pattern = os.path.expanduser('~/seed_datasets-100-2/FigureQA/**/*.png')
plotqa_pattern = os.path.expanduser('~/seed_datasets-100-2/PlotQA/**/*.png')

print(f"FigureQA pattern: {figureqa_pattern}")
print(f"PlotQA pattern: {plotqa_pattern}")

# Combine the patterns to match all csv files in FigureQA and PlotQA
patterns = [figureqa_pattern, plotqa_pattern]

# Process files matching the patterns
for pattern in patterns:
    for file_path in glob.glob(pattern, recursive=True):
        # Construct the full path to the PNG file
        parent_dir = os.path.dirname(file_path)
        grandparent_dir = os.path.dirname(parent_dir) # parent dir of png folder
        file_name = os.path.basename(file_path) 

        # Determine the path for the corresponding CSV file
        csv_directory = os.path.join(grandparent_dir, 'tables')
        base_name = os.path.splitext(file_name)[0]
        csv_file_path = os.path.join(csv_directory, f"{base_name}-dp.csv")
        
        # Skip if the CSV already exists
        if os.path.exists(csv_file_path):
            print(f"Skipping because CSV already exists for {file_path}.")
            continue
        
        # Create CSV directory if it doesn't exist
        os.makedirs(csv_directory, exist_ok=True) 

        # DePlot the PNG
        image = Image.open(file_path)
        inputs = processor(images=image, text="Generate underlying data table of the figure below:", return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()} # move to GPU
        predictions = model.generate(**inputs, max_new_tokens=512)
        decoded_predictions = processor.decode(predictions[0], skip_special_tokens=True)
        
        print(f"Extracted table for {file_path}:\n{decoded_predictions}\n")

        # Write prediction to CSV file in respective folder
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([decoded_predictions])
        print(f"CSV file saved for {file_path}")

print("CSV files saved successfully.")
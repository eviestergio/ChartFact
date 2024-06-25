import os
from transformers import Pix2StructProcessor, Pix2StructForConditionalGeneration
from PIL import Image
import csv

processor = Pix2StructProcessor.from_pretrained('google/deplot')
model = Pix2StructForConditionalGeneration.from_pretrained('google/deplot')

folder_path = '../random_sample_100'

# Recursively iterate through all files and directories in folder 
for root, dirs, files in os.walk(folder_path):
    # Iterate through all files in the current directory
    for file_name in files:
        # Check if the file has a PNG extension
        if file_name.lower().endswith('.png'):
            # Construct the full path to the PNG file
            file_path = os.path.join(root, file_name)

            # Determine the path for the corresponding CSV file
            parent_dir = os.path.dirname(root)
            # Create CSV directory and file paths relative to the parent directory
            csv_directory = os.path.join(parent_dir, 'tables')
            csv_file_path = os.path.join(csv_directory, file_name.replace('.png', '.csv'))
            
            # Check if the CSV file already exists
            if os.path.exists(csv_file_path):
                print(f"Skipping because CSV file already exists for {file_path}.")
                continue

            # DePlot the PNG
            image = Image.open(file_path)
            inputs = processor(images=image, text="Generate underlying data table of the figure below:", return_tensors="pt")
            predictions = model.generate(**inputs, max_new_tokens=512)
            decoded_predictions = processor.decode(predictions[0], skip_special_tokens=True)
            print(f"Data for {file_path}:\n{decoded_predictions}\n")

            # Create CSV directory if it doesn't exist
            os.makedirs(csv_directory, exist_ok=True) 
            
            # Write prediction to CSV file in respective folder
            with open(csv_file_path, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([decoded_predictions])
            print(f"CSV file saved for {file_path}")

print("CSV files saved successfully.")
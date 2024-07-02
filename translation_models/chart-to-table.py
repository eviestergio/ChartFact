from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import glob
import csv
import os

# Check for CREATE GPU availability and set as device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device {device}")

model_name = 'khhuang/chart-to-table'
model = VisionEncoderDecoderModel.from_pretrained(model_name).to(device) # move to GPU
processor = DonutProcessor.from_pretrained(model_name)
print("Model and processor loaded successfully")

# Paths to FigureQA and PlotQA datasets
# figureqa_pattern = '../random_sample_100-2/FigureQA/**/*.png'
# plotqa_pattern = '../random_sample_100-2/PlotQA/**/*.png'
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
        csv_file_path = os.path.join(csv_directory, f"{base_name}-ctt.csv")
        
        # Skip if the CSV already exists
        if os.path.exists(csv_file_path):
            print(f"Skipping because CSV already exists for {file_path}.")
            continue
        
        # Create CSV directory if it doesn't exist
        os.makedirs(csv_directory, exist_ok=True)

        # Format text inputs
        input_prompt = "<data_table_generation> <s_answer>"

        # Encode chart figure and tokenize text
        img = Image.open(file_path)
        pixel_values = processor(img.convert("RGB"), random_padding=False, return_tensors="pt").pixel_values.to(device)
        decoder_input_ids = processor.tokenizer(input_prompt, add_special_tokens=False, return_tensors="pt", max_length=510).input_ids.to(device)

        outputs = model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_length=model.decoder.config.max_position_embeddings,
            early_stopping=True,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
            use_cache=True,
            num_beams=4,
            bad_words_ids=[[processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )

        sequence = processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
        extracted_table = sequence.split("<s_answer>")[1].strip()

        print(f"Extracted table for {file_path}:\n{extracted_table}")

        # Write prediction to CSV file in respective folder
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([extracted_table])
        print(f"CSV file saved for {file_path}")
            
print("CSV files saved successfully.")
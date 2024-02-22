from transformers import Pix2StructProcessor, Pix2StructForConditionalGeneration
# import requests
from PIL import Image
import glob

processor = Pix2StructProcessor.from_pretrained('google/deplot')
model = Pix2StructForConditionalGeneration.from_pretrained('google/deplot')

folder_path = '../seed_datasets/ChartQA/test/png/'

png_files = glob.glob(f'{folder_path}*.png') #list of all pngs

print(f"Number of PNG files found: {len(png_files)}") 

for file_path in png_files:
    image = Image.open(file_path)

    inputs = processor(images=image, text="Generate underlying data table of the figure below:", return_tensors="pt")
    predictions = model.generate(**inputs, max_new_tokens=512)
    
    decoded_predictions = processor.decode(predictions[0], skip_special_tokens=True)
    print(f"Data for {file_path}:\n{decoded_predictions}\n")
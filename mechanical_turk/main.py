import os
import json
import csv

def main():
    # Explicitly set the base directory.
    base_dir = "/Users/angwang/ChartFact/seed_datasets_100/5_final_dataset_100-new"
    # List of subfolders to process.
    folders_to_search = ["test", "train", "val"]
    
    records = []
    
    for folder in folders_to_search:
        folder_path = os.path.join(base_dir, folder)
        json_path = os.path.join(folder_path, "fc_entries.json")
        # The images are expected to be inside the "png" directory of each folder.
        png_folder = os.path.join(folder_path, "png")
        
        print(f"Processing folder: {folder_path}")
        
        # Check if the JSON file exists in the folder.
        if not os.path.exists(json_path):
            print(f"Missing fc_entries.json in {folder_path}. Skipping this folder.")
            continue
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {json_path}: {e}")
            continue
        
        if not isinstance(data, list):
            print(f"Expected a list of entries in {json_path}, got {type(data)}. Skipping this file.")
            continue
        
        for entry in data:
            image_val = entry.get("image")
            claim_text = entry.get("claim")
            
            if not image_val or not claim_text:
                print(f"Skipping an entry in {json_path} due to missing 'image' or 'claim': {entry}")
                continue
            
            # Build the full path to the image within the png folder.
            image_full_path = os.path.join(png_folder, image_val)
            if not os.path.exists(image_full_path):
                print(f"Image file {image_full_path} does not exist. Skipping the corresponding entry.")
                continue
            
            # Build a relative URL for the chart image.
            # This will be relative to base_dir and with Unix-style slashes.
            relative_path = os.path.relpath(image_full_path, base_dir)
            chart_image_url = relative_path.replace(os.path.sep, '/')
            
            record = {
                "chart_image_url": f"https://raw.githubusercontent.com/eviestergio/ChartFact/refs/heads/main/seed_datasets_100/5_final_dataset_100-new/{chart_image_url}",
                "claim_text": claim_text
            }
            print(f"Record added: {record}")
            records.append(record)
    
    # Define the CSV output path (created in the base directory).
    output_csv_path = os.path.join(base_dir, "final_claims.csv")
    fieldnames = ["chart_image_url", "claim_text"]
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                writer.writerow(rec)
        print(f"CSV file created successfully: {output_csv_path}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")

if __name__ == "__main__":
    main()
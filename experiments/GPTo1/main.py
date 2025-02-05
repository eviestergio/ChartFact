# from model import QueryModel
import json
import os
import shutil
import sys
import base64

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv('API_KEY'))

class QueryModel:
    """
    The class that handles GPT model queries and responses.
    """

    def __init__(self, params = None):
        """
        Constructor to initialise model parameters.
        Args:
            params (dict): The parameters of the model in dict format.
        """
        self.params = params or {
            'temperature': 1,
            'max_completion_tokens': 2000,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }

    def __call__(self, model_name, query, image_base64=None, *args, **kwargs):
        """
        Query the GPT-4 model with text and image input.
            model_name (str): The name of the model
            query (str): The text prompt for the model.
            image_base64 (str): Base64-encoded image string. (optional)
        Returns:
            response_text (str): The response from the model.
        """

        # If no image provided, send text-only request
        messages = [
            {"role": "user", "content": query}
        ]
            
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            **self.params
        )
        
        response_text = response.choices[0].message.content
        print(response_text)
        return response_text

# --- Image input prompts ---

## Supports prompts
def create_zero_shot_prompt(image, claim):
    """ 
    Creates a zero-shot prompt to generate a 'supports' claim with an explanation using 
    image input based on a Q&A pair.
    """
    # Format the image as Markdown so the model (if multimodal) can render it.
    # image_markdown = f"![chart](data:image/png;base64,{image})"
    
    prompt = f"""
    Given the chart: {image} in the image input, what is the appropriate label (\'supports\', \'refutes\', or \'not enough information\') for the following claim: {claim}? Why? Output the result as a JSON object with the following keys: "explanation" and "label". The format should strictly follow this structure: {{"explanation": "your explanation for the label selected", "label": "your label for the claim"}}
    """
    
    return prompt

# --- Other functions ---
def encode_image(image_path, base_dir):
    ''' Encode image from a given path. '''
    for root, dirs, files in os.walk(base_dir):
        if image_path in files:
            full_path = os.path.join(root, image_path)
            with open(full_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                return base64_image
    
    raise FileNotFoundError(f"Image: '{image_path}' not found in '{base_dir}' or its subdirectories")

def parse_json_response(response):
    ''' Parse JSON object response to extract claim and explanation. '''
    try:
        # strip gpt-4o-mini leading/trailing syntax 
        if response.startswith("```json"):
            response = response[len("```json"):].strip()
        if response.endswith("```"):
            response = response[:-len("```")].strip()

        response_json = json.loads(response)
        return response_json
    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
        return {}

def generate_label_explanation(image_path, claim, model, base_dir):
    ''' Generate a 'label' and 'explanation' for a claim and image pair'''
    base64_image = encode_image(image_path, base_dir)
    prompt = create_zero_shot_prompt(base64_image, claim) # change prompt version here
    response = model(model_name='gpt-4o', query=prompt, image_base64=base64_image) # change model here
    response_json = parse_json_response(response)

    # If failed, add empty entries to filter out from final dataset
    if not response_json:
        print("Failed to parse response for supports claim.")
        return "", "" 
    
    label = response_json['label']
    explanation = response_json['explanation']

    return label, explanation

def generate_labels_explanations_from_file(input_file, model, base_dir, claim_index):
    ''' Process an input file to generate one claim for each Q&A pair entry.
        Uses a persistent claim_index that is updated across files.
    '''
    with open(input_file, 'r') as file:
        entries = json.load(file)

    results = []
    
    for entry in entries:
        # Check if necessary keys exist
        claim = entry.get("claim")
        image = entry.get("image")

        # Check for missing data 
        if not claim or not image:
            print(f"Skipping entry due to missing data: {entry}")
            continue

        # Generate 'label' and 'explanation'

        label, explanation = generate_label_explanation(image, claim, model, base_dir)
        results.append({
            "image": image,
            "claim": claim,
            "label": label,
            "explanation": explanation
        })
        claim_index += 1
        continue
    # Save results to output file in the same folder as the input file.
    save_results(input_file, results)
    
    # Return the updated claim_index so that the counter persists across files.
    return claim_index

def save_results(input_file, results):
    ''' Save generated results to an output file. '''
    output_folder = os.path.dirname(input_file) # Determine the output folder based on the input file path
    output_file_name = os.path.basename(input_file).replace('fc', 'gpto1')
    output_path = os.path.join(output_folder, output_file_name)

    with open(output_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)

    print(f"Conversion completed for {os.path.basename(input_file)}. Results saved to {output_path}.")

    # Remove old 'fc'/gold data file
    os.remove(input_file)
    print(f"Removed gold data file: {input_file}")

def copy_folder_structure_and_files(src, dst):
    ''' Copy entire folder structure and contents of source folder to destination folder. '''
    if os.path.exists(dst):
        shutil.rmtree(dst)  # Remove destination folder if it exists

    shutil.copytree(src, dst)
    print(f"Copied {src} to {dst}")

def main(src, dst):
    ''' Main function to process all JSON files in specified directory. '''
    model = QueryModel()
    global_claim_index = 0

    # Copy entire source directory to destination directory
    copy_folder_structure_and_files(src, dst)

    for root, _, files in os.walk(dst):
        for filename in files:
            if filename.startswith('fc_') and filename.endswith('.json'):
                input_file = os.path.join(root, filename)
                # Pass the global counter into each file's processing,
                # and update it with the returned value.
                global_claim_index = generate_labels_explanations_from_file(input_file, model, dst, global_claim_index)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python experiments/GPTo1/main.py <from_path> <to_path>")
        sys.exit(1)
    from_path = sys.argv[1]
    to_path = sys.argv[2]
    main(from_path, to_path)
    print("Prompted files saved successfully.")
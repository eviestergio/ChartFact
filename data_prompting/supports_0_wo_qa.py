# Only for ChartQA inside seed_datasets_12
# Completing only 2 from ChartQA/test first

from model import QueryModel
import json
import os
import shutil
import sys
import base64

def encode_image(image_path, base_dir):
    ''' Encode image from a given path. '''
    # Ensure the image path is relative to the base_dir
    full_path = os.path.normpath(image_path)
    print(f"Looking for file at: {full_path}")  # Debugging log

    if os.path.exists(full_path):
        with open(full_path, "rb") as image_file:
            image = base64.b64encode(image_file.read()).decode('utf-8')
            return image
    
    raise FileNotFoundError(f"Image: '{full_path}' not found.")


def create_zero_shot_supports_prompt_wo_QA(image, annotations):
    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with an image of a chart and JSON file with annotations related to the chart, delimited by triple single quotes.

    Data input: '''
        "image": {image},
        "annotations": {annotations}
    '''

    Task: Generate a claim that supports the information in the chart and provide an explanation.

    Process for generating a 'supports' claim and explanation:
        1. Using the image and its associated annotations, develop a claim that is supported by the data in the chart.
        2. Validate that your claim supports the information in the chart by carefully analyzing the image and the annotations. 
        3. Explain why the claim supports the chart by referencing specific visual aspects and data points visible in the image. For example, reference specific values, lines, or categories shown in the chart.

    Output the result as a JSON object with the following keys: "supports claim" and "explanation". The format should strictly follow this structure:
    {{
        "supports claim": "your generated supports claim",
        "explanation": "your explanation for why the claim supports the chart"
    }}
    """
    print(f"Generated Prompt: {prompt}")  # Debugging prompt content
    return prompt

def parse_json_response(response):
    ''' Parse JSON object response to extract claim and explanation. '''
    try:
        # Strip model-specific formatting
        if response.startswith("```json"):
            response = response[len("```json"):].strip()
        if response.endswith("```"):
            response = response[:-len("```")].strip()

        response_json = json.loads(response)
        if "supports claim" in response_json and "explanation" in response_json:
            return response_json
        else:
            print(f"Missing keys in response JSON: {response_json}")
            return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        return None


def get_image_annotation_pairs(base_dir):
    # Define the subdirectories based on your dataset structure
    sub_dir = os.path.join(base_dir, "ChartQA/test")
    images_dir = os.path.join(sub_dir, "png")  # Images are in 'png/'
    annotations_dir = os.path.join(sub_dir, "annotations")  # Annotations are in 'annotations/'

    # Ensure the directories exist
    if not os.path.exists(images_dir) or not os.path.exists(annotations_dir):
        raise FileNotFoundError(f"Image directory or annotation directory not found in {sub_dir}")

    # Get matching image and annotation pairs
    image_files = set(f for f in os.listdir(images_dir) if f.endswith('.png'))
    annotation_files = set(f for f in os.listdir(annotations_dir) if f.endswith('.json'))

    matched_files = [
        (os.path.join(images_dir, img), os.path.join(annotations_dir, img.replace('.png', '.json')))
        for img in image_files if img.replace('.png', '.json') in annotation_files
    ]
    return matched_files


def process_image_annotation_pair(image_path, annotation_path, model):
    base_dir = os.path.dirname(image_path)
    print(f"Processing Image: {image_path}")
    print(f"Processing Annotations: {annotation_path}")

    # Encode the image
    try:
        image_encoded = encode_image(image_path, base_dir)
    except FileNotFoundError as e:
        print(e)
        return None  # Handle missing file gracefully

    # Read annotations
    try:
        with open(annotation_path, "r") as f:
            annotations = json.load(f)
    except Exception as e:
        print(f"Failed to read annotation file: {e}")
        return None

    # Generate the prompt
    prompt = create_zero_shot_supports_prompt_wo_QA(image_encoded, annotations)
    print(f"Prompt Sent to Model: {prompt}")

    # Get the model response
    try:
        response = model(model_name='gpt-4o-mini', query=prompt)
        print(f"Model Response: {response}")
    except Exception as e:
        print(f"Model query failed: {e}")
        return None

    # Parse the response
    response_json = parse_json_response(response)
    print(f"Parsed Response: {response_json}")

    if not response_json or "supports claim" not in response_json or "explanation" not in response_json:
        print("Model did not return a valid JSON response.")
        return None

    return response_json


def process_dataset(base_dir, model):
    pairs = get_image_annotation_pairs(base_dir)
    results = []

    for image_path, annotation_path in pairs:
        result = process_image_annotation_pair(image_path, annotation_path, model)
        results.append(result)

    # Save the results to a JSON file
    output_file = os.path.join(base_dir, "results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"Processed {len(results)} pairs. Results saved to {output_file}.")

if __name__ == "__main__":
    base_dir = "seed_datasets_12/3_translated_data_12"  # Adjust the path as needed
    model = QueryModel(query_type='json_object')  # Initialize the model
    process_dataset(base_dir, model)
# RESULTS ARE NON-SENSICAL WITHOUT ANNOTATIONS AND WITHOUT Q&A PAIRS

from model import QueryModel
import json
import os
import base64


def encode_image(image_path):
    ''' Encode image from a given path. '''
    full_path = os.path.normpath(image_path)
    print(f"Looking for file at: {full_path}")  # Debugging log

    if os.path.exists(full_path):
        with open(full_path, "rb") as image_file:
            image = base64.b64encode(image_file.read()).decode('utf-8')
            return image

    raise FileNotFoundError(f"Image: '{full_path}' not found.")

def create_few_shot_supports_prompt_wo_QA(image, annotations):
    """ Creates a few-shot prompt to generate a 'supports' claim with an explanation using image input without a Q&A pair. """

    image1 = encode_image("seed_datasets/PlotQA/test/png/plotQA_39-test.png")
    image2 = encode_image("seed_datasets/FigureQA/test/png/figureQA_1-1-test.png") 

    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with an image of a chart delimited by triple single quotes.

    Data input: '''
        "image": {image}
    '''

    Task: Using the two input-output examples below delimited by angle brackets, generate a claim that supports the information in the chart, and provide an explanation.

    Process for generating a 'supports' claim and explanation:
        1. Using the image, develop a claim that is supported by the data in the chart.
        2. Validate that your claim supports the information in the chart by carefully analyzing the image. 
        3. Explain why the claim refutes the chart by referencing specific visual aspects and data points visible in the image. For example, reference specific values, lines, or categories shown in the chart.

    Output the result as a JSON object with the following keys: "supports claim" and "explanation". The format should strictly follow this structure:
    {{
        "supports claim": "your generated supports claim",
        "explanation": "your explanation for why the claim supports the chart"
    }}

    Examples: < 
     1. Input: 
            "image": {image1}
        Output: {{
            "supports claim": "The domestic liabilities increased significantly from 2005 to 2009.", 
            "explanation": "The chart shows a clear trend where domestic liabilities grew substantially over the years, starting from 102600000 in 2005 to 184518000000 in 2009. This increase is directly supported by the numerical values provided in the chart."
        }}
     2. Input: 
            "image": {image2}
        Output: {{
            "supports claim": "Deep Sky Blue has a higher value than Magenta.",
            "explanation": "The chart shows that the bar representing Deep Sky Blue has a visibly higher height than the one for Magenta, supporting the claim that Deep Sky Blue's value is indeed greater."
        }}
    >
    """
    
    return prompt

def parse_json_response(response):
    ''' Parse JSON object response to extract claim and explanation. '''
    try:
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


def get_image_annotation_pairs(sub_dir):
    ''' Get matching image-annotation pairs from a subdirectory. '''
    images_dir = os.path.join(sub_dir, "png")  # Images are in 'png/'
    annotations_dir = os.path.join(sub_dir, "annotations")  # Annotations are in 'annotations/'

    if not os.path.exists(images_dir) or not os.path.exists(annotations_dir):
        raise FileNotFoundError(f"Image directory or annotation directory not found in {sub_dir}")

    image_files = set(f for f in os.listdir(images_dir) if f.endswith('.png'))
    annotation_files = set(f for f in os.listdir(annotations_dir) if f.endswith('.json'))

    matched_files = [
        (os.path.join(images_dir, img), os.path.join(annotations_dir, img.replace('.png', '.json')))
        for img in image_files if img.replace('.png', '.json') in annotation_files
    ]
    return matched_files


def process_image_annotation_pair(image_path, annotation_path, model):
    ''' Process a single image-annotation pair. '''
    print(f"Processing Image: {image_path}")
    print(f"Processing Annotations: {annotation_path}")

    try:
        image_encoded = encode_image(image_path)
    except FileNotFoundError as e:
        print(e)
        return None

    try:
        with open(annotation_path, "r") as f:
            annotations = json.load(f)
    except Exception as e:
        print(f"Failed to read annotation file: {e}")
        return None

    prompt = create_few_shot_supports_prompt_wo_QA(image_encoded, annotations)

    try:
        response = model(model_name='gpt-4o-mini', query=prompt)
        print(f"Model Response: {response}")
    except Exception as e:
        print(f"Model query failed: {e}")
        return None

    response_json = parse_json_response(response)
    if not response_json:
        print("Model did not return a valid JSON response.")
        return None

    return response_json


def process_subdirectory(base_dir, subdirectory, model):
    ''' Process all image-annotation pairs in a subdirectory. '''
    sub_dir = os.path.join(base_dir, "ChartQA", subdirectory)
    pairs = get_image_annotation_pairs(sub_dir)
    results = []

    for image_path, annotation_path in pairs:
        result = process_image_annotation_pair(image_path, annotation_path, model)
        if result:
            results.append(result)

    output_file = os.path.join(sub_dir, "no_anno_supports_few_wo_qa.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"Processed {len(results)} pairs in {subdirectory}. Results saved to {output_file}.")


def process_dataset(base_dir, model):
    ''' Process ChartQA/test, ChartQA/train, and ChartQA/val. '''
    for subdirectory in ["test", "train", "val"]:
        try:
            process_subdirectory(base_dir, subdirectory, model)
        except FileNotFoundError as e:
            print(e)


if __name__ == "__main__":
    base_dir = "seed_datasets_12/3_translated_data_12"  # Adjust the path as needed
    model = QueryModel(query_type='json_object')  # Initialize the model
    process_dataset(base_dir, model)

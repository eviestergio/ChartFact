from model import QueryModel
import json
import os
import shutil
import sys
import base64
import requests
from openai import OpenAI
from dotenv import load_dotenv
import os

## Create function to prompt with manually added image input and claim

api_key = os.getenv('API_KEY')

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image, manually added
image_path = "seed_datasets_12/5_final_dataset_12/test/png/plotQA_1467-test.png"
image_path1 = "seed_datasets/FigureQA/test/png/figureQA_2-3-test.png"
image_path2 = "seed_datasets/PlotQA/test/png/plotQA_39-test.png"
image_path3 = "seed_datasets/ChartQA/test/png/chartQA_166.png"

# Getting the base64 string
chart = encode_image(image_path)
chart1 = encode_image(image_path1)
chart2 = encode_image(image_path2)
chart3 = encode_image(image_path3)
# Manually input the claim 
claim = 'The label of the X-axis in the chart is \'Year\'.'

# Prompt is dynamically filled by the encoded image and the claiim 
# prompt = 'Given the chart: {chart} in the image input, please explain the reasoning and then answer: What is the appropriate label (\'supports\', \'refutes\', or \'not enough information\') for the following claim: The label of the X-axis in the chart is \'Year\'.? Output the result as a JSON object with the following keys: "explanation" and "label". The format should strictly follow this structure: {{"explanation": "your explanation for the label selected", "label": "your label for the claim"}}'
prompt = '''Given the chart {{chart}}, what is the correct label ('supports', 'refutes', or 'not enough information') for the claim: 'The label of the X-axis in the chart is \'Year\'.'? Why? 
Output the result as a JSON object with the following keys: "label" and "explanation". The format should strictly follow this structure:
{{
"label": "your label for the claim",
"explanation": "your explanation for the label selected"
}}

Examples of how this task is done:
<
1. Input:
{{
"chart": {chart1}
“claim”: “Crimson is the maximum.”
}}
Output:
{{
"label": "refutes",
"explanation": "The claim directly contradicts the chart, which clearly shows that Gold has the maximum value at 59.05. By asserting that Crimson is the maximum, it directly opposes the factual information provided, refuting the chart."
}}
2. Input:
{{
"chart": {chart2}
“claim": "The income share held by the highest 10% of the population was greater than the average income share held by the highest 10% of the population in 1 year."
}}
Output:
{{
"label": "supports",
"explanation": "The chart shows data over several years where the income shares of the highest 10% are listed. Comparing these figures reveals that in one specific year, the income share of the top 10% exceeded the average income share held by the top 10% across all years.."
}}
3. Input:
{{
"chart": {chart3}
“claim”: “President Donald Trump's approach to international relations contributes to their perception as Dangerous.”
}}
Output:
{{
“label”: “not enough information”,
“explanation”: “This claim speculates on information not provided in the chart, as there is no data regarding international relations, making the connection to the perception of being 'Dangerous' unverifiable.”
}}
>'''

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": f"{prompt}"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{chart}"
          }
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{chart1}"
          }
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{chart2}"
          }
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{chart3}"
          }
        }
      ]
    }
  ],
  "max_tokens": 1000
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())

# ## Dynamically create the prompt for each of the data entries 
# def create_label_and_explanation_prompt(chart, claim): # 783 tokens, 3349 characters 
#     ''' Creates a prompt to generate a label with and explanation. '''
#     prompt = f"""
#     Given the chart: {chart} in the image input, please explain the reasoning and then answer: What is the appropriate label ('supports', 'refutes', or 'not enough information') for the following claim: {claim}?

#     Output the result as a JSON object with the following keys: "explanation" and "label". The format should strictly follow this structure:
#    {{
#        "explanation": "your explanation for the label selected",
#        "label": "your label for the claim"
#    }}
#     """

#     return prompt

# ## Parse JSON response for the prompt
# def parse_json_response(response):
#     ''' Parse JSON object response to extract claim and explanation. '''
#     try:
#         response_json = json.loads(response)
#         return response_json
#     except json.JSONDecodeError:
#         print("Failed to parse JSON response.")
#         return {}

# def generate_label_and_explanation(title, table, question, answer, model):
#     ''' Generate a 'supports' claim with an explanation. '''
#     prompt = create_supports_prompt(title, table, question, answer)
#     response = model(model_name='gpt-4o', query=prompt)
#     response_json = parse_json_response(response)

#     # If failed, add empty entries to filter out from final dataset
#     if not response_json:
#         print("Failed to parse response for supports claim.")
#         return "", "" 
    
#     claim = response_json['supports claim']
#     explanation = response_json['explanation']

#     return label, explanation

# def generate_claims_from_file(input_file, model):
#     ''' Process an input file to generate one claim for each Q&A pair entry. '''
#     with open(input_file, 'r') as file:
#         entries = json.load(file)

#     results = []
#     claim_types = ['Supports', 'Refutes', 'Not enough information']
#     claim_index = 0
    
#     for entry in entries:
#         # Check if necessary keys exist
#         question = entry.get("question")
#         answer = entry.get("answer")
#         image = entry.get("image")

#         base_csv_file_path = os.path.join(os.path.dirname(input_file), "tables", f"{entry['image'].split('.')[0]}")
#         csv_file_path = base_csv_file_path + "-dp.csv"
#         regular_csv_file_path = base_csv_file_path + ".csv"
#         title_file_path = base_csv_file_path + "-title.txt"

#         # Read CSV file (prioritize '-dp' file)
#         if os.path.exists(csv_file_path):
#             with open(csv_file_path, 'r') as csv_file:
#                 table = csv_file.read()
#         elif os.path.exists(regular_csv_file_path):
#             with open(regular_csv_file_path, 'r') as csv_file:
#                 table = csv_file.read()
#         else:
#             table = None

#         # Read title file if it exists
#         if os.path.exists(title_file_path):
#             with open(title_file_path, 'r') as title_file:
#                 title = title_file.read().strip()
#         else:
#             title = None

#         # Check for missing data (excluding optional title)
#         if not question or not answer or not image or (table is None):
#             print(f"Skipping entry due to missing data: {entry}")
#             continue

#         claim_type = claim_types[claim_index % 3]

#         # Generate 'supports' claim
#         if claim_type == 'Supports':
#             supports_claim, explanation = generate_supports_claim(title, table, question, answer, model)
#             results.append({
#                 "image": image,
#                 "claim": supports_claim,
#                 "label": "Supports",
#                 "explanation": explanation
#             })
#             claim_index += 1
#             continue

#         # Generate 'refutes' claim using 'supports' claim from simplified function
#         if claim_type == 'Refutes':
#             simple_supports_claim = generate_supports_claim_simple(question, answer, model)
#             refutes_claim, explanation = generate_refutes_claim(title, table, simple_supports_claim, model)
#             results.append({
#                 "image": image,
#                 "claim": refutes_claim,
#                 "label": "Refutes",
#                 "explanation": explanation
#             })
#             claim_index += 1
#             continue

#         # Generate 'not enough information' claim using 'supports' claim from simplified function
#         if claim_type == 'Not enough information':
#             simple_supports_claim = generate_supports_claim_simple(question, answer, model)
#             nei_claim, explanation = generate_nei_claim(title, table, simple_supports_claim, model)
#             results.append({
#                 "image": image,
#                 "claim": nei_claim,
#                 "label": "Not enough information",
#                 "explanation": explanation
#             })
#             claim_index += 1
#             continue

#     # Save results to output file
#     save_results(input_file, results)

# def save_results(input_file, results):
#     ''' Save generated results to an output file. '''
#     output_folder = os.path.dirname(input_file) # Determine the output folder based on the input file path
#     output_file_name = os.path.basename(input_file).replace('preprocessed', 'converted')
#     output_path = os.path.join(output_folder, output_file_name)

#     with open(output_path, 'w') as output_file:
#         json.dump(results, output_file, indent=4)

#     print(f"Conversion completed for {os.path.basename(input_file)}. Results saved to {output_path}.")

#     # Remove old 'preprocessed' file
#     os.remove(input_file)
#     print(f"Removed old preprocessed file: {input_file}")

# # def copy_entire_folder(src, dst):
# #     if os.path.exists(dst):
# #         shutil.rmtree(dst)
# #     shutil.copytree(src, dst)

# def copy_folder_structure_and_files(src, dst):
#     ''' Copy entire folder structure and contents of source folder to destination folder. '''
#     if os.path.exists(dst):
#         shutil.rmtree(dst)  # Remove destination folder if it exists

#     shutil.copytree(src, dst)
#     print(f"Copied {src} to {dst}")

# def main(src, dst):
#     ''' Main function to process all JSON files in specified directory. '''
#     model = QueryModel(query_type='json_object')

#     # Copy entire source directory to destination directory
#     copy_folder_structure_and_files(src, dst)

#     for root, _, files in os.walk(dst):
#         for filename in files:
#             if filename.startswith('preprocessed_') and filename.endswith('.json'):
#                 input_file = os.path.join(root, filename)
#                 generate_claims_from_file(input_file, model)

# if __name__ == '__main__':
#     if len(sys.argv) != 3:
#         print("Usage: python data_prompting.py <from_path> <to_path>") # Indicate correct usage if wrong command line arguments
#         sys.exit(1)
#     from_path = sys.argv[1]
#     to_path = sys.argv[2]
#     main(from_path, to_path)
#     print("Prompted files saved successfully.")
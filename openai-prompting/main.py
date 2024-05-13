from model import QueryModel
import json
import os

def create_supports_prompt(entry):
    prompt = f"""
        You will be provided with a data entry in JSON format deliminated by 3 single quotes. 

        Each data entry contains the following keys:
        'image', 'question', 'answer'

        Using the 4 input-output examples deliminated by angle brackets, your task is to convert 
        each 'question' and 'answer' pair to a claim that supports the information.

        Examples: < 
        1. Input: {{
            "image": "chartQA_multi_col_803.png",
            "question": "How many stores did Saint Laurent operate in Western Europe in 2020?",
            "answer": "47"
        }}
        Output: "Saint Laurent operated 47 stores in Western Europe in 2020." 
        2. Input: {{
            "image": "plotQA_11.png",
            "question": "What is the title of the graph ?",
            "answer": "Net disbursements of loans from International Monetary Fund"
        }}
        Output: "The title of the graph is Net disbursements of loans from International Monetary Fund."
        3. Input: {{
            "image": "figureQA_400.png",
            "question": "Is Turquoise the roughest?",
            "answer": "No"
        }}
        Output: "Turquoise is not the roughest."
        4. Input: {{
            "image": "figureQA_514.png",
            "question": "Is Periwinkle greater than Green Yellow?",
            "answer": "Yes"
        }}
        Output: "Periwinkle is greater than Green Yellow."
        >

        Output only the text for the claim derived from converting the question and answer pair in double quotes.

        Data entry: '''{entry}'''
        """
    return prompt

def create_refutes_prompt(entry, supports_claim):
    prompt = ""
    return prompt

def create_nei_prompt(entry, supports_claim):
    prompt = ""
    return prompt

def generate_supports_claim(entry, model):
    prompt = create_supports_prompt(entry)
    return model(query=prompt)

def generate_refutes_claim(entry, model, supports_claim):
    prompt = create_refutes_prompt(entry, supports_claim)
    return model(query=prompt)

def generate_nei_claim(entry, model, supports_claim):
    prompt = create_nei_prompt(entry, supports_claim)
    return model(query=prompt)

def process_file(input_file, model):
    
    with open(input_file, 'r') as file:
            entries = json.load(file)

    results = []
    
    for entry in entries:
        # Generate 'supports' claim
        supports_claim = generate_supports_claim(entry, model)
        results.append({
            "image": entry.get("image", ""),
            "claim": supports_claim,
            "label": "Supports"
        })

        # Generate 'refutes' claim using 'supports' claim
        refutes_claim = generate_refutes_claim(entry, model, supports_claim)
        results.append({
            "image": entry.get("image", ""),
            "claim": refutes_claim,
            "label": "Refutes"
        })

        # Generate 'not enough information' claim using 'supports' claim
        nei_claim = generate_nei_claim(entry, model, supports_claim)
        results.append({
            "image": entry.get("image", ""),
            "claim": nei_claim,
            "label": "Not enough information"
        })

    # Save results to output file
    save_results(input_file, results)

def save_results(input_file, results):
    output_folder = os.path.dirname(input_file) # Determine the output folder based on the input file path
    output_file_name = os.path.basename(input_file).replace('preprocessed', 'converted')
    output_path = os.path.join(output_folder, output_file_name)

    with open(output_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)

    print(f"Conversion completed for {os.path.basename(input_file)}. Results saved to {output_path}.")

def main():
    model = QueryModel(query_type='chat', model_name='gpt-3.5-turbo')
    current_folder = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(current_folder, "../seed_datasets") # directory containing preprocessed JSON files to convert

    for root, dirs, files in os.walk(input_directory):
        for filename in files:
            if filename.startswith('preprocessed_') and filename.endswith('.json'):
                input_file = os.path.join(root, filename)
                process_file(input_file, model)

if __name__ == '__main__':
    main()
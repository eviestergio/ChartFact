from model import QueryModel
import json
import os

def create_supports_prompt(csv,  question, answer):
    prompt = f"""
        You will be provided with a data entry in JSON format deliminated by 3 single quotes. 

        Each data entry contains the following keys: ‘csv’, 'question', 'answer'

        Using the 4 input-output examples deliminated by angle brackets, your task is to convert each 'question' and 'answer' pair to a claim that supports the information and an explanation.

        To provide an explanation as to why this claim is supported by the data, cite specific references of the csv in the entailment claim. Do not mention the question and answer pair in the explanation. These are examples of valid justifications for labelling an entailment claim as Supports:
        - Entailment claim directly states information that is recorded/confirmed in the csv 
        - Entailment claim states information that is synonymous with the information in the csv 

        Ensure that the output is in the format delineated by backticks: 
        `“Entailment claim”: “”,
        “Explanation”: “”`

        Examples: < 
            1. Input: {{
                "csv": "Year,Western Europe,North America,Japan,Emerging countries
                2020,47,47,32,113
                2019,46,43,31,102
                2018,43,34,26,91
                2017,47,29,30,78
                2016,37,25,27,70
                2015,35,21,25,61
                2014,33,22,21,52
                2013,31,17,21,46",
                "question": "How many stores did Saint Laurent operate in Western Europe in 2020?",
                "answer": "47"
            }}
            Output: {{
            “Entailment claim”: “The number of stores Saint Laurent operated in Western Europe in 2020 was 47.”,
            “Explanation”: “This claim is supported by the data in the provided csv file. According to the csv, in the year 2020, Saint Laurent operated 47 stores in Western Europe, as recorded under the column "Western Europe" for that year. Therefore, the entailment claim directly states information that is confirmed in the csv, specifically matching the data point for 2020 in the "Western Europe" column.”
            }}
            2. Input: {{
                "csv": "Year,Domestic Liabilities,Foreign Liabilities
                2005,102600000,-15510000000
                2006,1899000000,66250000000
                2007,5358700000,-15510000000
                2008,46958100000,27577000000
                2009,184518000000,20612000000",
                "question": "In how many years, is the income share held by highest 10% of the population greater than the average income share held by highest 10% of the population taken over all years ?",
                "answer": "1"
            }}
            Output: {{
            “Entailment claim”: “The domestic liabilities increased significantly from 2005 to 2009.”, 
            “Explanation”: “The CSV data shows a clear trend where domestic liabilities grew substantially over the years, starting from 102600000 in 2005 to 184518000000 in 2009. This increase is directly supported by the numerical values provided in the CSV.” 
            }}
            3. Input: {{
                "csv": " y axis label,xaxis label 
                Light Salmon,59.18
                Deep Sky Blue,87.66
                Magenta,62.45
                Navy Blue,69.7
                Rosy Brown,83.18
                Lawn Green,85.84
                Indian Red,74.26",
                "question": "Is Deep Sky Blue greater than Magenta?",
                "answer": "Yes"
            }}
            Output: {{
            “Entailment claim”: “Deep Sky Blue has a value of 87.66 which is greater than Magenta's value of 62.45.”,
            “Explanation”: “The CSV data shows that Deep Sky Blue corresponds to a value of 87.66, whereas Magenta corresponds to 62.45. This directly supports the claim that Deep Sky Blue has a higher value than Magenta based on the numerical comparison in the CSV.” 
            }}
        >

        Output the text for the entailment claim derived from converting the question and answer pair and the explanation based off of the CSV data provided. 

        Data entry: '''{{
            "csv": "{csv}",
            "question": "{question}",
            "answer": "{answer}"
        }}'''
        """
    return prompt

def create_refutes_prompt(entry, supports_claim):
    prompt = ""
    return prompt

def create_nei_prompt(entry, supports_claim):
    prompt = ""
    return prompt

def generate_supports_claim(csv, question, answer, model):
    prompt = create_supports_prompt(csv, question, answer)
    response = model(model_name='gpt-3.5-turbo', query=prompt)

    # Parse response to extract claim and explanation
    claim_start = response.find('“Entailment claim”: “') + len('“Entailment claim”: “')
    claim_end = response.find('”', claim_start)
    claim = response[claim_start:claim_end]
    
    explanation_start = response.find('“Explanation”: “') + len('“Explanation”: “')
    explanation_end = response.find('”', explanation_start)
    explanation = response[explanation_start:explanation_end]

    return claim, explanation

def generate_refutes_claim(entry, model, supports_claim):
    prompt = create_refutes_prompt(entry, supports_claim)
    return model(model_name='gpt-3.5-turbo', query=prompt)

def generate_nei_claim(entry, model, supports_claim):
    prompt = create_nei_prompt(entry, supports_claim)
    return model(model_name='gpt-3.5-turbo', query=prompt)

def process_file(input_file, model):
    
    with open(input_file, 'r') as file:
            entries = json.load(file)

    results = []
    
    for entry in entries:
        # Check if necessary keys exist
        question = entry.get("question")
        answer = entry.get("answer")
        image = entry.get("image")

        if not question or not answer or not image:
            # Add blank entry if any key is missing
            results.append({
                "image": image if image else "",
                "claim": "",
                "label": "Supports",
                "explanation": ""
            })
            continue

        csv_file_path = os.path.join(os.path.dirname(input_file), "tables", f"{entry['image'].split('.')[0]}.csv")
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r') as csv_file:
                csv = csv_file.read()
        else:
            print(f"CSV file {csv_file_path} not found.")
            results.append({
                "image": image,
                "claim": "",
                "label": "Supports",
                "explanation": ""
            })
            continue

        # Generate 'supports' claim
        supports_claim, explanation = generate_supports_claim(csv, question, answer, model)
        results.append({
            "image": entry.get("image", ""),
            "claim": supports_claim,
            "label": "Supports",
            "explanation": explanation
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
    model = QueryModel(query_type='chat')
    current_folder = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(current_folder, "../seed_datasets") # directory containing preprocessed JSON files to convert

    for root, dirs, files in os.walk(input_directory):
        for filename in files:
            if filename.startswith('preprocessed_') and filename.endswith('.json'):
                input_file = os.path.join(root, filename)
                process_file(input_file, model)

if __name__ == '__main__':
    main()
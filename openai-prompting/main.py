from model import QueryModel
import json
import os

def create_supports_prompt(title, table,  question, answer): # 1390 tokens, 6087 characters 
    title_ = title if title else ''
    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with a data entry in JSON format delimited by triple single quotes. Each data entry contains the keys "title", "table”, "question”, and "answer”. The title and table represent the underlying data of a chart.

    Data entry: '''{{
        "title”: "{title_}”
        "table": "{table}",
        "question": "{question}",
        "answer": "{answer}"
    }}'''

    Task: Using the 3 input-output examples below delimited by angle brackets, convert each 'question' and 'answer' pair to a claim that supports the information and provide an explanation.

    Process for generating a 'supports’ claim and explanation:
        1. Develop a supports claim using the question and answer pair. 
        2. Provide an explanation on why this claim supports the data, citing specific references from the chart which is represented by the table and title (if it exists) given. Do not mention the table, or question and answer pair in the explanation; instead, refer to the chart. Valid justifications include: 
            - The supports claim directly states information recorded/confirmed in the chart.
            - The supports claim states information synonymous with that in the chart.

    Output the result as a JSON object with the following keys: "supports claim" and "explanation". The format should strictly follow this structure:
    {{
        "supports claim": "your generated supports claim",
        "explanation": "your explanation for why the claim supports the chart"
    }}

    Examples: < 
    1. Input: {{
        "title”: 'Net insurance of liabilities of government of Iceland', 
        "table": "Year,Domestic Liabilities,Foreign Liabilities
        2005,102600000,-15510000000
        2006,1899000000,66250000000
        2007,5358700000,-15510000000
        2008,46958100000,27577000000
        2009,184518000000,20612000000",
        "question": "In how many years, is the income share held by highest 10% of the population greater than the average income share held by highest 10% of the population taken over all years ?",
        "answer": "1"
        }}
        Output: {{
        "supports claim”: "The domestic liabilities increased significantly from 2005 to 2009.”, 
        "explanation”: "The chart shows a clear trend where domestic liabilities grew substantially over the years, starting from 102600000 in 2005 to 184518000000 in 2009. This increase is directly supported by the numerical values provided in the chart."
        }}
    2. Input: {{
        "title”: '', 
        "table": " y axis label, x axis label 
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
        "supports claim”: "Deep Sky Blue has a value of 87.66 which is greater than Magenta's value of 62.45.”,
        "explanation”: "The chart shows that Deep Sky Blue corresponds to a value of 87.66, whereas Magenta corresponds to 62.45. This directly supports the claim that Deep Sky Blue has a higher value than Magenta based on the numerical comparison in the chart."
        }}
        >
        """

    return prompt

def create_refutes_prompt(title, table, supports_claim): # 519 tokens, 2331 characters
    title_ = title if title else ''
    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with a data entry in JSON format delimited by triple single quotes. Each data entry contains the keys "title”, "table”, and "supports claim”. The title and table represent the underlying data of a chart.

    Data entry: '''{{
        "title”: "{title_}”,
        "table”: "{table}”, 
        "supports claim”: "{supports_claim}”
    }}'''

    Task: Using the input-output example below delimited by angle brackets, generate a 'refutes’ claim and an explanation. Ensure the claim aligns with the data or adjust it to fit the data if necessary.

    Process for generating 'refutes’ claim and explanation:
        1. Identify the information in the chart from the table and title (if it exists), and the supports claim.
        2. Develop a claim that refutes the data based on the supports claim without adding unverifiable information. This can be done by:
            - Wrongly stating factual data, such as changing reported numbers or trends.
            - Misinterpreting or changing one or more factual elements in a way that is plausible but incorrect based on the data.
        3. Provide an explanation on why this claim refutes the data, citing specific discrepancies between the claim and the chart. Valid justifications include:
            - The claim directly states information that refutes the data and/or supports claim 
            - The claim states information that is antonymous with information in the chart and/or supports claim

    Output the result as a JSON object with the following keys: "refutes claim" and "explanation". The format should strictly follow this structure:
    {{
        "refutes claim": "your generated refutes claim",
        "explanation": "your explanation for why the claim refutes the chart"
    }}

    Example: <
    Input: {{
        "title”: "Traits of President Donald Trump”,
        "table”: "Entity,Values
            Caring about ordinary people,23.0
            Well-qualified to be president,26.0
            Charismatic,39.0
            A strong leader,55.0
            Dangerous,62.0
            Intolerant,65.0
            Arrogant,75.0”,
        "supports claim”: "62 percent view President Donald Trump as Dangerous.”
    }}
    Output: {{
        "refutes claim”: "The majority of people consider Donald Trump to be charismatic.”,
        "explanation”: "The claim counters the chart, which shows a lower percentage for 'Charismatic' compared to 'Dangerous'. It misrepresents the chart by suggesting that 'Charismatic' has a majority view, which directly contradicts the higher percentage listed for 'Dangerous'.”
    }}
    >
    """
    
    return prompt

def create_nei_prompt(title, table, supports_claim): # 512 tokens, 2398 characters
    title_ = title if title else ''
    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with a data entry in JSON format delimited by triple single quotes. Each data entry contains the keys "title”, "table”, and "supports claim”. The title and table represent the underlying data of a chart.

    Data entry: '''{{
        "title”: "{title_}”,
        "table”: "{table}”, 
        "supports claim”: "{supports_claim}”
    }}'''

    Task: Using the input-output example delimited by angle brackets, generate a 'not enough information’ claim and an explanation. Ensure the claim aligns with the data or adjust it to fit the data if necessary.

    Process for generating 'not enough information’ claim and explanation:
        1. Assess the chart data from table and title (if it exists) with the supports claim for information gaps or unspecified details.
        2. Develop a claim based on these gaps without explicitly stating the lack of information. This can be done by:
            - Offering different scenarios or conclusions that are not directly contradicted by the data in the chart.
            - Suggesting causes or reasons for trends in the data that are not explicitly supported or denied by the data in the chart.
        3. Provide an explanation on why this claim is classified as 'not enough information' by highlighting the lack of data in the chart to support or refute the claim, making it unverifiable. Valid justifications include:
            - The claim cannot be confirmed or disproven with the given data.
            - Additional information from other sources would be required to verify the claim.

    Output the result as a JSON object with the following keys: "not enough information claim" and "explanation". The format should strictly follow this structure:
    {{
        "not enough information claim": "your generated not enough information claim",
        "explanation": "your explanation for why the claim lacks enough information"
    }}

    Example: <
    Input: {{
        "title”: "Traits of President Donald Trump”,
        "table”: "Entity,Values
            Caring about ordinary people,23.0
            Well-qualified to be president,26.0
            Charismatic,39.0
            A strong leader,55.0
            Dangerous,62.0
            Intolerant,65.0
            Arrogant,75.0”,
        "supports claim”: "62 percent view President Donald Trump as Dangerous.”
    }}
    Output: {{
        "not enough information claim”: "President Donald Trump's approach to international relations contributes to their perception as Dangerous.”,
        "explanation”: "This claim speculates on information not provided in the table, as there are no data regarding international relations, making the connection to the perception of being 'Dangerous' unverifiable.”
    }}
    >
    """
    
    return prompt

def parse_json_response(response):
    ''' Parse JSON object response to extract claim and explanation '''
    try:
        response_json = json.loads(response)
        return response_json
    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
        return {}

def generate_supports_claim(title, table, question, answer, model):
    prompt = create_supports_prompt(title, table, question, answer)
    response = model(model_name='gpt-3.5-turbo', query=prompt)
    response_json = parse_json_response(response)

    # If failed, add empty entries to filter out from final dataset
    if not response_json:
        print("Failed to parse response for supports claim.")
        return "", "" 
    
    claim = response_json['supports claim']
    explanation = response_json['explanation']

    return claim, explanation

def generate_refutes_claim(title, table, supports_claim, model):
    prompt = create_refutes_prompt(title, table, supports_claim)
    response = model(model_name='gpt-3.5-turbo', query=prompt)
    response_json = parse_json_response(response)

    # If failed, add empty entries to filter out from final dataset
    if not response_json:
        print("Failed to parse response for refutes claim.")
        return "", "" 
    
    claim = response_json['refutes claim']
    explanation = response_json['explanation']

    return claim, explanation

def generate_nei_claim(title, table, supports_claim, model):
    prompt = create_nei_prompt(title, table, supports_claim)
    response = model(model_name='gpt-3.5-turbo', query=prompt)
    response_json = parse_json_response(response)

    # If failed, add empty entries to filter out from final dataset
    if not response_json:
        print("Failed to parse response for not enough information claim.")
        return "", "" 
    
    claim = response_json['not enough information claim']
    explanation = response_json['explanation']

    return claim, explanation

def process_file(input_file, model):
    
    with open(input_file, 'r') as file:
        entries = json.load(file)

    results = []
    
    for entry in entries:
        # Check if necessary keys exist
        question = entry.get("question")
        answer = entry.get("answer")
        image = entry.get("image")

        base_csv_file_path = os.path.join(os.path.dirname(input_file), "tables", f"{entry['image'].split('.')[0]}")
        csv_file_path = base_csv_file_path + "-converted.csv"
        regular_csv_file_path = base_csv_file_path + ".csv"
        title_file_path = base_csv_file_path + "-title.txt"

        # Read CSV file (prioritize '-converted' file)
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r') as csv_file:
                table = csv_file.read()
        elif os.path.exists(regular_csv_file_path):
            with open(regular_csv_file_path, 'r') as csv_file:
                table = csv_file.read()
        else:
            table = None

        # Read title file if it exists
        if os.path.exists(title_file_path):
            with open(title_file_path, 'r') as title_file:
                title = title_file.read().strip()
        else:
            title = None

        # Check for missing data (excluding optional title)
        if not question or not answer or not image or (table is None):
            print(f"Skipping entry due to missing data: {entry}")
            continue

        # Generate 'supports' claim
        supports_claim, explanation = generate_supports_claim(title, table, question, answer, model)
        results.append({
            "image": image,
            "claim": supports_claim,
            "label": "Supports",
            "explanation": explanation
        })

        # Generate 'refutes' claim using 'supports' claim
        refutes_claim, explanation = generate_refutes_claim(title, table, supports_claim, model)
        results.append({
            "image": image,
            "claim": refutes_claim,
            "label": "Refutes",
            "explanation": explanation
        })

        # Generate 'not enough information' claim using 'supports' claim
        nei_claim, explanation = generate_nei_claim(title, table, supports_claim, model)
        results.append({
            "image": image,
            "claim": nei_claim,
            "label": "Not enough information",
            "explanation": explanation
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
    model = QueryModel(query_type='json_object')
    current_folder = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(current_folder, "../seed_datasets") # directory containing preprocessed JSON files to convert

    for root, dirs, files in os.walk(input_directory):
        for filename in files:
            if filename.startswith('preprocessed_') and filename.endswith('.json'):
                input_file = os.path.join(root, filename)
                process_file(input_file, model)

if __name__ == '__main__':
    main()
from model import QueryModel
import json
import os
import shutil
import sys
import base64

# --- Image input prompts ---

## Supports prompts
def create_zero_shot_supports_prompt(image, question, answer): # (final) 254 tokens, 1228 character w/o image and Q&A
    """ Creates a zero-shot prompt to generate a 'supports' claim with an explanation using image input based on a Q&A pair. """

    prompt = f"""
    You are a helpful assistant designed to convert question-answering pairs into claims and output the result in JSON.

    You will receive as input a chart image along with a question about the chart and its corresponding answer, delimited by triple single quotes (see data input below).

    Data input: '''
        "chart": {image},
        "question": "{question}",
        "answer": "{answer}"
    '''

    Task: Convert the 'question' and 'answer' pair to a declarative sentence and generate an explanation of why the sentence is true based on the information in the chart.

    Process for generating a declarative sentence and an explanation:
        1. Check that the "answer" to the "question" is correct by examining the "chart". If the "answer" in correct, generate the correct answer and use this as the "answer" going forward.
        2. Using only the "question" and "answer", convert them into a sentence such that the resulting sentence is supported by the data in the chart. 
        3. Validate that the generated sentence is correct by carefully analyzing the chart image. 
        4. Explain why the sentence is correct by referencing information extracted from the chart. Note: information in charts can be expressed through visual elements, data points, categorical labels, numbers, etc. 

    Output the result as a JSON object strictly following this structure:
    {{
        "supports claim": "your generated sentence",
        "explanation": "your explanation for why the sentence supports the chart"
    }}
    """

    return prompt

def create_zero_shot_supports_prompt_o(question, answer): #(!) 254 tokens, 1228 character w/o image and Q&A (w/ trying to fix incorrect input data)
    """ Creates a zero-shot prompt to generate a 'supports' claim with an explanation using image input based on a Q&A pair. """

    prompt = f"""
    You are a helpful assistant designed to convert question-answering pairs into claims and output the result in JSON.

    You will receive as input a chart image along with a question about the chart and its corresponding answer, delimited by triple single quotes (see data input below).

    Data input: '''
        "question": "{question}",
        "answer": "{answer}"
    '''

    Task: Convert the 'question' and 'answer' pair to a declarative sentence and generate an explanation of why the sentence is true based on the information in the chart.

    Process for generating a declarative sentence and an explanation:
        1. Validate whether the "question" and "answer" pair can be reliably supported by analyzing the chart image. Ensure the information is accurate and that any numerical values are not overly specific or difficult to clearly observe in the chart.
        2. If the Q&A pair is reliably supported, generate a declarative sentence directly based on the "question" and "answer."
        3. If the Q&A pair is not reliably supported (e.g., due to incorrect information or overly specific values), generate a new sentence that is clearly supported by observable information in the chart.
        4. Explain why the final sentence (whether derived from the Q&A pair or newly generated) is correct by referencing specific information extracted from the chart. Note: information in charts can be expressed through visual elements, data points, trends, categorical labels, etc.

    Output the result as a JSON object strictly following this structure:
    {{
        "supports claim": "your generated sentence",
        "explanation": "your explanation for why the sentence supports the chart"
    }}
    """

    return prompt

def create_few_shot_supports_prompt(question, answer): # 504 tokens, 2318 characters
    """ Creates a few-shot prompt to generate a 'supports' claim with an explanation using image input based on a Q&A pair. """

    image1 = encode_image("plotQA_39-test.png", "seed_datasets/PlotQA/test/png")
    image2 = encode_image("figureQA_1-1-test.png", "seed_datasets/FigureQA/test/png") 

    prompt = f"""
    You are a helpful assistant designed to convert question-answering pairs into claims and output the result in JSON.

    You will receive as input a chart image along with a question about the chart and its corresponding answer, delimited by triple single quotes (see data input below).

    Data input: '''
        "question": "{question}",
        "answer": "{answer}"
    '''

    Task: Convert the 'question' and 'answer' pair to a declarative sentence and generate an explanation of why the sentence is true given the information in the chart.

    Process for generating a declarative sentence and an explanation:
        1. Using only the "question" and "answer", convert them into a sentence such that the resulting sentence is supported by the data in the chart. 
        2. Validate that the generated sentence is correct by carefully analyzing the chart image. 
        3. Explain why the sentence is correct by referencing information extracted from the chart. Note: information in charts can be expressed through visual elements, data points, categorical labels, etc. 

    Output the result as a JSON object strictly following this structure:
    {{
        "supports claim": "your generated supports claim",
        "explanation": "your explanation for why the claim supports the chart"
    }}

    Examples:  
    Input: 
        "image": {image1}
        "question": "Did the domestic liabilities increase from 2005 to 2009?"
        "answer": "Yes"
    Output: {{
        "supports claim": "The domestic liabilities increased significantly from 2005 to 2009.", 
        "explanation": "The chart shows a clear trend where domestic liabilities grew substantially over the years, starting from 102600000 in 2005 to 184518000000 in 2009. This increase is directly supported by the numerical values provided in the chart."
    }}

    Input: 
        "image": {image2}
        "question": "Is Deep Sky Blue greater than Magenta?"
        "answer": "Yes"
    Output: {{
        "supports claim": "Deep Sky Blue has a higher value than Magenta.",
        "explanation": "The chart shows that the bar representing Deep Sky Blue has a visibly higher height than the one for Magenta, supporting the claim that Deep Sky Blue's value is indeed greater."
    }}
    """

    return prompt

def create_zero_shot_supports_prompt_wo_QA(): #(!)
    """ Creates a zero-shot prompt to generate a 'supports' claim with an explanation using image input without a Q&A pair. """

    prompt = f"""
    You are a helpful assistant designed to convert question-answering pairs into claims and output the result in JSON.

    Task: Generate a declarative sentence that supports the information in the chart and provide an explanation of why this sentence is false.

    Process for generating a 'supports' claim and explanation:
        1. Using the chart image, develop a declarative sentence that is supported by the information in the chart.
        2. Validate that the generated sentence is correct by carefully analyzing the chart image. 
        3. Explain why the generated sentence is correct by referencing information extracted from the chart. Note: information in charts can be expressed through visual elements, data points, trends, categorical labels, etc.

    Output the result as a JSON object strictly following this structure:
    {{
        "supports claim": "your generated sentence",
        "explanation": "your explanation for why the sentence supports the chart"
    }}
    """

    return prompt

def create_few_shot_supports_prompt_wo_QA():
    """ Creates a few-shot prompt to generate a 'supports' claim with an explanation using image input without a Q&A pair. """

    image1 = encode_image("plotQA_39-test.png", "seed_datasets/PlotQA/test/png")
    image2 = encode_image("figureQA_1-1-test.png", "seed_datasets/FigureQA/test/png") 

    prompt = f"""
    You are a helpful assistant designed to generate claims based on the given chart and output the result in JSON.

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

### Simple supports prompt
def create_supports_prompt_simple(question, answer): # (final) 254 tokens, 1221 characters
    ''' Creates a simplified prompt to generate a 'supports' claim without an explanation. '''
    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with a question and its corresponding answer delimited by triple single quotes.

    Data entry: '''
        question: "{question}",
        answer: "{answer}"
    '''

    Task: Using the two input-output examples delimited by angle brackets, convert each 'question' and 'answer' pair to a claim that supports the information.

    Output the result as a JSON object with the key "supports claim". The format should strictly follow this structure:
    {{
        "supports claim": "your generated supports claim"
    }}

    Examples: < 
     1. Input: {{
            "question": "How many stores did Saint Laurent operate in Western Europe in 2020?",
            "answer": "47"
        }}
        Output: {{
            "supports claim": "Saint Laurent operated 47 stores in Western Europe in 2020."
        }},
     2. Input: {{
            "question": "What is the title of the graph?",
            "answer": "Net disbursements of loans from International Monetary Fund"
        }} 
        Output: {{
            "supports claim": "The title of the graph is Net disbursements of loans from International Monetary Fund."
        }},
    >
    """
    
    return prompt

## Refutes prompts
def create_zero_shot_refutes_prompt(image, supports_claim): # (final) 279 tokens, 1355 characters w/o image and support claim
    # Image must be included due to issue with figureQA_37961-train.png: When there are no numbers in the chart, the model struggles
    ''' Creates a zero-shot prompt to generate a 'refutes' claim with an explanation using image input based on a Q&A pair. '''
    
    prompt = f"""
    You are a helpful assistant designed to generate contradictory claims based on provided supporting claims and output the result in JSON.

    You will receive as input a chart image along with a claim that supports the information in the chart, delimited by triple single quotes (see data input below).

    Data input: '''
        "chart": {image},
        "supports claim": "{supports_claim}"
    '''

    Task: Generate a 'refutes' claim that contradicts the information in the chart and provide an explanation. 

    Process for generating a 'refutes' claim and explanation:
        1. Develop a sentence that refutes the information in the chart based on the given claim that supports the information in the chart, without adding unverifiable information. This can be done by changing reported numbers, trends, or other factual elements in a plausible but incorrect way. Ensure that the statement does not reveal that it is refuted by the chart. 
        2. Validate that the generated sentences refutes the information in the chart by carefully analyzing the chart image. 
        3. Explain why the sentence refutes the chart image by referencing information extracted from the chart. Note: information in charts can be expressed through visual elements, data points, categorical labels, numbers, etc. In the explanation, do not refer to the given supports claim.

    Output the result as a JSON object strictly following this structure:
    {{
        "refutes claim": "your generated sentence",
        "explanation": "your explanation for why the sentence refutes the chart"
    }}
    """
    
    return prompt

def create_few_shot_refutes_prompt(image, supports_claim):
    ''' Creates a few-shot prompt to generate a 'refutes' claim with an explanation using image input based on a Q&A pair. '''
    
    image1 = encode_image("plotQA_39-test.png", "seed_datasets/PlotQA/test/png") #change
    image2 = encode_image("figureQA_2-3-test.png", "seed_datasets/FigureQA/test/png") #change

    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with an image of a chart along with a claim that supports the information in the chart, delimited by triple single quotes.

    Data input: '''
        "image": {image},
        "supports claim": "{supports_claim}"
    '''

    Task: Using the two input-output examples below delimited by angle brackets, generate a 'refutes' claim that contradicts the information in the chart and provide an explanation. 

    Process for generating a 'refutes' claim and explanation:
        1. Develop a refutes claim based on the given supports claim without adding unverifiable information. This can be done by changing reported numbers, trends, or other factual elements in a plausible but incorrect way.
        2. Validate that your claim refutes the information in the chart by carefully analyzing the image. 
        3. Explain why the claim refutes the chart by referencing specific visual aspects and data points visible in the image. For example, reference specific values, lines, or categories shown in the chart. In the explanation, do not refer to the supports claim.

    Output the result as a JSON object with the following keys: "refutes claim" and "explanation". The format should strictly follow this structure:
    {{
        "refutes claim": "your generated refutes claim",
        "explanation": "your explanation for why the claim refutes the chart"
    }}

    Examples: <
     1. Input: {{
        "image": {image1},
        "supports claim": "The merchandise exports in 2007 were the minimum among the years shown in the chart."
        }}
        Output: {{
        "refutes claim": "The merchandise exports in 2010 were the highest among the years shown in the chart.",
        "explanation": "This claim refutes the chart as it inaccurately states that merchandise exports peaked in 2010. However, according to the chart, merchandise exports were highest in 2008 with a value of 1.22, and in 2010, the exports decreased to 1.05. Therefore, the claim contradicts the actual data presented in the chart."
        }}
     2. Input: {{
        "image": "{image2}",
        "supports claim": "Chartreuse has a value of 55, which is the maximum in the chart."
        }}
        Output: {{
        "refutes claim": "Medium Mint has a value of 0, which is the minimum in the chart.",
        "explanation": "The refutes claim incorrectly states that Medium Mint has a value of 0, indicating it is the minimum in the chart. However, according to the chart data, Medium Mint actually has a value of 18. This misstatement contradicts the factual information present in the chart, where 0 is associated with a different color. Therefore, the refutes claim directly contradicts the actual data provided in the chart."
        }}
    >
    """
    
    return prompt

def create_zero_shot_refutes_prompt_wo_QA(image):
    ''' Creates a zero-shot prompt to generate a 'refutes' claim with an explanation using image input. '''
    
    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with an image of a chart delimited by triple single quotes.

    Data input: '''
        "image": {image},
    '''

    Task: Generate a 'refutes' claim that contradicts the information in the chart and provide an explanation. 

    Process for generating a 'refutes' claim and explanation:
        1. Develop a refutes claim without adding unverifiable information. This can be done by changing reported numbers, trends, or other factual elements in a plausible but incorrect way.
        2. Validate that your claim refutes the information in the chart by carefully analyzing the image. 
        3. Explain why the claim refutes the chart by referencing specific visual aspects and data points visible in the image. For example, reference specific values, lines, or categories shown in the chart.

    Process for generating 'refutes' claim and explanation:
        1. Develop a claim that refutes the data without adding unverifiable information. This can be done by:
            - Wrongly stating factual data, such as changing reported numbers or trends.
            - Misinterpreting or changing one or more factual elements in a way that is plausible but incorrect based on the data.
        2. Explain why the claim refutes the data. Use specific references form the chart. Valid justifications include:
            - The claim directly states information that refutes the chart. 
            - The claim states information that is antonymous with information in the chart.

    Output the result as a JSON object with the following keys: "refutes claim" and "explanation". The format should strictly follow this structure:
    {{
        "refutes claim": "your generated refutes claim",
        "explanation": "your explanation for why the claim refutes the chart"
    }}
    """

    return prompt

def create_few_shot_refutes_prompt_wo_QA(image):
    ''' Creates a few-shot prompt to generate a 'refutes' claim with an explanation using image input. '''
    
    image1 = encode_image("plotQA_39-test.png", "seed_datasets/PlotQA/test/png") #change
    image2 = encode_image("figureQA_2-3-test.png", "seed_datasets/FigureQA/test/png") #change

    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with an image of a chart delimited by triple single quotes.

    Data input: '''
        "image": {image},
    '''

    Task: Using the two input-output examples below delimited by angle brackets, generate a 'refutes' claim that contradicts the information in the chart and provide an explanation. 

    Process for generating a 'refutes' claim and explanation:
        1. Develop a refutes claim without adding unverifiable information. This can be done by changing reported numbers, trends, or other factual elements in a plausible but incorrect way.
        2. Validate that your claim refutes the information in the chart by carefully analyzing the image. 
        3. Explain why the claim refutes the chart by referencing specific visual aspects and data points visible in the image. For example, reference specific values, lines, or categories shown in the chart.

    Process for generating 'refutes' claim and explanation:
        1. Develop a claim that refutes the data without adding unverifiable information. This can be done by:
            - Wrongly stating factual data, such as changing reported numbers or trends.
            - Misinterpreting or changing one or more factual elements in a way that is plausible but incorrect based on the data.
        2. Explain why the claim refutes the data. Use specific references form the chart. Valid justifications include:
            - The claim directly states information that refutes the chart. 
            - The claim states information that is antonymous with information in the chart.

    Output the result as a JSON object with the following keys: "refutes claim" and "explanation". The format should strictly follow this structure:
    {{
        "refutes claim": "your generated refutes claim",
        "explanation": "your explanation for why the claim refutes the chart"
    }}

    Examples: <
     1. Input: {{
        "image": {image1},
        "supports claim": "The merchandise exports in 2007 were the minimum among the years shown in the chart."
        }}
        Output: {{
        "refutes claim": "The merchandise exports in 2010 were the highest among the years shown in the chart.",
        "explanation": "This claim refutes the chart as it inaccurately states that merchandise exports peaked in 2010. However, according to the chart, merchandise exports were highest in 2008 with a value of 1.22, and in 2010, the exports decreased to 1.05. Therefore, the claim contradicts the actual data presented in the chart."
        }}
     2. Input: {{
        "image": "{image2}",
        "supports claim": "Chartreuse has a value of 55, which is the maximum in the chart."
        }}
        Output: {{
        "refutes claim": "Medium Mint has a value of 0, which is the minimum in the chart.",
        "explanation": "The refutes claim incorrectly states that Medium Mint has a value of 0, indicating it is the minimum in the chart. However, according to the chart data, Medium Mint actually has a value of 18. This misstatement contradicts the factual information present in the chart, where 0 is associated with a different color. Therefore, the refutes claim directly contradicts the actual data provided in the chart."
        }}
    >
    """

    return prompt

## Not enough information prompts
def create_zero_shot_nei_prompt(supports_claim): # (final) 269 tokens, 1390 characters w/o image and support claim
    ''' Creates a zero-shot prompt to generate a 'not enough information' claim with an explanation. '''

    prompt = f"""
    You are a helpful assistant designed to generate sentences that neither fully support nor refute a given chart-based claim and output the result in JSON.

    You will receive as input a chart image along with a claim that supports the information in the chart, delimited by triple single quotes (see data input below).

    Data input: '''
        "supports claim": "{supports_claim}"
    '''

    Task: Generate a 'not enough information' claim that neither fully supports or refutes the information in the chart and provide an explanation. 

    Process for generating a 'not enough information' claim and explanation:
        1. Analyze the chart data and the provided supports claim for gaps or missing details that prevent fully supporting or refuting the claim.
        2. Generate a sentence based on these gaps, asserting, as if it were a fact, plausible scenarios or causes that, in reality, neither directly support nor refute the supports_claim but that is related to the supports_claim. Ensure that the sentence does not reveal that there is not enough information for it to be evaluated by the chart.
        3. Explain why the generated sentence cannot be verified with the available data by referencing information extracted from the chart. Note: information in charts can be expressed through visual elements, data points, categorical labels, numbers, etc. In the explanation, do not refer to the given supports claim.
        
    Output the result as a JSON object strictly following this structure:    
    {{
        "not enough information claim": "your generated sentence",
        "explanation": "your explanation for why the sentence lacks enough information to support the chart"
    }}
    """

    return prompt

def create_few_shot_nei_prompt(image, supports_claim):
    ''' Creates a few-shot prompt to generate a 'not enough information' claim with an explanation. '''
    
    image1 = encode_image("chartQA_166.png", "seed_datasets/ChartQA/test/png") #OK
    image2 = encode_image("figureQA_2-3-test.png", "seed_datasets/FigureQA/test/png") #change

    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with an image of a chart along with a claim that supports the information in the chart, delimited by triple single quotes.

    Data input: '''
        "image": {image},
        "supports claim": "{supports_claim}"
    '''

    Task: Using the two input-output examples delimited by angle brackets, generate a 'not enough information' claim that neither fully supports or refutes the information in the chart and provide an explanation. 

    Process for generating a 'not enough information' claim and explanation:
        1. Analyze the chart data and the provided supports claim for gaps or missing details that prevent fully supporting or refuting the claim.
        2. Develop a claim based on these gaps, suggesting plausible scenarios or causes that neither directly support nor refute the original claim but is related to it.
        3. Provide an explanation for why the claim cannot be verified with the available information, referencing specific aspects of the chart. In the explanation, do not refer to the original supports claim.

    Output the result as a JSON object with the following keys: "not enough information claim" and "explanation". The format should strictly follow this structure:
    {{
        "not enough information claim": "your generated not enough information claim",
        "explanation": "your explanation for why the claim lacks enough information"
    }}

    Example: <
     1. Input: {{
        "image": "{image1}",
        "supports claim": "62 percent view President Donald Trump as Dangerous."
        }}
        Output: {{
        "not enough information claim": "President Donald Trump's approach to international relations contributes to their perception as Dangerous.",
        "explanation": "This claim speculates on information not provided in the table, as there is no data regarding international relations, making the connection to the perception of being 'Dangerous' unverifiable."
        }}
     2. Input: {{
        "image": "{image2}",
        "supports claim": "Dark Cyan is not the low median."
        }}
        Output: {{
        "not enough information claim": "Dark Cyan would be the median if the dataset included more color values.",
        "explanation": "This claim suggests that adding more color values could shift the median to Dark Cyan. However, the current dataset does not provide information on potential additional values or their distribution, making it impossible to verify this claim."
        }}
    >
    """

    return prompt

def create_zero_shot_nei_prompt_wo_QA(image):  
    ''' Creates a zero-shot prompt to generate a 'not enough information' claim with an explanation without a support claim based on the Q&A pair. '''

    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with an image of a chart along with a claim that supports the information in the chart, delimited by triple single quotes.

    Data input: '''
        "image": {image}
    '''

    Task: Generate a 'not enough information' claim that neither fully supports or refutes the information in the chart and provide an explanation. 

    Process for generating a 'not enough information' claim and explanation:
        1. Identify gaps or unspecified details that make it difficult to fully support or refute the information in the chart.
        2. Develop a claim based on these gaps, suggesting plausible scenarios or causes not directly confirmed or denied by the chart.
        3. Provide an explanation for why the claim cannot be verified with the available information, using specific references from the chart. 

    Output the result as a JSON object with the following keys: "not enough information claim" and "explanation". The format should strictly follow this structure:
    {{
        "not enough information claim": "your generated not enough information claim",
        "explanation": "your explanation for why the claim lacks enough information"
    }}
    """

    return prompt

def create_few_shot_nei_prompt_wo_QA(image):
    ''' Creates a few -shot prompt to generate a 'not enough information' claim with an explanation without a support claim based on the Q&A pair. '''

    image1 = encode_image("chartQA_166.png", "seed_datasets/ChartQA/test/png") #OK
    image2 = encode_image("figureQA_2-3-test.png", "seed_datasets/FigureQA/test/png") #change

    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with an image of a chart along with a claim that supports the information in the chart, delimited by triple single quotes.

    Data input: '''
        "image": {image}
    '''

    Task: Using the two input-output examples delimited by angle brackets, generate a 'not enough information' claim that neither fully supports or refutes the information in the chart and provide an explanation. 

    Process for generating a 'not enough information' claim and explanation:
        1. Identify gaps or unspecified details that make it difficult to fully support or refute the information in the chart.
        2. Develop a claim based on these gaps, suggesting plausible scenarios or causes not directly confirmed or denied by the chart.
        3. Provide an explanation for why the claim cannot be verified with the available information, using specific references from the chart. 

    Output the result as a JSON object with the following keys: "not enough information claim" and "explanation". The format should strictly follow this structure:
    {{
        "not enough information claim": "your generated not enough information claim",
        "explanation": "your explanation for why the claim lacks enough information"
    }}

    Example: <
     1. Input: {{
        "image": "{image1}",
        "supports claim": "62 percent view President Donald Trump as Dangerous."
        }}
        Output: {{
        "not enough information claim": "President Donald Trump's approach to international relations contributes to their perception as Dangerous.",
        "explanation": "This claim speculates on information not provided in the table, as there is no data regarding international relations, making the connection to the perception of being 'Dangerous' unverifiable."
        }}
     2. Input: {{
        "image": "{image2}",
        "supports claim": "Dark Cyan is not the low median."
        }}
        Output: {{
        "not enough information claim": "Dark Cyan would be the median if the dataset included more color values.",
        "explanation": "This claim suggests that adding more color values could shift the median to Dark Cyan. However, the current dataset does not provide information on potential additional values or their distribution, making it impossible to verify this claim."
        }}
    >
    """

    return prompt

# --- Table input prompts ---
def create_supports_prompt_w_table(title, table,  question, answer): # 783 tokens, 3349 characters 
    ''' Creates a prompt to generate a 'supports' claim with an explanation. '''
    title_ = f'"title": "{title}",' if title else ''
    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with a data entry in JSON format delimited by triple single quotes. Each data entry contains the keys "title", "table", "question", and "answer". The "title" and "table" represent the underlying data of a chart.

    Data entry: '''{{
        {title_}
        "table": "{table}",
        "question": "{question}",
        "answer": "{answer}"
    }}'''

    Task: Using the two input-output examples below delimited by angle brackets, convert each 'question' and 'answer' pair to a claim that supports the information and provide an explanation.

    Process for generating a 'supports' claim and explanation:
        1. Using only the "question" and "answer", develop a claim that is supported by the data. 
        2. Provide an explanation on why this claim supports the data. Use specific references to the table and title (if it exists) but referring to neither by name, instead call both the "chart". If there is no title, do not mention the chart being titled. Valid justifications include: 
            - The supports claim directly states information recorded/confirmed in the chart.
            - The supports claim states information synonymous with that in the chart.

    Output the result as a JSON object with the following keys: "supports claim" and "explanation". The format should strictly follow this structure:
    {{
        "supports claim": "your generated supports claim",
        "explanation": "your explanation for why the claim supports the chart"
    }}

    Examples: < 
     1. Input: {{
        "title": 'Net insurance of liabilities of government of Iceland', 
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
        "supports claim": "The income share held by the highest 10% of the population was greater than the average income share held by the highest 10% of the population in 1 year.", 
        "explanation": "The chart shows data over several years where the income shares of the highest 10% are listed. Comparing these figures reveals that in one specific year, the income share of the top 10% exceeded the average income share held by the top 10% across all years."
        }}
     2. Input: {{
        "table": "y axis label, x axis label 
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
        "supports claim": "Deep Sky Blue has a higher value than Magenta.",
        "explanation": "The chart indicates that Deep Sky Blue is recorded with a value of 87.66, while Magenta is recorded with 62.45. Therefore, it is confirmed that Deep Sky Blue's value is indeed greater than that of Magenta, supporting the claim."
        }}
    >
    """

    return prompt

def create_refutes_prompt_w_table(title, table, supports_claim): # 771 tokens, 3433 characters
    ''' Creates a prompt to generate a 'refutes' claim with an explanation. '''

    title_ = f'"title": "{title}",' if title else ''    
    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with a data entry in JSON format delimited by triple single quotes. Each data entry contains the keys "title", "table", and "supports claim". The "title" and "table" represent the underlying data of a chart.

    Data entry: '''{{
        {title_}
        "table": "{table}", 
        "supports claim": "{supports_claim}"
    }}'''

    Task: Using the two input-output examples below delimited by angle brackets, generate a 'refutes' claim and an explanation. Ensure the claim aligns with the data or adjust it to fit the data if necessary.

    Process for generating 'refutes' claim and explanation:
        1. Develop a claim that refutes the data based on the supports claim without adding unverifiable information. This can be done by:
            - Wrongly stating factual data, such as changing reported numbers or trends.
            - Misinterpreting or changing one or more factual elements in a way that is plausible but incorrect based on the data.
        2. Explain why the claim refutes the data. Use specific references to the table and title (if it exists) but referring to neither by name, instead call both the "chart". In the explanation, do not refer to the supports claim. Valid justifications include:
            - The claim directly states information that refutes the chart. 
            - The claim states information that is antonymous with information in the chart.

    Output the result as a JSON object with the following keys: "refutes claim" and "explanation". The format should strictly follow this structure:
    {{
        "refutes claim": "your generated refutes claim",
        "explanation": "your explanation for why the claim refutes the chart"
    }}

    Examples: <
     1. Input: {{
        "title": "Merchandise exports between developing economies in Europe and Heavily indebted poor countries",
        "table": "Year,Merchandise Exports
            2007,0.99
            2008,1.22
            2009,1.06
            2010,1.05",
        "supports claim": "The merchandise exports in 2007 were the minimum among the years shown in the chart."
        }}
        Output: {{
        "refutes claim": "The merchandise exports in 2010 were the highest among the years shown in the chart.",
        "explanation": "This claim refutes the chart as it inaccurately states that merchandise exports peaked in 2010. However, according to the chart, merchandise exports were highest in 2008 with a value of 1.22, and in 2010, the exports decreased to 1.05. Therefore, the claim contradicts the actual data presented in the chart."
        }}
     2. Input: {{
        "table": "yaxis_label,title Magenta,0 Medium Mint,18 Web Gray,36 Chartreuse,55",
        "supports claim": "Chartreuse has a value of 55, which is the maximum in the chart."
        }}
        Output: {{
        "refutes claim": "Medium Mint has a value of 0, which is the minimum in the chart.",
        "explanation": "The refutes claim incorrectly states that Medium Mint has a value of 0, indicating it is the minimum in the chart. However, according to the chart data, Medium Mint actually has a value of 18. This misstatement contradicts the factual information present in the chart, where 0 is associated with a different color. Therefore, the refutes claim directly contradicts the actual data provided in the chart."
        }}
    >
    """
    
    return prompt

def create_nei_prompt_w_table(title, table, supports_claim): # 733 tokens, 3531 characters
    ''' Creates a prompt to generate a 'not enough information' claim with an explanation. '''
    title_ = f'"title": "{title}",' if title else ''  
    prompt = f"""
    You are a helpful assistant designed to output JSON.

    You will be provided with a data entry in JSON format delimited by triple single quotes. Each data entry contains the keys "title", "table", and "supports claim". The title and table represent the underlying data of a chart.

    Data entry: '''{{
        {title_}
        "table": "{table}", 
        "supports claim": "{supports_claim}"
    }}'''

    Task: Using the two input-output examples delimited by angle brackets, generate a 'not enough information' claim and an explanation. Ensure the claim aligns with the data or adjust it to fit the data if necessary.

    Process for generating 'not enough information' claim and explanation:
        1. Assess the chart data from table and title (if it exists) with the supports claim for information gaps or unspecified details.
        2. Develop a claim based on these gaps without explicitly stating the lack of information. This can be done by:
            - Offering different scenarios or conclusions that are not directly contradicted by the data in the chart.
            - Suggesting causes or reasons for trends in the data that are not explicitly supported or denied by the data in the chart.
        3. Provide an explanation on why this claim is classified as 'not enough information'. Use specific references to the table and title (if it exists) but referring to neither by name, instead call both the "chart". Show the lack of data in the chart to support or refute the claim, making it unverifiable. In the explanation, do not refer to the supports claim. Valid justifications include:
            - The claim cannot be confirmed or disproven with the given data.
            - Additional information from other sources would be required to verify the claim.

    Output the result as a JSON object with the following keys: "not enough information claim" and "explanation". The format should strictly follow this structure:
    {{
        "not enough information claim": "your generated not enough information claim",
        "explanation": "your explanation for why the claim lacks enough information"
    }}

    Example: <
     1. Input: {{
        "title": "Traits of President Donald Trump",
        "table": "Entity,Values
            Caring about ordinary people,23.0
            Well-qualified to be president,26.0
            Charismatic,39.0
            A strong leader,55.0
            Dangerous,62.0
            Intolerant,65.0
            Arrogant,75.0",
        "supports claim": "62 percent view President Donald Trump as Dangerous."
        }}
        Output: {{
        "not enough information claim": "President Donald Trump's approach to international relations contributes to their perception as Dangerous.",
        "explanation": "This claim speculates on information not provided in the table, as there is no data regarding international relations, making the connection to the perception of being 'Dangerous' unverifiable."
        }}
     2. Input: {{
        "table": "y axis label,title Indian Red,35 Dim Gray,57 Dark Cyan,22 Light Salmon,55 Dark Khaki,95 Salmon,15 Indigo,5 Web Maroon,46 Navy Blue,18",
        "supports claim": "Dark Cyan is not the low median."
        }}
        Output: {{
        "not enough information claim": "Dark Cyan would be the median if the dataset included more color values.",
        "explanation": "This claim suggests that adding more color values could shift the median to Dark Cyan. However, the current dataset does not provide information on potential additional values or their distribution, making it impossible to verify this claim."
        }}
    >
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

def generate_supports_claim(image_path, question, answer, model, base_dir):
    ''' Generate a 'supports' claim with an explanation. '''
    base64_image = encode_image(image_path, base_dir)
    prompt = create_zero_shot_supports_prompt(base64_image, question, answer) # change prompt version here
    response = model(model_name='gpt-4o-mini', query=prompt, image_base64=base64_image) # change model here
    response_json = parse_json_response(response)

    # If failed, add empty entries to filter out from final dataset
    if not response_json:
        print("Failed to parse response for supports claim.")
        return "", "" 
    
    claim = response_json['supports claim']
    explanation = response_json['explanation']

    return claim, explanation

def generate_supports_claim_simple(question, answer, model): 
    ''' Generate a simplified 'supports' claim without an explanation. '''
    prompt = create_supports_prompt_simple(question, answer) # leave prompt as is
    response = model(model_name='gpt-3.5-turbo', query=prompt) # leave model as is
    response_json = parse_json_response(response)

    # If failed, add empty entries to filter out from final dataset
    if not response_json:
        print("Failed to parse response for supports claim.")
        return ""

    claim = response_json['supports claim']
    return claim

def generate_refutes_claim(image_path, supports_claim, model, base_dir):
    ''' Generate a 'refutes' claim with an explanation. '''
    base64_image = encode_image(image_path, base_dir)
    prompt = create_zero_shot_refutes_prompt(base64_image, supports_claim) # change prompt version here
    response = model(model_name='gpt-4o-mini', query=prompt, image_base64=base64_image) # change model here
    response_json = parse_json_response(response)

    # If failed, add empty entries to filter out from final dataset
    if not response_json:
        print("Failed to parse response for refutes claim.")
        return "", "" 
    
    claim = response_json['refutes claim']
    explanation = response_json['explanation']

    return claim, explanation

def generate_nei_claim(image_path, supports_claim, model, base_dir):
    ''' Generate a 'not enough information' claim with an explanation. '''
    base64_image = encode_image(image_path, base_dir)
    prompt = create_zero_shot_nei_prompt(supports_claim) # change prompt version here
    response = model(model_name='gpt-4o-mini', query=prompt, image_base64=base64_image) # change model here
    response_json = parse_json_response(response)

    # If failed, add empty entries to filter out from final dataset
    if not response_json:
        print("Failed to parse response for not enough information claim.")
        return "", "" 
    
    claim = response_json['not enough information claim']
    explanation = response_json['explanation']

    return claim, explanation

def generate_claims_from_file(input_file, model, base_dir, claim_index):
    ''' Process an input file to generate one claim for each Q&A pair entry.
        Uses a persistent claim_index that is updated across files.
    '''
    with open(input_file, 'r') as file:
        entries = json.load(file)

    results = []
    claim_types = ['Supports', 'Refutes', 'Not enough information']
    
    for entry in entries:
        # Check if necessary keys exist
        question = entry.get("question")
        answer = entry.get("answer")
        image = entry.get("image")

        # Check for missing data 
        if not question or not answer or not image:
            print(f"Skipping entry due to missing data: {entry}")
            continue

        claim_type = claim_types[claim_index % 3]

        # Generate 'supports' claim
        if claim_type == 'Supports':
            supports_claim, explanation = generate_supports_claim(image, question, answer, model, base_dir)
            results.append({
                "image": image,
                "claim": supports_claim,
                "label": "Supports",
                "explanation": explanation
            })
            claim_index += 1
            continue

        # Generate 'refutes' claim using 'supports' claim from simplified function
        if claim_type == 'Refutes':
            simple_supports_claim = generate_supports_claim_simple(question, answer, model)
            refutes_claim, explanation = generate_refutes_claim(image, simple_supports_claim, model, base_dir)
            results.append({
                "image": image,
                "claim": refutes_claim,
                "label": "Refutes",
                "explanation": explanation
            })
            claim_index += 1
            continue

        # Generate 'not enough information' claim using 'supports' claim from simplified function
        if claim_type == 'Not enough information':
            print("Reached Not Enough Information Claim Generation")
            simple_supports_claim = generate_supports_claim_simple(question, answer, model)
            nei_claim, explanation = generate_nei_claim(image, simple_supports_claim, model, base_dir)
            results.append({
                "image": image,
                "claim": nei_claim,
                "label": "Not enough information",
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
    output_file_name = os.path.basename(input_file).replace('preprocessed', 'converted')
    output_path = os.path.join(output_folder, output_file_name)

    with open(output_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)

    print(f"Conversion completed for {os.path.basename(input_file)}. Results saved to {output_path}.")

    # Remove old 'preprocessed' file
    os.remove(input_file)
    print(f"Removed old preprocessed file: {input_file}")

def copy_folder_structure_and_files(src, dst):
    ''' Copy entire folder structure and contents of source folder to destination folder. '''
    if os.path.exists(dst):
        shutil.rmtree(dst)  # Remove destination folder if it exists

    shutil.copytree(src, dst)
    print(f"Copied {src} to {dst}")

def main(src, dst):
    ''' Main function to process all JSON files in specified directory. '''
    model = QueryModel()
    # Initialize a global counter that persists across multiple files.
    global_claim_index = 0

    # Copy entire source directory to destination directory
    copy_folder_structure_and_files(src, dst)

    for root, _, files in os.walk(dst):
        for filename in files:
            if filename.startswith('preprocessed_') and filename.endswith('.json'):
                input_file = os.path.join(root, filename)
                # Pass the global counter into each file's processing,
                # and update it with the returned value.
                global_claim_index = generate_claims_from_file(input_file, model, dst, global_claim_index)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python data_prompting.py <from_path> <to_path>")
        sys.exit(1)
    from_path = sys.argv[1]
    to_path = sys.argv[2]
    main(from_path, to_path)
    print("Prompted files saved successfully.")
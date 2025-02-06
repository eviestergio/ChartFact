from PIL import Image
import requests
from transformers import AutoProcessor, PaliGemmaForConditionalGeneration
import torch

# Load Model
model = PaliGemmaForConditionalGeneration.from_pretrained("ahmed-masry/chartgemma", torch_dtype=torch.float16)
processor = AutoProcessor.from_pretrained("ahmed-masry/chartgemma")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

chart = "../../5_final_dataset_12/train/png/plotQA_37698-train.png" 
claim = "There are 3 bars on the 2nd tick from the top."

input_text_variations = [
    # Prompt (1)
    f"""
        * Given the chart, what is the correct label ('supports', 'refutes', or 'not enough information') for the claim: {claim}? Why?
    
    Output the result as a JSON object with the following keys: "explanation" and "label". The format should strictly follow this structure: 
        {{
            "label": "your label for the claim", 
            "explanation": "your explanation for the label selected" 
        }}

    Examples: 
    
    1. Input: 
        {{ 
            “claim”: “The merchandise exports in 2010 were the highest among the years shown in the chart.”
        }} 
       Output: 
       {{ 
            "label": "refutes", 
            "explanation": "This claim refutes the chart as it inaccurately states that merchandise exports peaked in 2010. However, according to the chart, merchandise exports were highest in 2008 with a value of 1.22, and in 2010, the exports decreased to 1.05. Therefore, the claim contradicts the actual data presented in the chart." 
        }} 
    2. Input: 
        {{ 
            “claim": "The income share held by the highest 10% of the population was greater than the average income share held by the highest 10% of the population in 1 year." 
        }} 
       Output: 
       {{ 
            "label": "supports", 
            "explanation": "The chart shows data over several years where the income shares of the highest 10% are listed. Comparing these figures reveals that in one specific year, the income share of the top 10% exceeded the average income share held by the top 10% across all years.." 
        }} 
    3. Input: 
        {{ 
            “claim”: “President Donald Trump's approach to international relations contributes to their perception as Dangerous.” 
        }} 
       Output: 
       {{ 
            “label”: “not enough information”, 
            “explanation”: “This claim speculates on information not provided in the table, as there is no data regarding international relations, making the connection to the perception of being 'Dangerous' unverifiable.” 
       }}
    
    """,
    # Prompt (2)
    f"""
    Task: Given the chart, determine the correct label ('supports', 'refutes', or 'not enough information') for the following claim. 
    Provide an explanation for your classification using specific references from the chart to support your reasoning.
    
    Output the result as a JSON object with the following keys: "explanation" and "label". The format should strictly follow this structure: 
        {{
            "label": "your label for the claim", 
            "explanation": "your explanation for the label selected" 
        }}

    Examples: 
    
    1. Input: 
        {{ 
            “claim”: “The merchandise exports in 2010 were the highest among the years shown in the chart.”
        }} 
       Output: 
        {{ 
            "label": "refutes", 
            "explanation": "This claim refutes the chart as it inaccurately states that merchandise exports peaked in 2010. However, according to the chart, merchandise exports were highest in 2008 with a value of 1.22, and in 2010, the exports decreased to 1.05. Therefore, the claim contradicts the actual data presented in the chart." 
        }} 
    2. Input: 
        {{ 
            “claim": "The income share held by the highest 10% of the population was greater than the average income share held by the highest 10% of the population in 1 year." 
        }} 
       Output: 
       {{ 
            "label": "supports", 
            "explanation": "The chart shows data over several years where the income shares of the highest 10% are listed. Comparing these figures reveals that in one specific year, the income share of the top 10% exceeded the average income share held by the top 10% across all years.." 
        }} 
    3. Input: 
        {{ 
            “claim”: “President Donald Trump's approach to international relations contributes to their perception as Dangerous.” 
        }} 
       Output: 
       {{ 
            “label”: “not enough information”, 
            “explanation”: “This claim speculates on information not provided in the table, as there is no data regarding international relations, making the connection to the perception of being 'Dangerous' unverifiable.” 
        }}

    Based on the given chart, assess the following claim:
        Input: {claim}
        Output:
    """,
    # Prompt (3)
    f"""
    Given the chart, analyse whether the following claim: '{claim}' is supported, refuted, or if there is insufficient information to make a judgment. 
    First, provide an explanation using specific references from the chart to support your reasoning. After completing your explanation, classify the claim as’ supports', 'refutes', or 'not enough information'.

    Output the result as a JSON object with the following keys: "explanation" and "label". The format should strictly follow this structure: 
        {{
            "label": "your label for the claim", 
            "explanation": "your explanation for the label selected" 
        }}

    Examples: 
    
    1. Input: 
        {{ 
            “claim”: “The merchandise exports in 2010 were the highest among the years shown in the chart.”
        }} 
       Output: 
       {{ 
            "label": "refutes", 
            "explanation": "This claim refutes the chart as it inaccurately states that merchandise exports peaked in 2010. However, according to the chart, merchandise exports were highest in 2008 with a value of 1.22, and in 2010, the exports decreased to 1.05. Therefore, the claim contradicts the actual data presented in the chart." 
        }} 
    2. Input: 
        {{ 
            “claim": "The income share held by the highest 10% of the population was greater than the average income share held by the highest 10% of the population in 1 year." 
        }} 
       Output: 
       {{ 
            "label": "supports", 
            "explanation": "The chart shows data over several years where the income shares of the highest 10% are listed. Comparing these figures reveals that in one specific year, the income share of the top 10% exceeded the average income share held by the top 10% across all years.." 
        }} 
    3. Input: 
        {{ 
            “claim”: “President Donald Trump's approach to international relations contributes to their perception as Dangerous.” 
        }} 
       Output: 
       {{ 
            “label”: “not enough information”, 
            “explanation”: “This claim speculates on information not provided in the table, as there is no data regarding international relations, making the connection to the perception of being 'Dangerous' unverifiable.” 
        }}

    """
]

def run_experiment(input_text):
    # Process Inputs
    image = Image.open(chart).convert('RGB')
    inputs = processor(text=input_text, images=image, return_tensors="pt")
    prompt_length = inputs['input_ids'].shape[1]
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Generate
    generate_ids = model.generate(**inputs, num_beams=4, max_new_tokens=512)
    output_text = processor.batch_decode(generate_ids[:, prompt_length:], skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

    print(f"Input: {input_text}\nOutput: {output_text}\n") 
    
    return output_text

if __name__ == "__main__":
    for input_text in input_text_variations:
        run_experiment(input_text)

    print("Experiments completed successfully")
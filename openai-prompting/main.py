from model import QueryModel
import json


def main():
    model = QueryModel(query_type='chat')
    
    with open('qa_pairs.json', 'r') as file:
            entries = json.load(file)

    results = []
    
    for entry in entries:

         # 2. Few-shot
        prompt = f"""
            You will be provided with a data entry in JSON format deliminated by 3 single quotes. 

            Each data entry contains the following keys:
            'image', 'question', 'answer'

            Using the 4 input-output examples deliminated by angle brackets, your task is to convert 
            each 'question' and 'answer' pair to a claim that supports the information.

            Examples: < 
            1.Input: {{
                "image": "chartQA_multi_col_803.png",
                "question": "How many stores did Saint Laurent operate in Western Europe in 2020?",
                "answer": "47"
            }}
            Output: {{
                "image": "chartQA_multi_col_803.png",
                "claim": "Saint Laurent operated 47 stores in Western Europe in 2020.",
                "label": "Supports"
            }},
            2.Input: {{
                "image": "plotQA_11.png",
                "question": "What is the title of the graph ?",
                "answer": "Net disbursements of loans from International Monetary Fund"
            }} 
                Output: {{
                "image": "plotQA_11.png",
                "claim": "The title of the graph is Net disbursements of loans from International Monetary Fund.",
                "label": "Supports"
            }},
            3.Input: {{
                "image": "figureQA_400.png",
                "question": "Is Turquoise the roughest?",
                "answer": "No"
            }} 
                Output: {{
                "image": "figureQA_400.png",
                "claim": "Turquoise is not the roughest.",
                "label": "Supports"
            }},
            4.Input: {{
                "image": "figureQA_514.png",
                "question": "Is Periwinkle greater than Green Yellow?",
                "answer": "Yes"
            }} 
                Output: {{
                "image": "figureQA_514.png",
                "claim": "Periwinkle is greater than Green Yellow.",
                "label": "Supports"
            }},
            >

            Output only the text for the claim derived from converting the question and answer pair in double quotes.

            Data entry: '''{entry}'''
            """
        
        response = model(model_name='gpt-4', query=prompt)
        
        # Extract relevant information from the response
        result_entry = {
            "image": entry.get("imgname", ""),
            "claim": response.lstrip('Claim: '),
            "label": "Supports"
        }

        results.append(result_entry)

    # Save the results to 'converted.json'
    with open('converted.json', 'w') as output_file:
        json.dump(results, output_file, indent=4)

    print("Conversion completed. Results saved to 'converted.json'.")

if __name__ == '__main__':
    main()
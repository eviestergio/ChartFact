from openai import OpenAI
import ast
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QueryModel:
    """
    The class the handles model queries and responses
    """

    def __init__(self, query_type=None, params_dict=None):
        """
        The constructor
        Args:
            query_type (): The type of response expected ('completion',
            'chat'). If you want to query GPT3.5 and up models use 'chat'
            params_dict (): The parameters of the model in dict format
        """
        self.type = query_type if query_type is not None else 'completion'
        self.params = params_dict if params_dict is not None else {
            'temperature': 0,
            'max_tokens': 50,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }

    def __call__(self, model_name, query, *args, **kwargs):
        """
        A function that returns the response of an OpenAI model to a query
        :param model_name: The name of the model. It should be noted that
        GPT3.5 and up only work on 'chat' query_type, whereas
        text-davinci-003 and below only work in completion mode
        :type model_name: String
        :param query: The query
        :type query: String
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return: The response of the model
        :rtype: String
        """
        if self.type == 'completion':
            response = client.completions.create(model=model_name,
            prompt=query,
            **self.params)
            response = response.choices[0].text
            response = response.splitlines()[0]
            if len(response) > 0:
                if response[0] == " ":
                    response = response[1:]
            print("Answer is: " + response)
            try:
                response = ast.literal_eval(response)
            except:
                response = []
            return response
        else:
            response = client.chat.completions.create(model=model_name,
            messages=[{"role": "user", "content": query}])
            response = response.choices[0].message.content
            response = response.splitlines()[0]
            if len(response) > 0:
                if response[0] == " ":
                    response = response[1:]
            print("Answer is: " + response)
            try:
                response = ast.literal_eval(response)
            except:
                response = []
            return response


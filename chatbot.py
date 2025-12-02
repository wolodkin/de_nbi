import requests

class Chatbot():
    def __init__(self, api_path: str):
        self.api_key = self.__load_api_key(api_path)
    
    def get_response(self, message: str, filter_response: bool = True):
        prompt = self.__create_openrouter_prompt(message)
        print("Sending prompt to OpenRouter API: ", prompt)

        response = self.__call_openrouter_api(prompt)
        return self.__filter_response(response, filter_response)

    #########################################################
    # Private methods
    #########################################################

    def __filter_response(self, response: dict, message_only: bool = True):
        try:
            return response['choices'][0]['message']['content'] if message_only else response
        except Exception as e:
            print(f"Error filtering response: {e}")
            return response

    def __create_openrouter_prompt(self, message: str):
        return f"You are a helpful assistant. Answer the following question: {message}"

    def __load_api_key(self, api_path: str):
        with open(api_path, "r") as file:
            return file.readline().strip()

    def __call_openrouter_api(self, prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Here is a inline definition. In this case we dont need to define the payload in a separate config or any code segment.
        payload = {
            "model": "x-ai/grok-4.1-fast:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 30000,
            "stream": False
        }
        
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()  # Raises an exception for bad status code
        result = response.json()
        return result
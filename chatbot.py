from mcp_client import MCPClient
import requests

class Chatbot():
    def __init__(self, api_path: str):
        self.mcp_client = MCPClient()
        
        self.api_key = self.__load_api_key(api_path)
        self.messages = []
        self.messages.append({
            "role": "system",
            "content": "You are a helpful assistant."
        })

        self.tools = [self.mcp_client.test_mcp_ability_schema()]

        
    def get_response(self, message: str, filter_response: bool = True):
        prompt = self.__create_openrouter_prompt(message)
        # print("Sending prompt to OpenRouter API: ", prompt)

        response = self.__call_openrouter_api(prompt)
        self.__update_messages_history(response)

        self.check_for_tool_calls(response)
        return self.__filter_response(response, filter_response)

    #########################################################
    # Private methods
    #########################################################

    def check_for_tool_calls(self, response: dict):
        """Check for tool calls in the response from the OpenRouter API."""
        tool_calls = response['choices'][0]['message'].get('tool_calls') or []
        if tool_calls:
            for tool_call in tool_calls:
                if tool_call['function']['name'] == 'test_mcp_ability':
                    tool_response = self.mcp_client.test_mcp_ability()
                    self.messages.append({
                        "role": "tool",
                        "content": tool_call['function']['name'] + ": " + tool_response
                    })

                else:
                    self.messages.append({
                        "role": "tool",
                        "content": f"Tool call {tool_call['function']['name']} not found."
                    })

    def __update_messages_history(self, response: dict):
        """Update the messages history with the response from the OpenRouter API."""
        self.messages.append(response['choices'][0]['message'])

    def __filter_response(self, response: dict, message_only: bool = True):
        """Extract message content from an OpenRouter API response, or return the full response."""
        try:
            return response['choices'][0]['message']['content'] if message_only else response
        except Exception as e:
            print(f"Error filtering response: {e}")
            return response

    def __create_openrouter_prompt(self, message: str):
        """
        Create a prompt for the OpenRouter API.
        Here we currently just return the message as is.
        """
        return f"{message}"

    def __load_api_key(self, api_path: str):
        with open(api_path, "r") as file:
            return file.readline().strip()

    def __call_openrouter_api(self, prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        message =             {
                "role": "user",
                "content": prompt
            }

        self.messages.append(message)
        
        payload = {
            "model": "arcee-ai/trinity-large-preview:free",
            "messages": self.messages,
            "tools": self.tools,
            "tool_choice": "auto",
            "temperature": 0.3,
            "max_tokens": 4096,
            "stream": False
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        if not response.ok:
            print(f"OpenRouter API Error {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()
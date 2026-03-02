from mcp_client import MCPClient
import requests

class Chatbot():
    def __init__(self, api_path: str):
        self.mcp_client = MCPClient()
        
        self.api_key = self.__load_api_key(api_path)
        self.messages = []
        self.messages.append({
            "role": "system",
            "content": """
            You are a data curator from Senckenberg Nature Research. 
            You are responsible for curating collection data from the web. In your workflow you can use several tools to help you with your task. 
            These tools are provided to you by the MCP client. Use them to get more data and combine data from different sources for your work, if necessary. 
            You are also a helpful assistant and you can answer questions about the data you are curating. 
            Answer in the language of the user, but always use English for tools and MCP Server messages. 
            Important: If a user asks you not in English and you have to use a tool or MCP Server, always translate the user's message to English first. Use the translated message for the tool call or MCP Server call. 
            Important: Don't answer with hypotetical information. If you don't know the answer, say so.
            Example: A user asks you in German: 'Welche Proben beinhalten Holz?'. Then you should use the tools and MCP Servers to get the information about the samples that contain the translated word 'wood'."""
        })

        self.tools = [self.mcp_client.test_mcp_ability_schema()]

        
    def get_response(self, message: str | None = None, filter_response: bool = True):
        prompt = self.__create_openrouter_prompt(message)
        # print("Sending prompt to OpenRouter API: ", prompt)

        response = self.__call_openrouter_api(prompt)
        self.__update_messages_history(response)

        tool_call_flag = self.__check_for_tool_calls(response)
        return {"tool_call_flag":tool_call_flag, "text_result": self.__filter_response(response, filter_response)}

    #########################################################
    # Private methods
    #########################################################

    def __check_for_tool_calls(self, response: dict):
        """Check for tool calls in the response from the OpenRouter API."""
        tool_calls = response['choices'][0]['message'].get('tool_calls') or []
        if tool_calls:
            for tool_call in tool_calls:
                if tool_call['function']['name'] == 'test_mcp_ability':
                    tool_response = self.mcp_client.test_mcp_ability()
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", ""),
                        "content": tool_call['function']['name'] + ": " + tool_response
                    })
                    return True
                else:
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", ""),
                        "content": f"Tool call {tool_call['function']['name']} not found."
                    })
                    return False

    def __update_messages_history(self, response: dict):
        """Update the messages history with the response from the OpenRouter API.
        Normalize tool_calls so each function has 'arguments' (required when re-sending to API).
        """
        messages = response['choices'][0]['message'].copy()
        tool_calls = messages.get('tool_calls')
        if tool_calls:
            normalized = []
            for single_tool_call in tool_calls:
                single_tool_call = single_tool_call.copy()
                function = single_tool_call.get('function') or {}
                if isinstance(function, dict) and 'arguments' not in function:
                    single_tool_call['function'] = {**function, 'arguments': function.get('arguments', '{}')}
                normalized.append(single_tool_call)
            messages['tool_calls'] = normalized
        self.messages.append(messages)

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
        return f"{message}" if message is not None else None

    def __load_api_key(self, api_path: str):
        with open(api_path, "r") as file:
            return file.readline().strip()

    def __call_openrouter_api(self, prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if prompt is not None:
            self.messages.append({
                    "role": "user",
                    "content": prompt
                })
        
        payload = {
            "model": "arcee-ai/trinity-large-preview:free",
            "messages": self.messages,
            "tools": self.tools,
            "tool_choice": "auto",
            "temperature": 0.3,
            "max_tokens": 30000,
            "stream": False
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        if not response.ok:
            print(f"OpenRouter API Error {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()
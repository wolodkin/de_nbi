from mcp_client import MCPClient
import json
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
You are responsible for curating collection data from our collections only. Our collections you can access with the tools provided to you. You don't know anything about other collections or institutions.
These tools are provided to you by the MCP client. Use them to get more data and combine data from different sources for your work.
You can answer questions only about the collections and data you are curating, no other institutions or collections are part of your scope.
You are also a helpful assistant and you can answer questions about the data you are curating. You always have maximum 3 tries to answer the question. If you don't find the answer, say so.
Answer in the language of the user, but always use English for tools and MCP Server messages. 
Important: If a user asks you not in English and you have to use a tool or MCP Server, always translate the user's message to English first. Use the translated message for the tool call or MCP Server call. 
Important: Don't answer with hypothetical information. If you don't know the answer, say so.
Important: Always use only collection names and data you can access with the tools provided to you.
Example: A user asks you in German: 'Welche Proben beinhalten Holz?'. Then you should use the tools and MCP Servers to get the information about the samples that contain the translated word 'wood'.
Our collections are: """ + json.dumps(self.mcp_client.get_collection_list())
        })

        self.tools = [self.mcp_client.test_mcp_ability_schema(),
                      self.mcp_client.get_collection_list_schema(),
                      self.mcp_client.get_collection_data_as_list_schema(),
                      self.mcp_client.get_collection_data_as_dict_schema()]

        # Dispatcher: tool name -> MCP client method (called with **tool_args)
        self.__tool_handlers = {
            "test_mcp_ability": self.mcp_client.test_mcp_ability,
            "get_collection_list": self.mcp_client.get_collection_list,
            "get_collection_data_as_list": self.mcp_client.get_collection_data_as_list,
            "get_collection_data_as_dict": self.mcp_client.get_collection_data_as_dict,
        }

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

    def __parse_tool_args(self, tool_call: dict) -> dict:
        """Parse JSON arguments from tool_call['function']['arguments']."""
        raw = tool_call.get('function') or {}
        args_str = raw.get('arguments') or '{}'
        try:
            return json.loads(args_str)
        except json.JSONDecodeError:
            return {}

    def __check_for_tool_calls(self, response: dict):
        """Check for tool calls in the response from the OpenRouter API."""
        tool_calls = response['choices'][0]['message'].get('tool_calls') or []
        if not tool_calls:
            return

        for tool_call in tool_calls:
            name = tool_call['function']['name']
            handler = self.__tool_handlers.get(name)

            if handler is None:
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", ""),
                    "content": f"Tool call {name} not found."
                })
                return False

            tool_args = self.__parse_tool_args(tool_call)
            try:
                tool_response = handler(**tool_args)
            except Exception as e:
                tool_response = f"Error: {e}"
                print("Error in tool call:", name)

            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", ""),
                "content": f"{tool_response}"
            })
        return True

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
            "max_tokens": 4000,
            "stream": False,
            "transforms": ["middle-out"]
        }

        # print("\n\nSending payload to OpenRouter API: ", payload, "\n\n")

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        if not response.ok:
            print(f"OpenRouter API Error {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()
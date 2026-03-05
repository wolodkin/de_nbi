from chatbot import Chatbot

class MCP_Handler():
    def __init__(self, api_path: str):
        self.chatbot = Chatbot(api_path)

    def query_model_cli_loop(self):
        input_needed_flag = False

        while True:
            if input_needed_flag: print("\n--------------------------------")
            message = input("Enter a message (type 'exit' to quit): ") if input_needed_flag else None

            if message == "exit": break

            response = self.chatbot.get_response(message, filter_response=True)
            # print(response)
            print("")

            text = response.get("text_result")
            has_text = text is not None and text != ""

            if response["tool_call_flag"] is not None:
                if has_text:
                    print(text)
                else:
                    print("tool call without a message")
                input_needed_flag = False

            else:
                if has_text:
                    print(text)
                input_needed_flag = True



    #########################################################
    # Test methods
    #########################################################
    def test_chatbot_query(self, message: str = "What is your opinion about a travel to the middle of the earth?", filter_response: bool = True):
        print(self.chatbot.get_response(message))


if __name__ == "__main__":
    mcp_handler = MCP_Handler("api/api_openrouter.txt")
    # mcp_handler.test_chatbot_query()
    mcp_handler.query_model_cli_loop()
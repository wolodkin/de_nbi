class MCPClient():
    def __init__(self):
        pass

    def test_mcp_ability(self):
        return "MCP test client is working."

    def test_mcp_ability_schema(self):
        return {
                "type": "function",
                "function": {
                                    "name": "test_mcp_ability",
                                    "description": "Test the MCP ability. Return a string that you have to return to the user.",
                                    "parameters": {
                                        "properties": {},
                                        "required": []
                                    }
                                }
            }
        
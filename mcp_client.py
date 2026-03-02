from utils import load_csv_file_as_list, load_csv_file_as_dict

class MCPClient():
    def __init__(self):
        self.path_prefix = "/home/alex/Schreibtisch/Projects/BITS/confidential/"

    #########################################################
    # Test methods
    def test_mcp_ability(self):
        return "MCP test client is working."

    def test_mcp_ability_schema(self):
        return {
                "type": "function",
                "function": {
                    "name": "test_mcp_ability",
                    "description": "Test the MCP ability. Return a string that you have to return to the user.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
    #########################################################

    #########################################################
    # Collection methods
    #########################################################

    def get_collection_list(self):
        return {
            "02-Herbarium Senckenbergianum (FR) - Algae & Protista":{
                "filename":"02_annotated.csv",
                "description":"Algae & Protista collection. This collection contains data on algae and protists. Protists are single-celled or multicellular eukaryotes that do not belong to the animal, plant, or fungal kingdoms. They form a very diverse group of organisms that occur in various habitats. Protists include, for example, amoebas, diatoms, dinoflagellates, euglenoids, slime molds, and others. They play important roles in ecosystems, both as primary producers and as food for other organisms."
                }
            
        }

    def get_collection_list_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "get_collection_list",
                "description": "Get the list of available collections",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    #########################################################
    
    def get_collection_data_as_list(self, filename: str):
        return load_csv_file_as_list(self.path_prefix + filename)

    def get_collection_data_as_list_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "get_collection_data_as_list",
                "description": "Get the data for a collection as a list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The filename of the collection for other tools to use"
                        }
                    },
                    "required": ["filename"]
                }
            }
        }
    #########################################################
    
    def get_collection_data_as_dict(self, filename: str):
        return load_csv_file_as_dict(self.path_prefix + filename)

    def get_collection_data_as_dict_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "get_collection_data_as_dict",
                "description": "Get the data for a collection as a dictionary",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The filename of the collection for other tools to use"
                        }
                    },
                    "required": ["filename"]
                }
            }
        }
    #########################################################
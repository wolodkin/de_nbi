from utils import load_csv_file_as_list, load_csv_file_as_dict
"""
Here we use mcp-csv-database to access the data. Source: https://pypi.org/project/mcp-csv-database

How to install the package:
pip install mcp-csv-database

If you can't install it using Kubuntu, you can try to install it using the following commands:

sudo apt install python3.12-venv
python3 -m venv .venv # Here you can choise the path for the venv. I recommend to use the project path.
source .venv/bin/activate # Activate the venv   

pip install mcp-csv-database # Install the package
"""


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
    # Own collections methods
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

    #########################################################
    # MCP Server methods
    #########################################################

    def get_mcp_server_list(self):
        return {
            "csv-database": {
                "description": "CSV Database MCP Server"
            }
        }
    #########################################################
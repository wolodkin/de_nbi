from utils import load_csv_file_as_list, load_csv_file_as_dict

import asyncio
import threading
from concurrent.futures import TimeoutError as FuturesTimeoutError

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
from mcp.types import TextContent

"""
Here we use mcp-csv-database to access the data. Source: https://pypi.org/project/mcp-csv-database

How to install the package:
Step 1
pip install mcp-csv-database

If you can't install it using Kubuntu, you can try to install it using the following commands:

sudo apt install python3.12-venv
python3 -m venv .venv # Here you can choise the path for the venv. I recommend to use the project path.
source .venv/bin/activate # Activate the venv   

pip install mcp-csv-database # Install the package

Step 2
Instal python module mcp: pip install mcp

"""


class MCPClient():
    def __init__(self):
        print("Initializing MCP Clients...")

        self.path_prefix = "/home/alex/Schreibtisch/Projects/BITS/confidential/annotated"        
        # Single MCP server preparation

        # mcp_csv_database
        self.mcp_csv_database_allowed_tools = ["list_loaded_tables", "execute_sql_query", "get_database_schema", "get_table_info", "get_query_plan", "get_data_summary", "get_column_stats", "analyze_missing_data", "find_duplicates" ] # to be initiated by start_mcp_csv_database_server
        self.mcp_csv_database_session = None  # set in _run_mcp_session_async
        self.mcp_csv_database_schema = None  # list of OpenAI-style tool schemas; set in _run_mcp_session_async

        # MCP session runs in background thread; these are set in start_mcp_csv_database_server
        self._mcp_loop = None
        self._mcp_ready = threading.Event()
        self._mcp_thread = None


    #########################################################
    # MCP Tool → OpenAI/OpenRouter schema (for AI model tool use)
    #########################################################

    @staticmethod
    def mcp_tool_to_openai_schema(tool) -> dict:
        """
        Convert one MCP Tool to the OpenAI/OpenRouter tool schema format
        (same structure as test_mcp_ability_schema / get_collection_list_schema).
        """
        params = dict(tool.inputSchema) if tool.inputSchema else {"type": "object", "properties": {}}
        if "required" not in params:
            params["required"] = []
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or f"Tool: {tool.name}",
                "parameters": params,
            },
        }

    def get_mcp_csv_database_tool_schemas(self):
        """Return list of OpenAI-style tool schemas for allowed MCP CSV database tools (after server start)."""
        return self.mcp_csv_database_schema or []


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
    # Own collections methods (old CSV based approach)
    #########################################################

    def get_collection_list(self):
        return {
            "02-Herbarium Senckenbergianum (FR) - Algae & Protista":{
                "filename":"02_annotated.csv",
                "description":"Specimen records of algae and protists from the Herbarium Senckenbergianum (FR). Each row represents one specimen. Identifiers: AQUiLA-ID, Barcode, Katalognummer, Katalognr. (alphanum.), Katalognr. (num.). Taxonomy fields: Taxon, Familie, Synonyme, Taxonomie, Typus. Collection event fields: Sammler, Sammeldatum, Sammelnummer, Bestimmer, Bestimmungsdatum. Locality fields: Fundortbeschreibung, Geographische Breite, Geographische Länge, Latitude, Longitude, Administrative Einheit, Adm. Einheit, Kontinent, Koordinatentyp. Ecological fields: Habitat, Substrat, Endwirt, Zwischenwirt, Meer, Marine Einheit."
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

    def start_mcp_csv_database_server(self):
        """Start MCP CSV database server in a background thread. Blocks until session is ready."""
        print("Starting MCP CSV Database Server...")
        self._mcp_ready.clear()

        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._mcp_loop = loop
            try:
                loop.run_until_complete(self._run_mcp_session_async())
            finally:
                loop.close()

        self._mcp_thread = threading.Thread(target=run_loop, daemon=True)
        self._mcp_thread.start()

        if not self._mcp_ready.wait(timeout=30):
            raise RuntimeError("MCP CSV database server did not become ready within 30 seconds")

        # for tool_name in self.mcp_csv_database_allowed_tools:
        #     if any(s.get("function", {}).get("name") == tool_name for s in (self.mcp_csv_database_schema or [])):
        #         print(f"  {tool_name}: available")

    async def _run_mcp_session_async(self):
        """Run MCP session in background thread. Keeps session alive until shutdown."""
        server_params = StdioServerParameters(
            command="mcp-csv-database",
            args=["--csv-folder", self.path_prefix],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as self.mcp_csv_database_session:
                await self.mcp_csv_database_session.initialize()
                tools = await self.mcp_csv_database_session.list_tools()
                self.mcp_csv_database_schema = [
                    self.mcp_tool_to_openai_schema(t)
                    for t in tools.tools
                    if t.name in self.mcp_csv_database_allowed_tools
                ]
                self._mcp_ready.set()
                await asyncio.Event().wait()

    @staticmethod
    def _call_tool_result_to_str(result) -> str:
        """Convert MCP CallToolResult to string for chatbot message."""
        parts = []
        for block in (result.content or []):
            if isinstance(block, TextContent):
                parts.append(block.text)
        text = "".join(parts).strip() or "(no output)"
        if result.isError:
            text = f"Error: {text}"
        return text

    def call_mcp_csv_database_tool(self, name: str, arguments: dict | None = None) -> str:
        """Call an MCP CSV database tool by name. Synchronous, blocks until result."""
        try:
            if name not in self.mcp_csv_database_allowed_tools:
                return f"Error: Tool {name} is not in allowed tools."
            if self.mcp_csv_database_session is None or self._mcp_loop is None:
                return "Error: MCP session not ready."
            arguments = arguments or {}
            future = asyncio.run_coroutine_threadsafe(
                self.mcp_csv_database_session.call_tool(name, arguments),
                self._mcp_loop,
            )
            result = future.result(timeout=60)
            return self._call_tool_result_to_str(result)
        except (TimeoutError, FuturesTimeoutError):
            return "Error: MCP tool call timed out."
        except Exception as e:
            return f"Error: {e}"

    def get_mcp_tool_handlers(self) -> dict:
        """Return handlers for all allowed MCP CSV database tools (name -> callable)."""
        return {
            name: (lambda n: lambda **a: self.call_mcp_csv_database_tool(n, a))(name)
            for name in self.mcp_csv_database_allowed_tools
        }

    #########################################################
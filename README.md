## DE NBI – BITS Collection Data Chatbot at Senckenberg

Interactive command line chatbot for curating and exploring collection data from Senckenberg Nature Research.  
The assistant uses OpenRouter for LLM access and an MCP-style client to read local CSV-based collection databases.

### Features

- **Domain-specific assistant**: Acts as a data curator for Senckenberg collections only.
- **Tool-augmented responses**: Uses an MCP client to query CSV collections via tools.
- **Multilingual user interaction**: Answers in the user’s language while keeping tool/server calls in English.
- **CLI interface**: Simple interactive loop for asking questions and receiving answers.

### Requirements

- **Python**: 3.10 or newer
- **Python packages**:
  - `requests`
  - `mcp` (MCP client library)
  - `mcp-csv-database` (CSV-based MCP server for querying collection data)

Install dependencies with:

```bash
pip install requests mcp mcp-csv-database
```

> **Note:** If installation fails on Linux, try using a virtual environment:  
> `python3 -m venv .venv && source .venv/bin/activate` (on Windows: `.venv\Scripts\activate`)

### OpenRouter API setup

To use this project, you need to provide an OpenRouter API key in a local file.

1. Create a folder named `api` in the project root.
2. Inside it, create a file named `api_openrouter.txt`.
3. Paste your OpenRouter API key into that file (single line, no extra spaces or quotes).

Project structure (simplified):

```text
de_nbi/
├── api/
│   └── api_openrouter.txt
├── chatbot.py
├── main.py
├── mcp_client.py
└── utils.py
```

### CSV data and MCP client

The `MCPClient` in `mcp_client.py` starts an **mcp-csv-database** server in the background. It loads all CSV files from the directory configured in `path_prefix` (see line 36 in `mcp_client.py`). Adjust this path to point to your own CSV folder.

**Available MCP tools** (among others):
- `list_loaded_tables` – list loaded tables
- `execute_sql_query` – run SQL queries on the CSV data
- `get_database_schema`, `get_table_info` – schema and column information
- `get_data_summary`, `get_column_stats`, `analyze_missing_data`, `find_duplicates` – analysis tools

Additionally, `get_collection_list()` returns the collection list with descriptions. The helpers in `utils.py` (`load_csv_file_as_list`, `load_csv_file_as_dict`) are available for custom extensions.

### Running the chatbot

Run the interactive CLI from the project root:

```bash
python main.py
```

The chatbot starts with an automatic introduction and checks available collections. You can then enter questions in your preferred language.  
Type `exit` to quit.

### Behavior and scope

- The chatbot only answers questions about the collections it can access via the MCP tools.
- It will try at most three times to answer a question; if it cannot find an answer, it explicitly says so.
- It avoids hypothetical information and only uses collection names and data available through its tools.


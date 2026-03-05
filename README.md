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
  - `mcp-csv-database` (for the CSV-based MCP functionality, see below)

You can install dependencies for example with:

```bash
pip install requests mcp-csv-database
```

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

The `MCPClient` class in `mcp_client.py` is responsible for accessing your collection data, which is stored in CSV files.  
By default, it expects CSVs in a directory configured via its `path_prefix` attribute. Adjust this path to point to your own CSV data.

- **Collections list**: `get_collection_list()` returns the available collections and the filenames used.
- **Data access helpers** (in `utils.py`):
  - `load_csv_file_as_list(...)`
  - `load_csv_file_as_dict(...)`

Make sure your CSV files are accessible at the location configured in `MCPClient.path_prefix`.

### Running the chatbot

Run the interactive CLI loop from the project root:

```bash
python main.py
```

You can then enter questions in your preferred language.  
Type `exit` to quit the program.

### Behavior and scope

- The chatbot only answers questions about the collections it can access via the MCP tools.
- It will try at most three times to answer a question; if it cannot find an answer, it explicitly says so.
- It avoids hypothetical information and only uses collection names and data available through its tools.


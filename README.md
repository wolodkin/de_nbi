# DE NBI

## Setup

To use this project, you need to create an `api` folder and place a file `api_openrouter.txt` containing your OpenRouter API key inside it.

### API Configuration

1. Create a folder named `api` in the project directory
2. Create a file `api_openrouter.txt` inside this folder
3. Add your OpenRouter API key to the file (one line, without any additional characters)

The structure should look like this:
```
de_nbi/
├── api/
│   └── api_openrouter.txt
├── chatbot.py
├── main.py
└── mcp_client.py
```

## Usage

Run `main.py` to start the interactive CLI loop:

```bash
python main.py
```


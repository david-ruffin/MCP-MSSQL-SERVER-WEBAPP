# Natural Language SQL Chat Interface

A chat-based interface that allows users to query an SQL database using natural language. The system translates questions into SQL and returns answers using AI for language understanding.

## Features

- **Natural Language Querying:** Ask questions about the database in plain English
- **Chat Interface:** Simple web UI for interaction
- **AI Query Engine:** Converts questions to SQL using Claude API
- **Documentation-Aware:** Uses Context7 for SQL syntax awareness
- **Fallback Mode:** Works even without an API key (provides raw SQL results)

## Project Structure

```
MCP-MSSQL-SERVER-WEBAPP/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api.py      # FastAPI endpoints
│   │   ├── answer.py   # NL-to-SQL conversion logic
│   │   └── config.py   # Configuration settings
│   └── run.py          # Server entry point
├── frontend/
│   └── index.html      # Chat UI
├── src/
│   └── mssql/          # SQL Server MCP implementation
├── .env.example        # Environment variables template
└── requirements.txt    # Python dependencies
```

## Setup Instructions

### 1. Environment Setup

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```
# Database settings
MSSQL_SERVER=your_server
MSSQL_DATABASE=your_database
MSSQL_USER=your_username
MSSQL_PASSWORD=your_password
MSSQL_DRIVER={ODBC Driver 17 for SQL Server}

# API settings
PORT=8000
HOST=0.0.0.0
DEBUG=True

# Optional: AI settings (if you have an API key)
ANTHROPIC_API_KEY=your_api_key
```

### 3. Running the Application

**Backend**:

```bash
cd backend
python run.py
```

The server will start at http://localhost:8000

**Frontend**:

```bash
cd frontend
python -m http.server 8080
```

Access the chat UI at http://localhost:8080

## Operating Modes

### With API Key
If you provide an Anthropic API key, the system will:
1. Convert natural language to SQL using Claude
2. Execute the SQL query
3. Format the results into a natural language answer using Claude

### Fallback Mode (No API Key)
Without an API key, the system will:
1. Execute a simplified SQL query
2. Return the raw results to the user

## Troubleshooting

- **CORS Issues**: Make sure your backend and frontend are allowed to communicate
- **Database Connection**: Verify ODBC driver is installed and credentials are correct
- **API Key**: If using AI features, ensure your Anthropic API key is valid

## Development

This project was developed using Cursor IDE with Claude AI and MCP tools.
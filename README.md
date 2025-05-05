# Natural Language MCP-MSSQL Client

A natural language interface for SQL databases using the Model Context Protocol (MCP). This client allows users to query Microsoft SQL Server databases using plain English questions through Claude AI.

## Features

- **Natural Language Querying**: Ask questions about your database in plain English
- **MCP Integration**: Connects to MCP-MSSQL server using FastMCP
- **Claude AI**: Uses Anthropic's Claude API to translate natural language to SQL
- **Interactive Mode**: Type questions directly and get database results
- **Demo Mode**: Run predefined questions to showcase functionality

## Components

1. **MCP-MSSQL Server**: Provides access to MS SQL Server databases through MCP
2. **Natural Language Client**: Converts plain English to SQL using Claude API
3. **FastMCP Framework**: Handles the communication between client and server

## Prerequisites

* Python 3.8+
* ODBC Driver for SQL Server installed on your system
* Anthropic API key
* Required Python packages (fastmcp, anthropic, python-dotenv, etc.)

## Project Structure

```
MCP-MSSQL-SERVER-WEBAPP/
├── src/
│   └── mssql/           # MSSQL MCP server implementation
│       ├── __init__.py
│       └── server.py    # Main MCP server
├── interactive_client.py   # Interactive natural language client
├── demo_nl_client.py       # Demo client with predefined questions
├── .env                    # Environment configuration (not in git)
├── .env.example            # Example environment configuration
└── requirements.txt        # Project dependencies
```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/david-ruffin/MCP-MSSQL-SERVER-WEBAPP.git
   cd MCP-MSSQL-SERVER-WEBAPP
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure the environment**:
   Copy `.env.example` to `.env` and fill in your database and API credentials:
   ```
   MSSQL_SERVER=your_server
   MSSQL_DATABASE=your_database
   MSSQL_USER=your_username
   MSSQL_PASSWORD=your_password
   MSSQL_DRIVER={ODBC Driver 17 for SQL Server}
   ANTHROPIC_API_KEY=your_api_key
   ```

## Running the Client

### Interactive Mode

Run the interactive client to ask your own questions:

```bash
source venv/bin/activate
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d= -f2)
python interactive_client.py
```

Type natural language questions at the prompt, and the client will convert them to SQL, execute them, and display the results.

### Demo Mode

Run the demo to see predefined questions:

```bash
source venv/bin/activate
export ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY .env | cut -d= -f2)
python demo_nl_client.py
```

The demo will automatically run several example questions, showing the natural language to SQL conversion and results.

## Example Questions

- "How many products are there?"
- "List all customers from California"
- "Show me the most expensive products"
- "What are the different product categories?"
- "How many orders were placed in 2004?"

## ODBC Driver Setup

This client requires the Microsoft ODBC Driver for SQL Server. Follow the official Microsoft guides to install:

- [Windows](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)
- [macOS/Linux](https://learn.microsoft.com/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

## License

MIT License
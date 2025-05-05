#!/usr/bin/env python3
"""
Interactive Natural Language SQL Client using FastMCP
"""

import asyncio
import sys
import os
import anthropic
from fastmcp import Client

# Path to the MCP-MSSQL server
SERVER_PATH = os.path.join(os.getcwd(), "src/mssql/server.py")

# Initialize the Anthropic client
claude_client = anthropic.Anthropic()

async def get_schema_info(mcp_client):
    """Get database schema information"""
    schema_info = {}
    
    # Get list of tables
    resources = await mcp_client.list_resources()
    tables = [str(resource.uri).split('/')[2] for resource in resources]
    
    # Get schema to know which schema tables are in
    schema_query = "SELECT SCHEMA_NAME(schema_id) as schema_name, name FROM sys.tables"
    result = await mcp_client.call_tool("execute_sql", {"query": schema_query})
    
    if result and hasattr(result[0], 'text'):
        lines = result[0].text.strip().split('\n')
        table_schemas = {}
        
        # Skip header row
        for i, line in enumerate(lines):
            if i == 0:  # Skip header
                continue
                
            parts = line.split(',')
            if len(parts) >= 2:
                schema_name = parts[0].strip()
                table_name = parts[1].strip()
                table_schemas[table_name] = schema_name
    
    return tables, table_schemas

async def nl_to_sql(query, tables, table_schemas):
    """Use Claude to convert natural language to SQL"""
    # Special case for listing tables
    if "list tables" in query.lower() or "show tables" in query.lower():
        return "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
        
    # Build context about the database schema
    schema_text = "Database Schema:\n"
    for table, schema in table_schemas.items():
        schema_text += f"Table: {schema}.{table}\n"
    
    # Create prompt for Claude
    prompt = f"""
{schema_text}

You are an expert at converting natural language questions into SQL queries.
Given the database schema above, convert the following question into a SQL query:
"{query}"

Return ONLY the SQL query, nothing else. Make sure it's valid SQL for SQL Server.
If you can't create a valid SQL query, just return "UNABLE_TO_CONVERT".
"""
    
    try:
        # Call Claude API
        message = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0,
            system="You convert natural language questions to SQL queries. Only return the SQL query, nothing else.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract SQL from response
        sql = message.content[0].text.strip()
        
        # Handle when Claude can't convert
        if "UNABLE_TO_CONVERT" in sql:
            return None
            
        # Clean up any markdown or extra text
        if sql.startswith("```sql"):
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif sql.startswith("```"):
            sql = sql.split("```")[1].split("```")[0].strip()
            
        return sql
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

async def main():
    """Main entry point"""
    print("Interactive Natural Language SQL Client")
    print("======================================")
    
    # Create client for the MCP-MSSQL server
    client = Client(SERVER_PATH)
    
    try:
        # Connect and get schema information
        print("Connecting to MCP-MSSQL server...")
        async with client:
            print("Connected!")
            tables, table_schemas = await get_schema_info(client)
            
            print("\nAvailable tables:")
            for table, schema in table_schemas.items():
                print(f"- {schema}.{table}")
            
            print("\nType your natural language questions and press Enter.")
            print("Type 'exit' to quit.")
            
            while True:
                query = input("\nYour question: ")
                if query.lower() == "exit":
                    break
                
                # Handle listing tables
                if "list tables" in query.lower() or "show tables" in query.lower():
                    print("\nAvailable tables:")
                    for table, schema in table_schemas.items():
                        print(f"- {schema}.{table}")
                    continue
                
                # Convert natural language to SQL
                print("Translating to SQL...")
                sql = await nl_to_sql(query, tables, table_schemas)
                
                if not sql:
                    print("Sorry, I couldn't convert that to SQL. Please try a different question.")
                    continue
                
                print(f"SQL: {sql}")
                
                # Ask for confirmation
                confirm = input("Execute this SQL query? (y/n): ")
                if confirm.lower() != "y":
                    print("Query execution cancelled.")
                    continue
                
                # Execute the SQL
                try:
                    print("Executing query...")
                    async with client:
                        result = await client.call_tool("execute_sql", {"query": sql})
                        
                        if result and hasattr(result[0], 'text'):
                            # Format results as a table
                            lines = result[0].text.strip().split('\n')
                            
                            if not lines:
                                print("No results returned")
                                continue
                                
                            print("\nResults:")
                            for i, line in enumerate(lines):
                                cells = line.split(',')
                                if i == 0:  # Header row
                                    print("  " + " | ".join(cells))
                                    print("  " + "-" * (sum(len(cell) for cell in cells) + 3 * len(cells)))
                                else:
                                    print("  " + " | ".join(cells))
                except Exception as e:
                    print(f"Error executing query: {e}")
    
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    # Check for API key
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable not found")
        sys.exit(1)
        
    # Run the client
    asyncio.run(main())
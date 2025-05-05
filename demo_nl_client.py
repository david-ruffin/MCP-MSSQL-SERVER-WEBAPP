#!/usr/bin/env python3
"""
Demo Natural Language SQL Client using FastMCP and Claude API
This version automatically runs some example queries to demonstrate functionality
"""

import asyncio
import os
import sys
import time
import anthropic
from fastmcp import Client

# Path to the MCP-MSSQL server
SERVER_PATH = os.path.join(os.getcwd(), "src/mssql/server.py")

# Initialize the Anthropic client
claude_client = anthropic.Anthropic()

# Demo questions to demonstrate the client
DEMO_QUESTIONS = [
    "List all tables in the database",
    "How many products are there?",
    "Show me the top 3 customers",
    "What are the product categories?",
    "List products that cost more than $1000"
]

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
                
        # Store tables with their schemas
        for table in tables:
            if table in table_schemas:
                schema = table_schemas[table]
                full_name = f"{schema}.{table}"
                
                # Get columns for each table
                col_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' AND TABLE_SCHEMA = '{schema}'"
                try:
                    col_result = await mcp_client.call_tool("execute_sql", {"query": col_query})
                    if col_result and hasattr(col_result[0], 'text'):
                        # Skip header row and parse column names
                        col_lines = col_result[0].text.strip().split('\n')[1:]
                        columns = [col.strip() for col in col_lines]
                        schema_info[full_name] = columns
                except Exception as e:
                    print(f"Error getting columns for {full_name}: {e}")
    
    return tables, table_schemas, schema_info

async def nl_to_sql(query, tables, table_schemas, schema_info):
    """Use Claude to convert natural language to SQL"""
    # Special case for listing tables
    if query.lower() in ["list all tables", "show all tables", "what tables are in the database"]:
        return "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
        
    # Build context about the database schema
    schema_text = "Database Schema:\n"
    for table, schema in table_schemas.items():
        full_name = f"{schema}.{table}"
        schema_text += f"Table: {full_name}\n"
        if full_name in schema_info:
            schema_text += f"  Columns: {', '.join(schema_info[full_name])}\n"
    
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
    print("Natural Language SQL Client Demo")
    print("===============================")
    
    # Create client for the MCP-MSSQL server
    client = Client(SERVER_PATH)
    
    try:
        # Connect and get schema information
        print("Connecting to MCP-MSSQL server...")
        async with client:
            print("Connected! Loading database schema...")
            tables, table_schemas, schema_info = await get_schema_info(client)
            
            print(f"Loaded schema for {len(tables)} tables")
            print("\nAvailable tables:")
            for table, schema in table_schemas.items():
                print(f"- {schema}.{table}")
            
            print("\nRunning demo questions:")
            
            # Process demo questions
            for i, question in enumerate(DEMO_QUESTIONS, 1):
                print(f"\n[Question {i}]: {question}")
                
                # Handle listing tables
                if "list all tables" in question.lower() or "show all tables" in question.lower():
                    print("\nAvailable tables:")
                    for table, schema in table_schemas.items():
                        print(f"- {schema}.{table}")
                    continue
                
                # Convert natural language to SQL
                print("Translating to SQL...")
                sql = await nl_to_sql(question, tables, table_schemas, schema_info)
                
                if not sql:
                    print("Sorry, I couldn't convert that to SQL.")
                    continue
                
                print(f"SQL: {sql}")
                
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
                    
                # Pause between questions for readability
                time.sleep(1)
            
            print("\nDemo completed!")
    
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    # Check for API key
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable not found")
        sys.exit(1)
        
    # Run the client
    asyncio.run(main())
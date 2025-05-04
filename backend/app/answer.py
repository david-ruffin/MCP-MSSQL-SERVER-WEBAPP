from typing import Dict, Any, Optional
import logging
import json
import os
import anthropic
import sys
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("answer")

# Load environment variables
load_dotenv()

# Initialize MCP client and check if we're running in MCP context
IN_MCP = "MCP_FUNCTION" in os.environ

# Try to import anthropic
try:
    from anthropic import Anthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if ANTHROPIC_API_KEY:
        anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    else:
        anthropic_client = None
        logger.warning("No ANTHROPIC_API_KEY found, AI features will be disabled")
except ImportError:
    anthropic_client = None
    logger.warning("anthropic package not found, AI features will be disabled")

def get_sql_documentation():
    """
    Fetch SQL documentation using Context7 MCP.
    
    Returns:
        str: SQL documentation or empty string if Context7 is not available
    """
    if not IN_MCP:
        logger.warning("Not running in MCP context, cannot fetch SQL documentation")
        return ""
    
    try:
        # First resolve the library ID for SQL Server
        from mcp.function import resolve_context7_library_id, get_context7_library_docs
        
        resolve_result = resolve_context7_library_id(libraryName="SQL Server")
        if not resolve_result or "id" not in resolve_result:
            logger.warning("Could not resolve SQL Server library ID")
            return ""
            
        library_id = resolve_result["id"]
        
        # Now fetch the documentation
        docs_result = get_context7_library_docs(
            context7CompatibleLibraryID=library_id,
            tokens=5000,
            topic="SELECT queries"
        )
        
        if docs_result and "textContent" in docs_result:
            return docs_result["textContent"]
        else:
            logger.warning("Could not fetch SQL Server documentation")
            return ""
    except Exception as e:
        logger.error(f"Error fetching SQL documentation: {str(e)}")
        return ""

def execute_sql_query(sql_query):
    """
    Execute an SQL query using the MCP SQL server.
    
    Args:
        sql_query: SQL query to execute
        
    Returns:
        dict: Query result or error
    """
    if not IN_MCP:
        logger.warning("Not running in MCP context, cannot execute SQL query")
        return {"error": "Not running in MCP context"}
    
    try:
        from mcp.function import execute_sql
        
        # Call the MCP SQL server to execute the query
        result = execute_sql(query=sql_query)
        
        # Parse the result
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"data": result}
        return result
    except Exception as e:
        logger.error(f"Error executing SQL query: {str(e)}")
        return {"error": str(e)}

def generate_sql_from_question(question, docs=""):
    """
    Use AI to generate an SQL query from a natural language question.
    
    Args:
        question: Natural language question
        docs: SQL documentation to help the AI
        
    Returns:
        str: SQL query
    """
    if not anthropic_client:
        # If no AI is available, return a placeholder query
        logger.warning("No AI client available, returning placeholder query")
        return "SELECT 'AI not available' AS message"
    
    try:
        # Create a prompt for the AI
        prompt = f"""You are an expert SQL developer. Convert the following natural language question into a SQL query for SQL Server. 
The query should be valid SQL that could be executed against a database.
Only return the SQL query itself, nothing else.

{docs}

Question: {question}

SQL query:"""

        # Call the Anthropic API
        response = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the SQL query from the response
        if response and response.content:
            sql_query = response.content[0].text.strip()
            # Clean up any markdown code blocks
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.startswith("```"):
                sql_query = sql_query[3:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            return sql_query.strip()
        else:
            logger.error("Empty response from AI")
            return "SELECT 'AI error: empty response' AS message"
    except Exception as e:
        logger.error(f"Error generating SQL from question: {str(e)}")
        return f"SELECT 'AI error: {str(e)}' AS message"

def generate_answer_from_result(question, sql_query, result):
    """
    Use AI to generate a natural language answer from the SQL query result.
    
    Args:
        question: Original natural language question
        sql_query: SQL query that was executed
        result: Result of the SQL query
        
    Returns:
        str: Natural language answer
    """
    if not anthropic_client:
        # If no AI is available, return a simple answer
        logger.warning("No AI client available, returning simple answer")
        return f"Here's the result of your query: {result}"
    
    try:
        # Convert result to string if it's a dict
        if isinstance(result, dict):
            result_str = json.dumps(result, indent=2)
        else:
            result_str = str(result)
        
        # Create a prompt for the AI
        prompt = f"""You are an assistant that helps users understand SQL query results. 
The user asked: "{question}"

The following SQL query was executed:
```sql
{sql_query}
```

And it returned this result:
```
{result_str}
```

Please provide a clear, concise natural language answer to the user's original question based on this result.
Explain the data in a way that directly answers their question. Be conversational but focused on the facts.
"""

        # Call the Anthropic API
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the answer from the response
        if response and response.content:
            return response.content[0].text.strip()
        else:
            logger.error("Empty response from AI")
            return f"Here's the result of your query: {result}"
    except Exception as e:
        logger.error(f"Error generating answer from result: {str(e)}")
        return f"Here's the result of your query: {result} (Error: {str(e)})"

def answer_question(question: str) -> Dict[str, Any]:
    """
    Main function to answer a natural language question about the database.
    
    Args:
        question: Natural language question
        
    Returns:
        dict: Answer and SQL query (if available)
    """
    logger.info(f"Processing question: {question}")
    
    # Get SQL documentation if available in MCP context
    docs = get_sql_documentation()
    
    # Generate SQL query from the question using AI
    sql_query = generate_sql_from_question(question, docs)
    logger.info(f"Generated SQL query: {sql_query}")
    
    # Execute the SQL query
    result = execute_sql_query(sql_query)
    logger.info(f"Query result: {result}")
    
    # Generate a natural language answer from the result
    answer = generate_answer_from_result(question, sql_query, result)
    logger.info(f"Generated answer: {answer}")
    
    # Return the answer and SQL query for display
    return {
        "answer": answer,
        "sql": sql_query
    }
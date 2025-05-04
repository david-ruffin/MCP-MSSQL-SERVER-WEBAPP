import pytest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.mark.skip(reason="Requires actual database connection")
def test_database_connection():
    """
    Test that we can connect to the database (requires real credentials).
    """
    import pyodbc
    
    # Get connection details from environment variables
    server = os.getenv("MSSQL_SERVER")
    database = os.getenv("MSSQL_DATABASE")
    username = os.getenv("MSSQL_USER")
    password = os.getenv("MSSQL_PASSWORD")
    driver = os.getenv("MSSQL_DRIVER")
    
    # Skip if credentials are missing
    if not all([server, database, username, password, driver]):
        pytest.skip("Database credentials not configured")
    
    # Attempt to connect
    conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes"
    conn = pyodbc.connect(conn_str)
    
    # Assert connection is successful if we got this far
    assert conn is not None
    
    # Close connection
    conn.close()
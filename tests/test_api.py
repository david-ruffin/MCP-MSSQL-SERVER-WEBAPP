import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.app.api import app

# Create a test client
client = TestClient(app)

# Mock the answer_question function to avoid making real API calls and DB queries
@pytest.fixture(autouse=True)
def mock_answer_question():
    with patch("backend.app.api.answer_question") as mock:
        # Default mock response
        mock.return_value = {
            "answer": "There are 5 users in the database.",
            "sql": "SELECT COUNT(*) FROM users"
        }
        yield mock


def test_root_endpoint():
    """
    Test the root endpoint returns a status message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "running" in response.json()["message"]


def test_query_endpoint_with_valid_question(mock_answer_question):
    """
    Test the query endpoint with a valid question.
    """
    # Arrange
    test_question = "How many users are in the database?"
    
    # Act
    response = client.post(
        "/query",
        json={"question": test_question}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["answer"] == "There are 5 users in the database."
    assert response.json()["sql"] == "SELECT COUNT(*) FROM users"
    mock_answer_question.assert_called_once_with(test_question)


def test_query_endpoint_with_empty_question():
    """
    Test the query endpoint with an empty question.
    """
    response = client.post(
        "/query",
        json={"question": ""}
    )
    
    # Empty question is still valid according to the API schema
    assert response.status_code == 200


def test_query_endpoint_with_error(mock_answer_question):
    """
    Test the query endpoint when answer_question raises an exception.
    """
    # Arrange - make the mock raise an exception
    mock_answer_question.side_effect = Exception("Test error")
    
    # Act
    response = client.post(
        "/query",
        json={"question": "How many users?"}
    )
    
    # Assert
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "Test error" in response.json()["detail"]


def test_query_endpoint_string_response(mock_answer_question):
    """
    Test the query endpoint when answer_question returns a string.
    """
    # Arrange - make the mock return a string
    mock_answer_question.return_value = "Simple string answer"
    
    # Act
    response = client.post(
        "/query",
        json={"question": "How many users?"}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["answer"] == "Simple string answer"
    assert response.json()["sql"] is None
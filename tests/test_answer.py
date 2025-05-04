import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

from backend.app.answer import (
    get_sql_documentation,
    execute_sql_query,
    generate_sql_from_question,
    generate_answer_from_result,
    answer_question
)


@pytest.fixture
def mock_anthropic():
    with patch('backend.app.answer.anthropic_client') as mock:
        mock.messages.create.return_value = MagicMock(
            content=[MagicMock(text="SELECT COUNT(*) FROM users")]
        )
        yield mock


@pytest.fixture
def mock_execute_sql():
    with patch('backend.app.answer.execute_sql_query') as mock:
        mock.return_value = {"count": 5}
        yield mock


def test_generate_sql_from_question(mock_anthropic):
    """
    Test that generate_sql_from_question calls Anthropic API.
    """
    # Act
    result = generate_sql_from_question("How many users are there?", "SQL docs")
    
    # Assert
    assert "SELECT COUNT(*) FROM users" in result
    mock_anthropic.messages.create.assert_called_once()


def test_generate_sql_from_question_without_ai():
    """
    Test that generate_sql_from_question returns a placeholder when no AI is available.
    """
    # Arrange
    with patch('backend.app.answer.anthropic_client', None):
        # Act
        result = generate_sql_from_question("How many users are there?")
        
        # Assert
        assert "AI not available" in result


def test_generate_answer_from_result(mock_anthropic):
    """
    Test that generate_answer_from_result calls Anthropic API.
    """
    # Act
    result = generate_answer_from_result(
        "How many users are there?", 
        "SELECT COUNT(*) FROM users", 
        {"count": 5}
    )
    
    # Assert
    assert result == "SELECT COUNT(*) FROM users"
    mock_anthropic.messages.create.assert_called_once()


def test_answer_question(mock_anthropic, mock_execute_sql):
    """
    Test that answer_question follows the expected flow.
    """
    # Act
    result = answer_question("How many users are there?")
    
    # Assert
    assert isinstance(result, dict)
    assert "answer" in result
    assert "sql" in result

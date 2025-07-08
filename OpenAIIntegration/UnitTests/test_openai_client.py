"""
test_openai_client.py
--------------------
Unit tests for openai_client.py. Tests header and payload construction, HTTP request logic, and error handling.
Mocks network calls and environment variables for isolation.
"""

import os
import pytest
from unittest.mock import Mock, patch
from src import openai_client

def test_build_headers():
    """
    Test that _build_headers returns correct headers for a given API key.
    """

    api_key = "testkey"
    headers = openai_client._build_headers(api_key)
    assert headers["Authorization"] == f"Bearer {api_key}"
    assert headers["Content-Type"] == "application/json"

def test_build_payload():
    """
    Test that _build_payload constructs the correct payload for the API request.
    """

    prompt = "What is AI?"
    model = "test-model"
    max_tokens = 42
    payload = openai_client._build_payload(prompt, model, max_tokens)
    assert payload["model"] == model
    assert payload["max_tokens"] == max_tokens
    assert payload["messages"][1]["content"] == prompt

def test_post_request_success():
    """
    Test that _post_request returns the response object from the session's post method.
    """

    mock_session = Mock()
    mock_response = Mock(status_code=200, text="success")
    mock_session.post.return_value = mock_response
    response = openai_client._post_request(mock_session, "url", {}, "{}", 10)
    assert response.status_code == 200
    assert response.text == "success"

def test_send_text_completion_request_success():
    """
    Test that send_text_completion_request returns the expected response text on success.
    """

    prompt = "Say hi"
    api_key = "abc123"
    expected_response = "{\"choices\": []}"
    mock_session = Mock()
    mock_response = Mock(status_code=200, text=expected_response)
    mock_session.post.return_value = mock_response
    result = openai_client.send_text_completion_request(
        prompt,
        api_key=api_key,
        session=mock_session
    )
    assert result == expected_response
    mock_session.post.assert_called_once()

def test_send_text_completion_request_api_key_env(monkeypatch):
    """
    Test that send_text_completion_request uses the API key from the environment variable if not provided.
    """

    prompt = "Say hi"
    expected_response = "{\"choices\": []}"
    mock_session = Mock()
    mock_response = Mock(status_code=200, text=expected_response)
    mock_session.post.return_value = mock_response
    monkeypatch.setenv("API_KEY", "envkey")
    result = openai_client.send_text_completion_request(
        prompt,
        api_key=None,
        session=mock_session
    )
    assert result == expected_response

def test_send_text_completion_request_no_api_key(monkeypatch):
    """
    Test that send_text_completion_request raises an error if no API key is provided or set in the environment.
    """

    prompt = "Say hi"
    mock_session = Mock()
    monkeypatch.delenv("API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="API_KEY environment variable is not set"):
        openai_client.send_text_completion_request(
            prompt,
            api_key=None,
            session=mock_session
        )

def test_send_text_completion_request_failure():
    """
    Test that send_text_completion_request raises an error if the API returns a non-200 status code.
    """
    
    prompt = "Say hi"
    api_key = "abc123"
    mock_session = Mock()
    mock_response = Mock(status_code=400, text="bad request")
    mock_session.post.return_value = mock_response
    with pytest.raises(RuntimeError, match="API request failed with status code: 400"):
        openai_client.send_text_completion_request(
            prompt,
            api_key=api_key,
            session=mock_session
        ) 
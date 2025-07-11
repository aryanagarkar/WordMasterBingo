"""
test_meaning_and_synonym_fetcher.py
-----------------------------------
Unit tests for meaning_and_synonym_fetcher.py. Tests prompt building, response parsing, and the main get_definitions logic.
Mocks the OpenAI API call for isolation.
"""

import pytest
from OpenAIIntegration.src import meaning_and_synonym_fetcher as fetcher

def test_build_prompt():
    """
    Test that _build_prompt correctly formats the prompt with the given word.
    """

    word = "apple"
    prompt = fetcher._build_prompt(word)
    assert word in prompt
    assert "Definition" in prompt
    assert "Easy synonym" in prompt

def test_parse_response_valid():
    """
    Test that _parse_response extracts the content from a valid OpenAI API response.
    """

    response = '{"choices": [{"message": {"content": "definition, easy, medium, hard"}}]}'
    result = fetcher._parse_response(response)
    assert result == "definition, easy, medium, hard"

def test_parse_response_missing_fields():
    """
    Test that _parse_response returns an empty string if expected fields are missing.
    """

    response = '{"choices": [{}]}'
    result = fetcher._parse_response(response)
    assert result == ""

def test_parse_response_invalid_json():
    """
    Test that _parse_response returns an empty string if the response is not valid JSON.
    """

    response = 'not a json string'
    result = fetcher._parse_response(response)
    assert result == ""

def test_get_definitions_success():
    """
    Test that get_definitions returns the expected string when the API call is mocked to return a valid response.
    """

    def mock_send_text_completion_request(prompt):
        """
        Returns a valid OpenAI-style response with definition and synonyms for any prompt.
        """
        
        return '{"choices": [{"message": {"content": "def, easy, med, hard"}}]}'
    result = fetcher.get_definitions("banana", send_text_completion_request=mock_send_text_completion_request)
    assert result == "def, easy, med, hard"

def test_get_definitions_empty():
    """
    Test that get_definitions returns an empty string when the API call is mocked to return a response with missing fields.
    """

    def mock_send_text_completion_request(prompt):
        """
        Returns an OpenAI-style response with missing fields for any prompt.
        """
        
        return '{"choices": [{}]}'
    result = fetcher.get_definitions("banana", send_text_completion_request=mock_send_text_completion_request)
    assert result == ""

def test_get_definitions_invalid_json():
    """
    Test that get_definitions returns an empty string when the API call is mocked to return invalid JSON.
    """
    
    def mock_send_text_completion_request(prompt):
        """
        Returns a string that is not valid JSON for any prompt.
        """
        
        return 'not a json string'
    result = fetcher.get_definitions("banana", send_text_completion_request=mock_send_text_completion_request)
    assert result == "" 
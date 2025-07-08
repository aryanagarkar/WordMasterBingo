import pytest
from src import meaning_and_synonym_fetcher as fetcher

def test_build_prompt():
    word = "apple"
    prompt = fetcher._build_prompt(word)
    assert word in prompt
    assert "Definition" in prompt
    assert "Easy synonym" in prompt

def test_parse_response_valid():
    # Simulate a valid OpenAI API response
    response = '{"choices": [{"message": {"content": "definition, easy, medium, hard"}}]}'
    result = fetcher._parse_response(response)
    assert result == "definition, easy, medium, hard"

def test_parse_response_missing_fields():
    # Simulate a response missing expected fields
    response = '{"choices": [{}]}'
    result = fetcher._parse_response(response)
    assert result == ""

def test_parse_response_invalid_json():
    response = 'not a json string'
    result = fetcher._parse_response(response)
    assert result == ""

def test_get_definitions_success():
    def mock_send_text_completion_request(prompt):
        # Return a valid OpenAI-like response
        return '{"choices": [{"message": {"content": "def, easy, med, hard"}}]}'
    result = fetcher.get_definitions("banana", send_text_completion_request=mock_send_text_completion_request)
    assert result == "def, easy, med, hard"

def test_get_definitions_empty():
    def mock_send_text_completion_request(prompt):
        # Return a response with missing fields
        return '{"choices": [{}]}'
    result = fetcher.get_definitions("banana", send_text_completion_request=mock_send_text_completion_request)
    assert result == ""

def test_get_definitions_invalid_json():
    def mock_send_text_completion_request(prompt):
        return 'not a json string'
    result = fetcher.get_definitions("banana", send_text_completion_request=mock_send_text_completion_request)
    assert result == "" 
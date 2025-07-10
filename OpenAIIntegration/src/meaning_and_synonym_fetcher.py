"""
meaning_and_synonym_fetcher.py
-----------------------------
Fetches a simple definition and three synonyms (easy, medium, hard) for a given word using the OpenAI API.
Provides helpers for prompt building and response parsing. Designed for easy unit testing and mocking.
"""

import json
from .openai_client import send_text_completion_request as real_send_text_completion_request

PROMPT_TEMPLATE = (
    "Give me a simple Definition and 3 synonyms for the word '{word}' with the following rules: "
    "The easy synonym should be a word appropriate for advanced grades 1 to 5, "
    "the medium synonym should be the word itself ('{word}'), "
    "and the hard synonym should be a word appropriate for advanced grades 9 to 12. "
    "Format the response as a single line, separated by pipes: "
    "<put definition here>|<Easy synonym (grades 1-5)>|<Medium synonym: the word itself>|<Hard synonym (grades 9-12)>"
)

def _build_prompt(word: str) -> str:
    """
    Build the prompt for the OpenAI API to fetch definition and synonyms.
    Args:
        word (str): The word to fetch for.
    Returns:
        str: The formatted prompt string.
    """

    return PROMPT_TEMPLATE.format(word=word)

def _parse_response(response: str) -> str:
    """
    Parse the OpenAI API response and extract the definition and synonyms.
    Args:
        response (str): The raw response from the API.
    Returns:
        str: The extracted content, or an empty string if parsing fails.
    """

    try:
        response_node = json.loads(response)
        choices = response_node.get("choices")
        if choices and isinstance(choices, list) and len(choices) > 0:
            first_choice = choices[0]
            message = first_choice.get("message")
            if message:
                content = message.get("content")
                if content:
                    return content
        print("Warning: Could not find expected fields in response.")
        return ""
    except Exception as e:
        print(f"JSON parsing error: {e}")
        return ""

def get_definitions(word: str, send_text_completion_request=real_send_text_completion_request) -> str:
    """
    Fetches a simple definition and three synonyms (easy, medium, hard) for the given word from OpenAI.
    Args:
        word (str): The word to fetch the definition and synonyms for.
        send_text_completion_request (callable): Dependency-injected function for OpenAI API call (for testing).
    Returns:
        str: The definition and synonyms as a comma-separated string, or an empty string if parsing fails.
    """
    
    prompt = _build_prompt(word)
    response = send_text_completion_request(prompt)
    print(f"Raw response: {response}")  # Debug: print the raw response
    return _parse_response(response) 
"""
openai_client.py
----------------
Handles communication with the OpenAI API for text completion requests. Provides helper functions for building headers, payloads, and making HTTP requests. Designed for easy unit testing and mocking.
"""

import os
import requests
import json

DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 60

def _build_headers(api_key: str) -> dict:
    """
    Build the HTTP headers for the OpenAI API request.
    Args:
        api_key (str): The OpenAI API key.
    Returns:
        dict: Headers including authorization and content type.
    """

    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

def _build_payload(prompt: str, model: str, max_tokens: int) -> dict:
    """
    Build the payload for the OpenAI API request.
    Args:
        prompt (str): The prompt to send to the model.
        model (str): The model name.
        max_tokens (int): Maximum tokens to generate.
    Returns:
        dict: The payload for the API request.
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    return {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }

def _post_request(session, url, headers, data, timeout):
    """
    Make a POST request to the OpenAI API.
    Args:
        session: requests.Session or requests module for HTTP calls.
        url (str): The API endpoint.
        headers (dict): HTTP headers.
        data (str): JSON-encoded payload.
        timeout (int): Timeout in seconds.
    Returns:
        requests.Response: The HTTP response object.
    """

    return session.post(url, headers=headers, data=data, timeout=timeout)

def send_text_completion_request(
    prompt: str,
    api_key: str = None,
    api_url: str = DEFAULT_API_URL,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    session: requests.Session = None,
    timeout: int = 60
) -> str:
    """
    Sends a prompt to the OpenAI API and returns the response text.
    All parameters can be overridden for testing/mocking.
    Args:
        prompt (str): The prompt to send to the model.
        api_key (str, optional): The OpenAI API key. Defaults to environment variable 'API_KEY'.
        api_url (str, optional): The API endpoint. Defaults to DEFAULT_API_URL.
        model (str, optional): The model name. Defaults to DEFAULT_MODEL.
        max_tokens (int, optional): Maximum tokens to generate. Defaults to DEFAULT_MAX_TOKENS.
        session (requests.Session, optional): HTTP session or requests module. Defaults to requests.
        timeout (int, optional): Timeout in seconds. Defaults to 60.
    Returns:
        str: The raw response text from the API.
    Raises:
        RuntimeError: If the API key is missing or the request fails.
    """
    
    if api_key is None:
        api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY environment variable is not set and no api_key was provided")
    headers = _build_headers(api_key)
    payload = _build_payload(prompt, model, max_tokens)
    request_session = session or requests
    response = _post_request(request_session, api_url, headers, json.dumps(payload), timeout)
    if response.status_code == 200:
        return response.text
    else:
        raise RuntimeError(f"API request failed with status code: {response.status_code}, Response: {response.text}") 
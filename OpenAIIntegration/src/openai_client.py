import os
import requests
import json

DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 60

def _build_headers(api_key: str) -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

def _build_payload(prompt: str, model: str, max_tokens: int) -> dict:
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
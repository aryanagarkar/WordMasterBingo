import json
from .openai_client import send_text_completion_request as real_send_text_completion_request

PROMPT_TEMPLATE = (
    "Give me a simple Definition and 3 synonyms with difficulty level of easy, medium, and hard for the word '{word}', "
    "Format the response as a comma separate list in a single line - "
    "<put definition here>, <Easy synonym>, <Medium synonym>, <hard synonym>"
)

def _build_prompt(word: str) -> str:
    return PROMPT_TEMPLATE.format(word=word)

def _parse_response(response: str) -> str:
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
    The response is returned in the format: <definition>, <easy synonym>, <medium synonym>, <hard synonym>
    :param word: The word to fetch the definition and synonyms for.
    :param send_text_completion_request: Dependency-injected function for OpenAI API call (for testing).
    :return: The definition and synonyms as a comma-separated string, or an empty string if parsing fails.
    """
    prompt = _build_prompt(word)
    response = send_text_completion_request(prompt)
    print(f"Raw response: {response}")  # Debug: print the raw response
    return _parse_response(response) 
import os
import requests
from openai import OpenAI
from typing import Optional, Any
from CardGraphics.src.model_name import ModelName

# Model and API constants
OPENAI_DEFAULT_MODEL = "dall-e-3"
GEMINI_DEFAULT_MODEL = "gemini-pro"
GEMINI_IMAGE_MODEL = "gemini-2.0-flash-preview-image-generation"

OPENAI_API_URL = "https://api.openai.com/v1/images/generations"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

DEFAULT_IMAGE_SIZE = "1024x1024"

# Constants
OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
GEMINI_API_KEY_ENV_VAR = "GEMINI_API_KEY"
API_KEY_ERROR_MSG = "Error: Please set your OpenAI API key in the OPENAI_API_KEY environment variable."
GEMINI_API_KEY_ERROR_MSG = f"Error: Please set your Gemini API key in the {GEMINI_API_KEY_ENV_VAR} environment variable."
PROMPT_TEMPLATE = (
    "A simple, clear, and literal illustration of the word '{word}': {definition}. "
    "Use the definition provided to determine the meaning. "
    "Show only the most direct, universally recognized visual representation of the word as defined. "
    "The image should be a white line drawing with a black background. "
    "Do not use other meanings of the word. "
    "No text, no letters, no extra objects, no crowds, no cartoonish style, no unrelated people. "
    "The image should be immediately understandable to a child, with no ambiguity. "
    "Do not use subtle or abstract representations. If using a symbol or object, make it obvious and easily recognized for the word as defined."
)
USER_INPUT_PROMPT = "Enter a word to illustrate: "
DEFINITION_INPUT_PROMPT = "Enter the definition for the word: "
NO_WORD_MSG = "No word entered. Exiting."
GENERATING_MSG = "Generating image, please wait..."
GENERATION_FAILED_MSG = "Failed to generate image."
DOWNLOAD_FAILED_MSG = "Failed to download image."
IMAGE_SAVED_MSG = "Image saved as {filename}"
GENERATION_ERROR_MSG = "Error generating image: {error}"
DOWNLOAD_ERROR_MSG = "Error downloading image: {error}"
FILENAME_TEMPLATE = "{word}_for_child.png"

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv(OPENAI_API_KEY_ENV_VAR)
if not OPENAI_API_KEY:
    print(API_KEY_ERROR_MSG)
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def create_child_friendly_prompt(word: str, definition: str) -> str:
    """
    Creates a child-friendly prompt for image generation using the word and its definition.
    
    Args:
        word (str): The word to illustrate
        definition (str): The definition of the word
    
    Returns:
        str: A formatted prompt optimized for educational clarity
    """

    return PROMPT_TEMPLATE.format(word=word, definition=definition)

def generate_image(prompt: str, model: str = OPENAI_DEFAULT_MODEL, size: str = DEFAULT_IMAGE_SIZE, client_obj: Any = None) -> Optional[str]:
    """
    Generates an image using OpenAI's DALL-E API.
    Allows dependency injection of the OpenAI client for testing.
    
    Args:
        prompt (str): The prompt describing the image to generate
        model (str): The DALL-E model to use (default: "dall-e-3")
        size (str): The size of the generated image (default: "1024x1024")
        client_obj (Any): The OpenAI client object (default: None)
        
    Returns:
        Optional[str]: The URL of the generated image, or None if generation failed
    """

    if client_obj is None:
        client_obj = client
    try:
        response = client_obj.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size=size
        )
        return get_image_url_from_response(response)
    except Exception as e:
        print(GENERATION_ERROR_MSG.format(error=e))
        return None

def get_image_url_from_response(response: Any) -> Optional[str]:
    """
    Extracts the image URL from the OpenAI API response object.
    Returns None if not found.
    """
    
    # The response is expected to have a .data[0].url attribute
    try:
        return response.data[0].url
    except (AttributeError, IndexError, KeyError):
        return None

def is_valid_image_url(url: str) -> bool:
    """
    Checks if the given URL is a valid image URL (basic check).
    """

    return isinstance(url, str) and url.startswith("http") and (url.endswith(".png") or url.endswith(".jpg") or url.endswith(".jpeg"))

def download_image(image_url: str, filename: str, requests_module: Any = None) -> bool:
    """
    Downloads an image from a URL and saves it to a file.
    Allows dependency injection of the requests module for testing.
    
    Args:
        image_url (str): The URL of the image to download
        filename (str): The filename to save the image as
        requests_module (Any): The requests module object (default: None)
        
    Returns:
        bool: True if download successful, False otherwise
    """

    if requests_module is None:
        requests_module = requests
    try:
        img_data = requests_module.get(image_url).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        return True
    except Exception as e:
        print(DOWNLOAD_ERROR_MSG.format(error=e))
        return False

def get_user_input() -> Optional[tuple]:
    """
    Gets user input for the word and its definition to illustrate.
    
    Returns:
        Optional[tuple]: The user's input as (word, definition), or None if no input provided
    """

    word = input(USER_INPUT_PROMPT).strip()
    if not word:
        return None
    definition = input(DEFINITION_INPUT_PROMPT).strip()
    if not definition:
        return None
    return word, definition

def create_filename(word: str, model_name: str = None) -> str:
    """
    Creates a filename for the generated image, optionally including the model name.
    Args:
        word (str): The word that was illustrated
        model_name (str): The model name to append (e.g., 'openai', 'gemini')
    Returns:
        str: A descriptive filename
    """

    if model_name:
        return FILENAME_TEMPLATE.replace('.png', f'_{model_name}.png').format(word=word)
    return FILENAME_TEMPLATE.format(word=word)

def generate_image_openai(prompt, model=OPENAI_DEFAULT_MODEL, size=DEFAULT_IMAGE_SIZE):
    """
    Generate an image using OpenAI's DALL-E API.
    Args:
        prompt (str): The prompt describing the image to generate.
        model (str): The DALL-E model to use (default: OPENAI_DEFAULT_MODEL).
        size (str): The size of the generated image (default: DEFAULT_IMAGE_SIZE).
    Returns:
        str: The URL of the generated image.
    Raises:
        RuntimeError: If the API key is not set or the API call fails.
    """

    from openai import OpenAI
    api_key = os.getenv(OPENAI_API_KEY_ENV_VAR)
    if not api_key:
        raise RuntimeError(API_KEY_ERROR_MSG)
    client = OpenAI(api_key=api_key)
    response = client.images.generate(model=model, prompt=prompt, n=1, size=size)
    return response.data[0].url

def generate_image_gemini(prompt, model=GEMINI_IMAGE_MODEL):
    """
    Generate an image using Google's Gemini image generation model.
    Args:
        prompt (str): The prompt to send to Gemini.
        model (str): The Gemini image model to use (default: GEMINI_IMAGE_MODEL).
    Returns:
        dict: {"image_bytes": bytes, "text": str} if successful, None otherwise.
    Raises:
        RuntimeError: If the API key is not set or the API call fails.
    """

    import base64
    api_key = os.getenv(GEMINI_API_KEY_ENV_VAR)
    if not api_key:
        raise RuntimeError(GEMINI_API_KEY_ERROR_MSG)
    url = f"{GEMINI_API_URL}/{model}:generateContent?key={api_key}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }
    response = requests.post(url, json=data, timeout=60)
    response.raise_for_status()
    resp_json = response.json()

    # Find the image and text in the response
    image_bytes = None
    text = None
    try:
        for part in resp_json["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                image_bytes = base64.b64decode(part["inlineData"]["data"])
            elif "text" in part:
                text = part["text"]
    except Exception as e:
        print(GENERATION_ERROR_MSG.format(error=e))
        return None
    if image_bytes:
        return {"image_bytes": image_bytes, "text": text}
    else:
        return None

def generate_image_with_model(prompt, model_name: ModelName):
    """
    Dispatch image or prompt generation to the selected model provider.
    Args:
        prompt (str): The prompt to send to the model.
        model_name (ModelName): The model provider to use (OPENAI or GEMINI).
    Returns:
        dict or str: For OpenAI, returns image URL. For Gemini, returns dict with image bytes and text.
    Raises:
        ValueError: If an unknown model is specified.
    """
    
    if model_name == ModelName.OPENAI:
        return generate_image_openai(prompt)
    elif model_name == ModelName.GEMINI:
        return generate_image_gemini(prompt)
    else:
        raise ValueError(f"Unknown model: {model_name}")

def main():
    """
    Main function that handles the complete workflow:
    1. Prompts user for a word and its definition to illustrate
    2. Creates a child-friendly prompt for image generation
    3. Calls both OpenAI and Gemini APIs to generate images
    4. Downloads and saves the generated images locally with model-specific filenames
    """

    # Get user input for the word and its definition to illustrate
    user_input = get_user_input()
    if not user_input:
        print(NO_WORD_MSG)
        return
    word, definition = user_input

    # Create a child-friendly prompt optimized for educational clarity
    prompt = create_child_friendly_prompt(word, definition)

    print(GENERATING_MSG)

    # Generate image using OpenAI
    openai_result = generate_image_with_model(prompt, ModelName.OPENAI)
    openai_filename = create_filename(word, ModelName.OPENAI.value)
    if openai_result:
        if download_image(openai_result, openai_filename):
            print(f"[OpenAI] {IMAGE_SAVED_MSG.format(filename=openai_filename)}")
        else:
            print(f"[OpenAI] {DOWNLOAD_FAILED_MSG}")
    else:
        print(f"[OpenAI] {GENERATION_FAILED_MSG}")

    # Generate image using Gemini
    gemini_result = generate_image_with_model(prompt, ModelName.GEMINI)
    gemini_filename = create_filename(word, ModelName.GEMINI.value)
    if gemini_result:
        try:
            with open(gemini_filename, "wb") as f:
                f.write(gemini_result["image_bytes"])
            print(f"[Gemini] {IMAGE_SAVED_MSG.format(filename=gemini_filename)}")
            
            # Optionally print Gemini's explanation if present
            # if gemini_result["text"]:
            #     print(f"Gemini also said: {gemini_result['text']}")
        except Exception as e:
            print(f"[Gemini] {DOWNLOAD_ERROR_MSG.format(error=e)}")
    else:
        print(f"[Gemini] {GENERATION_FAILED_MSG}")

if __name__ == "__main__":
    main()
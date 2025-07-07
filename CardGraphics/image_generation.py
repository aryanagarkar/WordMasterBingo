import os
import requests
from openai import OpenAI
from typing import Optional

# Constants
OPENAI_API_KEY_ENV_VAR = "API_KEY"
API_KEY_ERROR_MSG = "Error: Please set your OpenAI API key in the OPENAI_API_KEY environment variable."
DEFAULT_MODEL = "dall-e-3"
DEFAULT_SIZE = "1024x1024"
PROMPT_TEMPLATE = "A VERY SIMPLE illustration of a '{word}' that a parent would use to teach 10-year-old child, that gets straight to the point. No complex pieces of art, no more than 4 objects."
USER_INPUT_PROMPT = "Enter a word to illustrate for a two-year-old: "
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

def create_child_friendly_prompt(word: str) -> str:
    """
    Creates a child-friendly prompt for image generation.
    
    Args:
        word (str): The word to illustrate
        
    Returns:
        str: A formatted prompt optimized for educational clarity
    """
    return PROMPT_TEMPLATE.format(word=word)

def generate_image(prompt: str, model: str = DEFAULT_MODEL, size: str = DEFAULT_SIZE) -> Optional[str]:
    """
    Generates an image using OpenAI's DALL-E API.
    
    Args:
        prompt (str): The prompt describing the image to generate
        model (str): The DALL-E model to use (default: "dall-e-3")
        size (str): The size of the generated image (default: "1024x1024")
        
    Returns:
        Optional[str]: The URL of the generated image, or None if generation failed
    """
    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size=size
        )
        return response.data[0].url
    except Exception as e:
        print(GENERATION_ERROR_MSG.format(error=e))
        return None

def download_image(image_url: str, filename: str) -> bool:
    """
    Downloads an image from a URL and saves it to a file.
    
    Args:
        image_url (str): The URL of the image to download
        filename (str): The filename to save the image as
        
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        img_data = requests.get(image_url).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        return True
    except Exception as e:
        print(DOWNLOAD_ERROR_MSG.format(error=e))
        return False

def get_user_input() -> Optional[str]:
    """
    Gets user input for the word to illustrate.
    
    Returns:
        Optional[str]: The user's input, or None if no input provided
    """
    word = input(USER_INPUT_PROMPT).strip()
    return word if word else None

def create_filename(word: str) -> str:
    """
    Creates a filename for the generated image.
    
    Args:
        word (str): The word that was illustrated
        
    Returns:
        str: A descriptive filename
    """
    return FILENAME_TEMPLATE.format(word=word)

def main():
    """
    Main function that handles the complete workflow:
    1. Prompts user for a word to illustrate
    2. Creates a child-friendly prompt for image generation
    3. Calls OpenAI's DALL-E API to generate an image
    4. Downloads and saves the generated image locally
    """
    # Get user input for the word to illustrate
    word = get_user_input()
    if not word:
        print(NO_WORD_MSG)
        return

    # Create a child-friendly prompt optimized for educational clarity
    prompt = create_child_friendly_prompt(word)

    print(GENERATING_MSG)
    
    # Generate image using OpenAI's DALL-E 3 model
    image_url = generate_image(prompt)
    if not image_url:
        print(GENERATION_FAILED_MSG)
        return
    
    # Create filename and download the image
    filename = create_filename(word)
    if download_image(image_url, filename):
        print(IMAGE_SAVED_MSG.format(filename=filename))
    else:
        print(DOWNLOAD_FAILED_MSG)

if __name__ == "__main__":
    main()
from enum import Enum

class ModelName(Enum):
    """
    Enum for selecting which LLM/image model provider to use for prompt or image generation.
    Usage:
        ModelName.OPENAI     # For OpenAI/ChatGPT/DALL-E
        ModelName.ANTHROPIC  # For Anthropic Claude
        ModelName.GEMINI     # For Google Gemini
    Pass this enum to dispatcher functions to select the provider.
    """
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini" 
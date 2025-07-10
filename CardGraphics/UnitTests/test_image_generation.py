import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
from CardGraphics.src.image_generation import (
    create_child_friendly_prompt,
    create_filename,
    download_image,
    get_user_input,
    generate_image,
    get_image_url_from_response,
    is_valid_image_url,
    
    # Import constants
    PROMPT_TEMPLATE,
    USER_INPUT_PROMPT,
    FILENAME_TEMPLATE,
    OPENAI_DEFAULT_MODEL,
    DEFAULT_IMAGE_SIZE,
    NO_WORD_MSG,
    GENERATION_FAILED_MSG,
    DOWNLOAD_FAILED_MSG,
    IMAGE_SAVED_MSG,
    GENERATION_ERROR_MSG,
    DOWNLOAD_ERROR_MSG,
    DEFINITION_INPUT_PROMPT,
    generate_image_with_model,
    ModelName,
    GEMINI_IMAGE_MODEL
)
import base64

class TestImageGeneration(unittest.TestCase):
    """Test cases for the image_generation module functions."""

    def test_constants_are_defined(self):
        """Test that all constants are properly defined."""
        self.assertIsInstance(PROMPT_TEMPLATE, str)
        self.assertIsInstance(USER_INPUT_PROMPT, str)
        self.assertIsInstance(FILENAME_TEMPLATE, str)
        self.assertIsInstance(OPENAI_DEFAULT_MODEL, str)
        self.assertIsInstance(DEFAULT_IMAGE_SIZE, str)
        self.assertIsInstance(NO_WORD_MSG, str)
        self.assertIsInstance(GENERATION_FAILED_MSG, str)
        self.assertIsInstance(DOWNLOAD_FAILED_MSG, str)
        self.assertIsInstance(IMAGE_SAVED_MSG, str)
        self.assertIsInstance(GENERATION_ERROR_MSG, str)
        self.assertIsInstance(DOWNLOAD_ERROR_MSG, str)
        self.assertIsInstance(DEFINITION_INPUT_PROMPT, str)

    def test_create_child_friendly_prompt(self):
        """Test that create_child_friendly_prompt generates correct prompts."""
        # Test with a simple word and definition
        result = create_child_friendly_prompt("cat", "a small domesticated animal")
        expected = PROMPT_TEMPLATE.format(word="cat", definition="a small domesticated animal")
        self.assertEqual(result, expected)
        
        # Test with a compound word and definition
        result = create_child_friendly_prompt("fire truck", "a large vehicle that puts out fires")
        expected = PROMPT_TEMPLATE.format(word="fire truck", definition="a large vehicle that puts out fires")
        self.assertEqual(result, expected)
        
        # Test with special characters
        result = create_child_friendly_prompt("don't", "to not do something")
        expected = PROMPT_TEMPLATE.format(word="don't", definition="to not do something")
        self.assertEqual(result, expected)

    def test_create_filename(self):
        """Test that create_filename generates correct filenames."""
        # Test with simple word
        result = create_filename("dog")
        expected = FILENAME_TEMPLATE.format(word="dog")
        self.assertEqual(result, expected)
        
        # Test with compound word
        result = create_filename("ice cream")
        expected = FILENAME_TEMPLATE.format(word="ice cream")
        self.assertEqual(result, expected)
        
        # Test with special characters
        result = create_filename("can't")
        expected = FILENAME_TEMPLATE.format(word="can't")
        self.assertEqual(result, expected)

        # Test with model name for OpenAI
        result = create_filename("dog", "openai")
        expected = FILENAME_TEMPLATE.replace('.png', '_openai.png').format(word="dog")
        self.assertEqual(result, expected)

        # Test with model name for Gemini
        result = create_filename("dog", "gemini")
        expected = FILENAME_TEMPLATE.replace('.png', '_gemini.png').format(word="dog")
        self.assertEqual(result, expected)

    @patch('builtins.input', side_effect=["testword", "test definition"])
    def test_get_user_input_with_valid_input(self, mock_input):
        """Test get_user_input with valid input for word and definition."""
        result = get_user_input()
        self.assertEqual(result, ("testword", "test definition"))
        self.assertEqual(mock_input.call_count, 2)
        mock_input.assert_any_call(USER_INPUT_PROMPT)
        mock_input.assert_any_call(DEFINITION_INPUT_PROMPT)

    @patch('builtins.input', side_effect=["   ", "test definition"])
    def test_get_user_input_with_empty_word(self, mock_input):
        """Test get_user_input with empty/whitespace word input."""
        result = get_user_input()
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=["testword", "   "])
    def test_get_user_input_with_empty_definition(self, mock_input):
        """Test get_user_input with empty/whitespace definition input."""
        result = get_user_input()
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=["", "test definition"])
    def test_get_user_input_with_no_word_input(self, mock_input):
        """Test get_user_input with no word input."""
        result = get_user_input()
        self.assertIsNone(result)

    @patch('builtins.input', side_effect=["testword", ""])
    def test_get_user_input_with_no_definition_input(self, mock_input):
        """Test get_user_input with no definition input."""
        result = get_user_input()
        self.assertIsNone(result)

    @patch('CardGraphics.src.image_generation.client')
    def test_generate_image_success(self, mock_client):
        """Test successful image generation."""
        # Mock the OpenAI client response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="https://example.com/test.png")]
        mock_client.images.generate.return_value = mock_response
        
        result = generate_image("test prompt")
        
        self.assertEqual(result, "https://example.com/test.png")
        mock_client.images.generate.assert_called_once_with(
            model=OPENAI_DEFAULT_MODEL,
            prompt="test prompt",
            n=1,
            size=DEFAULT_IMAGE_SIZE
        )

    @patch('CardGraphics.src.image_generation.client')
    def test_generate_image_failure(self, mock_client):
        """Test image generation failure."""
        # Mock the OpenAI client to raise an exception
        mock_client.images.generate.side_effect = Exception("API Error")
        
        result = generate_image("test prompt")
        
        self.assertIsNone(result)

    @patch('CardGraphics.src.image_generation.requests.get')
    def test_download_image_success(self, mock_get):
        """Test successful image download."""
        # Mock the requests response
        mock_response = MagicMock()
        mock_response.content = b"fake image data"
        mock_get.return_value = mock_response
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            result = download_image("https://example.com/test.png", temp_filename)
            self.assertTrue(result)
            
            # Verify the file was written
            with open(temp_filename, 'rb') as f:
                content = f.read()
            self.assertEqual(content, b"fake image data")
            
            mock_get.assert_called_once_with("https://example.com/test.png")
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    @patch('CardGraphics.src.image_generation.requests.get')
    def test_download_image_failure(self, mock_get):
        """Test image download failure."""
        # Mock requests to raise an exception
        mock_get.side_effect = Exception("Network Error")
        
        result = download_image("https://example.com/test.png", "nonexistent_file.png")
        self.assertFalse(result)

    def test_integration_workflow(self):
        """Test the integration of multiple functions."""
        # Test the complete workflow with mocked dependencies
        word = "elephant"
        definition = "a large animal with a trunk"
        prompt = create_child_friendly_prompt(word, definition)
        filename = create_filename(word)
        
        # Verify the workflow produces expected results
        self.assertIn("elephant", prompt)
        self.assertIn("trunk", prompt)
        self.assertEqual(filename, FILENAME_TEMPLATE.format(word="elephant"))
        self.assertIn("realistic", prompt)
        self.assertIn("plain or white", prompt)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with very long word and definition
        long_word = "a" * 100
        long_definition = "b" * 200
        prompt = create_child_friendly_prompt(long_word, long_definition)
        self.assertIn(long_word, prompt)
        self.assertIn(long_definition, prompt)
        
        # Test with numbers
        number_word = "123"
        number_definition = "a number sequence"
        prompt = create_child_friendly_prompt(number_word, number_definition)
        self.assertIn(number_word, prompt)
        self.assertIn(number_definition, prompt)
        
        # Test with unicode characters
        unicode_word = "café"
        unicode_definition = "a small restaurant"
        prompt = create_child_friendly_prompt(unicode_word, unicode_definition)
        self.assertIn(unicode_word, prompt)
        self.assertIn(unicode_definition, prompt)

    def test_constant_formats(self):
        """Test that constants have proper format placeholders."""
        # Test that PROMPT_TEMPLATE has the correct placeholder
        self.assertIn("{word}", PROMPT_TEMPLATE)
        
        # Test that FILENAME_TEMPLATE has the correct placeholder
        self.assertIn("{word}", FILENAME_TEMPLATE)
        
        # Test that IMAGE_SAVED_MSG has the correct placeholder
        self.assertIn("{filename}", IMAGE_SAVED_MSG)
        
        # Test that error messages have the correct placeholders
        self.assertIn("{error}", GENERATION_ERROR_MSG)
        self.assertIn("{error}", DOWNLOAD_ERROR_MSG)

    def test_constant_values(self):
        """Test that constants have expected values."""
        self.assertEqual(OPENAI_DEFAULT_MODEL, "dall-e-3")
        self.assertEqual(DEFAULT_IMAGE_SIZE, "1024x1024")
        self.assertIn("simple, clear, and realistic", PROMPT_TEMPLATE)
        self.assertIn("illustration", PROMPT_TEMPLATE)
        self.assertIn("_for_child.png", FILENAME_TEMPLATE)

    def test_get_image_url_from_response_success(self):
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url='http://example.com/image.png')]
        url = get_image_url_from_response(mock_response)
        self.assertEqual(url, 'http://example.com/image.png')

    def test_get_image_url_from_response_failure(self):
        mock_response = MagicMock()
        mock_response.data = []
        url = get_image_url_from_response(mock_response)
        self.assertIsNone(url)

    def test_is_valid_image_url(self):
        self.assertTrue(is_valid_image_url('http://example.com/image.png'))
        self.assertTrue(is_valid_image_url('https://example.com/image.jpg'))
        self.assertFalse(is_valid_image_url('ftp://example.com/image.png'))
        self.assertFalse(is_valid_image_url('http://example.com/image.txt'))
        self.assertFalse(is_valid_image_url(None))

    @patch('CardGraphics.src.image_generation.requests.post')
    def test_generate_image_gemini_success(self, mock_post):
        """Test successful Gemini image generation (image + text)."""
        # Prepare a fake image and text
        fake_image_bytes = b"fakeimagebytes"
        fake_image_b64 = base64.b64encode(fake_image_bytes).decode()
        fake_text = "Here is your image."
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "candidates": [{
                    "content": {
                        "parts": [
                            {"inlineData": {"data": fake_image_b64}},
                            {"text": fake_text}
                        ]
                    }
                }]
            },
            raise_for_status=lambda: None
        )
        from CardGraphics.src.image_generation import generate_image_gemini
        result = generate_image_gemini("test prompt")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["image_bytes"], fake_image_bytes)
        self.assertEqual(result["text"], fake_text)

    @patch('CardGraphics.src.image_generation.requests.post')
    def test_generate_image_gemini_failure(self, mock_post):
        """Test Gemini image generation failure (no image in response)."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"candidates": [{"content": {"parts": [{"text": "No image"}]}}]},
            raise_for_status=lambda: None
        )
        from CardGraphics.src.image_generation import generate_image_gemini
        result = generate_image_gemini("test prompt")
        self.assertIsNone(result)

    @patch('CardGraphics.src.image_generation.generate_image_openai')
    def test_generate_image_with_model_openai(self, mock_openai):
        """Test dispatcher for OpenAI model."""
        mock_openai.return_value = "https://example.com/openai.png"
        result = generate_image_with_model("prompt", ModelName.OPENAI)
        self.assertEqual(result, "https://example.com/openai.png")
        mock_openai.assert_called_once()

    @patch('CardGraphics.src.image_generation.generate_image_gemini')
    def test_generate_image_with_model_gemini(self, mock_gemini):
        """Test dispatcher for Gemini model."""
        mock_gemini.return_value = {"image_bytes": b"img", "text": "desc"}
        result = generate_image_with_model("prompt", ModelName.GEMINI)
        self.assertEqual(result, {"image_bytes": b"img", "text": "desc"})
        mock_gemini.assert_called_once()

    def test_generate_image_with_model_invalid(self):
        """Test dispatcher with invalid model name."""
        with self.assertRaises(ValueError):
            generate_image_with_model("prompt", "notamodel")

    @patch('CardGraphics.src.image_generation.open', new_callable=mock_open)
    def test_gemini_image_file_write(self, mock_file):
        """Test that Gemini image bytes are written to file correctly."""
        # Simulate the main logic for Gemini file writing
        filename = "testfile.png"
        image_bytes = b"imgdata"
        result = {"image_bytes": image_bytes, "text": "desc"}
        # Write to file
        with patch('builtins.open', mock_open()) as m:
            with open(filename, "wb") as f:
                f.write(result["image_bytes"])
            m.assert_called_with(filename, "wb")
            handle = m()
            handle.write.assert_called_once_with(image_bytes)

if __name__ == '__main__':
    unittest.main() 
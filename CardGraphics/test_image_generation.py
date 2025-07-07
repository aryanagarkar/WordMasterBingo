import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
from image_generation import (
    create_child_friendly_prompt,
    create_filename,
    download_image,
    get_user_input,
    generate_image,
    # Import constants
    PROMPT_TEMPLATE,
    USER_INPUT_PROMPT,
    FILENAME_TEMPLATE,
    DEFAULT_MODEL,
    DEFAULT_SIZE,
    NO_WORD_MSG,
    GENERATION_FAILED_MSG,
    DOWNLOAD_FAILED_MSG,
    IMAGE_SAVED_MSG,
    GENERATION_ERROR_MSG,
    DOWNLOAD_ERROR_MSG
)

class TestImageGeneration(unittest.TestCase):
    """Test cases for the image_generation module functions."""

    def test_constants_are_defined(self):
        """Test that all constants are properly defined."""
        self.assertIsInstance(PROMPT_TEMPLATE, str)
        self.assertIsInstance(USER_INPUT_PROMPT, str)
        self.assertIsInstance(FILENAME_TEMPLATE, str)
        self.assertIsInstance(DEFAULT_MODEL, str)
        self.assertIsInstance(DEFAULT_SIZE, str)
        self.assertIsInstance(NO_WORD_MSG, str)
        self.assertIsInstance(GENERATION_FAILED_MSG, str)
        self.assertIsInstance(DOWNLOAD_FAILED_MSG, str)
        self.assertIsInstance(IMAGE_SAVED_MSG, str)
        self.assertIsInstance(GENERATION_ERROR_MSG, str)
        self.assertIsInstance(DOWNLOAD_ERROR_MSG, str)

    def test_create_child_friendly_prompt(self):
        """Test that create_child_friendly_prompt generates correct prompts."""
        # Test with a simple word
        result = create_child_friendly_prompt("cat")
        expected = PROMPT_TEMPLATE.format(word="cat")
        self.assertEqual(result, expected)
        
        # Test with a compound word
        result = create_child_friendly_prompt("fire truck")
        expected = PROMPT_TEMPLATE.format(word="fire truck")
        self.assertEqual(result, expected)
        
        # Test with special characters
        result = create_child_friendly_prompt("don't")
        expected = PROMPT_TEMPLATE.format(word="don't")
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

    @patch('builtins.input', return_value="test")
    def test_get_user_input_with_valid_input(self, mock_input):
        """Test get_user_input with valid input."""
        result = get_user_input()
        self.assertEqual(result, "test")
        mock_input.assert_called_once_with(USER_INPUT_PROMPT)

    @patch('builtins.input', return_value="   ")
    def test_get_user_input_with_empty_input(self, mock_input):
        """Test get_user_input with empty/whitespace input."""
        result = get_user_input()
        self.assertIsNone(result)

    @patch('builtins.input', return_value="")
    def test_get_user_input_with_no_input(self, mock_input):
        """Test get_user_input with no input."""
        result = get_user_input()
        self.assertIsNone(result)

    @patch('image_generation.client')
    def test_generate_image_success(self, mock_client):
        """Test successful image generation."""
        # Mock the OpenAI client response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(url="https://example.com/test.png")]
        mock_client.images.generate.return_value = mock_response
        
        result = generate_image("test prompt")
        
        self.assertEqual(result, "https://example.com/test.png")
        mock_client.images.generate.assert_called_once_with(
            model=DEFAULT_MODEL,
            prompt="test prompt",
            n=1,
            size=DEFAULT_SIZE
        )

    @patch('image_generation.client')
    def test_generate_image_failure(self, mock_client):
        """Test image generation failure."""
        # Mock the OpenAI client to raise an exception
        mock_client.images.generate.side_effect = Exception("API Error")
        
        result = generate_image("test prompt")
        
        self.assertIsNone(result)

    @patch('image_generation.requests.get')
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

    @patch('image_generation.requests.get')
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
        prompt = create_child_friendly_prompt(word)
        filename = create_filename(word)
        
        # Verify the workflow produces expected results
        self.assertIn("elephant", prompt)
        self.assertEqual(filename, FILENAME_TEMPLATE.format(word="elephant"))
        self.assertIn("VERY SIMPLE", prompt)
        self.assertIn("10-year-old", prompt)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with very long word
        long_word = "a" * 100
        prompt = create_child_friendly_prompt(long_word)
        self.assertIn(long_word, prompt)
        
        # Test with numbers
        number_word = "123"
        prompt = create_child_friendly_prompt(number_word)
        self.assertIn(number_word, prompt)
        
        # Test with unicode characters
        unicode_word = "café"
        prompt = create_child_friendly_prompt(unicode_word)
        self.assertIn(unicode_word, prompt)

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
        self.assertEqual(DEFAULT_MODEL, "dall-e-3")
        self.assertEqual(DEFAULT_SIZE, "1024x1024")
        self.assertIn("VERY SIMPLE", PROMPT_TEMPLATE)
        self.assertIn("10-year-old", PROMPT_TEMPLATE)
        self.assertIn("_for_child.png", FILENAME_TEMPLATE)

if __name__ == '__main__':
    unittest.main() 
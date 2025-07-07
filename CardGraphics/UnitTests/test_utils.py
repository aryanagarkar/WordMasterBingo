import unittest
from unittest.mock import patch, mock_open
from CardGraphics.src.utils import Utils
from CardGraphics.src.word import Word
from CardGraphics.src.difficulty_level import DifficultyLevel

class TestUtils(unittest.TestCase):
    def setUp(self):
        Utils.clear()

    def tearDown(self):
        Utils.clear()

    @patch('CardGraphics.src.utils.open', new_callable=mock_open, read_data='cat: a small animal | kitty | feline | mouser\ndog: a pet | puppy | canine | hound\n')
    @patch('CardGraphics.src.utils.random.shuffle', lambda x: None)  # Disable shuffling for deterministic tests
    def test_initialize_and_get_words(self, mock_file):
        Utils.initialize('fake_path.txt')
        words = Utils.get_words()
        self.assertEqual(len(words), 2)
        self.assertIsInstance(words[0], Word)
        self.assertEqual(words[0].word, 'cat')
        self.assertEqual(words[1].word, 'dog')

    @patch('CardGraphics.src.utils.open', new_callable=mock_open, read_data='cat: a small animal | kitty | feline | mouser\n')
    @patch('CardGraphics.src.utils.random.shuffle', lambda x: None)
    def test_double_initialize_raises(self, mock_file):
        Utils.initialize('fake_path.txt')
        with self.assertRaises(RuntimeError):
            Utils.initialize('fake_path.txt')

    @patch('CardGraphics.src.utils.open', new_callable=mock_open, read_data='cat: a small animal | kitty | feline | mouser\ndog: a pet | puppy | canine | hound\n')
    @patch('CardGraphics.src.utils.random.shuffle', lambda x: None)
    def test_get_words_by_difficulty(self, mock_file):
        Utils.initialize('fake_path.txt')
        easy_words = Utils.get_words_by_difficulty(DifficultyLevel.EASY)
        medium_words = Utils.get_words_by_difficulty(DifficultyLevel.MEDIUM)
        hard_words = Utils.get_words_by_difficulty(DifficultyLevel.HARD)
        self.assertEqual(easy_words, ['kitty', 'puppy'])
        self.assertEqual(medium_words, ['feline', 'canine'])
        self.assertEqual(hard_words, ['mouser', 'hound'])

    @patch('CardGraphics.src.utils.open', new_callable=mock_open, read_data='badformatlinewithoutdelimiter\n')
    def test_parse_file_bad_format(self, mock_file):
        with self.assertRaises(ValueError):
            Utils.parse_file('fake_path.txt')

    def test_clear_resets_state(self):
        Utils.words = [Word('cat', 'a small animal', 'kitty', 'feline', 'mouser')]
        Utils._initialized = True
        Utils.clear()
        self.assertEqual(Utils.words, [])
        self.assertFalse(Utils._initialized)

if __name__ == '__main__':
    unittest.main() 
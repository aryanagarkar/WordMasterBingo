import unittest
from CardGraphics.src.word import Word
from CardGraphics.src.word_card import WordCardData, WordCard
from PySide6.QtWidgets import QApplication
import sys

class TestWordCardData(unittest.TestCase):
    def setUp(self):
        self.word = Word('cat', 'a small animal', 'kitty', 'feline', 'mouser')
        self.card_data = WordCardData(self.word)

    def test_card_data_fields(self):
        self.assertEqual(self.card_data.word.word, 'cat')
        self.assertEqual(self.card_data.definition, 'a small animal')
        self.assertEqual(self.card_data.easy_synonym, 'kitty')
        self.assertEqual(self.card_data.medium_synonym, 'cat')
        self.assertEqual(self.card_data.hard_synonym, 'mouser')

    def test_as_dict(self):
        expected = {
            'word': 'cat',
            'definition': 'a small animal',
            'easy_synonym': 'kitty',
            'medium_synonym': 'cat',
            'hard_synonym': 'mouser'
        }
        self.assertEqual(self.card_data.as_dict(), expected)

class TestWordCardGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Only create QApplication once for all GUI tests
        cls._app = QApplication.instance() or QApplication(sys.argv)

    def test_word_card_instantiation(self):
        word = Word('dog', 'a pet', 'puppy', 'canine', 'hound')
        card_data = WordCardData(word)
        card = WordCard(card_data)
        self.assertEqual(card.card_data.word.word, 'dog')
        self.assertEqual(card.card_data.definition, 'a pet')
        # We do not show or render the GUI in this test

    def test_word_card_setup_attributes(self):
        word = Word('dog', 'a pet', 'puppy', 'canine', 'hound')
        card_data = WordCardData(word)
        card = WordCard(card_data)
        self.assertEqual(card.grid_width, 240)
        self.assertEqual(card.grid_height, 336)
        self.assertIsNotNone(card.definition_font)
        self.assertIsNotNone(card.word_font)

if __name__ == '__main__':
    unittest.main() 
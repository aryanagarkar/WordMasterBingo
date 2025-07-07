import unittest
from CardGraphics.src.word import Word
from CardGraphics.src.bingo_card import BingoCardData, BingoCard
from CardGraphics.src.difficulty_level import DifficultyLevel
from PySide6.QtWidgets import QApplication
import sys

class TestBingoCardData(unittest.TestCase):
    def setUp(self):
        # 10 words used for testing purposes.
        # Actual application using 16 to render the bingo card.
        self.words = [
            Word(f'word{i}', f'def{i}', f'easy{i}', f'med{i}', f'hard{i}')
            for i in range(10)
        ]

    def test_normalize_words_list_padding(self):
        data = BingoCardData(self.words, DifficultyLevel.EASY)
        self.assertEqual(len(data.words), 16)
        for i in range(10, 16):
            self.assertEqual(data.words[i].word, '-')

    def test_normalize_words_list_truncation(self):
        words = [Word(f'word{i}', f'def{i}', f'easy{i}', f'med{i}', f'hard{i}') for i in range(20)]
        data = BingoCardData(words, DifficultyLevel.EASY)
        self.assertEqual(len(data.words), 16)
        self.assertEqual(data.words[-1].word, 'word15')

    def test_get_words_for_grid_easy(self):
        data = BingoCardData(self.words, DifficultyLevel.EASY)
        grid_words = data.get_words_for_grid()
        self.assertEqual(grid_words[:10], [f'easy{i}' for i in range(10)])
        self.assertEqual(len(grid_words), 16)

    def test_get_words_for_grid_medium(self):
        data = BingoCardData(self.words, DifficultyLevel.MEDIUM)
        grid_words = data.get_words_for_grid()
        self.assertEqual(grid_words[:10], [f'med{i}' for i in range(10)])
        self.assertEqual(len(grid_words), 16)

    def test_get_words_for_grid_hard(self):
        data = BingoCardData(self.words, DifficultyLevel.HARD)
        grid_words = data.get_words_for_grid()
        self.assertEqual(grid_words[:10], [f'hard{i}' for i in range(10)])
        self.assertEqual(len(grid_words), 16)

    def test_as_dict(self):
        data = BingoCardData(self.words, DifficultyLevel.HARD)
        d = data.as_dict()
        self.assertEqual(d['words'][:10], [f'word{i}' for i in range(10)])
        self.assertEqual(d['difficulty'], 'HARD')

class TestBingoCardGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication(sys.argv)

    def test_bingo_card_instantiation(self):
        words = [Word(f'word{i}', f'def{i}', f'easy{i}', f'med{i}', f'hard{i}') for i in range(16)]
        data = BingoCardData(words, DifficultyLevel.MEDIUM)
        card = BingoCard(data)
        self.assertEqual(card.card_data.difficulty, DifficultyLevel.MEDIUM)
        self.assertEqual(len(card.card_data.words), 16)
        # We do not show or render the GUI in this test

if __name__ == '__main__':
    unittest.main() 
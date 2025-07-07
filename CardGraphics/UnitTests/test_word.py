import unittest
from CardGraphics.src.word import Word

class TestWord(unittest.TestCase):
    def test_default_initialization(self):
        w = Word()
        self.assertEqual(w.word, '-')
        self.assertEqual(w.definition, '-')
        self.assertEqual(w.easy_word, '-')
        self.assertEqual(w.medium_word, '-')
        self.assertEqual(w.hard_word, '-')

    def test_custom_initialization(self):
        w = Word('cat', 'a small animal', 'kitty', 'feline', 'mouser')
        self.assertEqual(w.word, 'cat')
        self.assertEqual(w.definition, 'a small animal')
        self.assertEqual(w.easy_word, 'kitty')
        self.assertEqual(w.medium_word, 'feline')
        self.assertEqual(w.hard_word, 'mouser')

    def test_equality(self):
        w1 = Word('cat', 'a small animal', 'kitty', 'feline', 'mouser')
        w2 = Word('cat', 'a small animal', 'kitty', 'feline', 'mouser')
        w3 = Word('dog', 'a pet', 'puppy', 'canine', 'hound')
        self.assertEqual(w1, w2)
        self.assertNotEqual(w1, w3)

    def test_repr(self):
        w = Word('cat', 'a small animal', 'kitty', 'feline', 'mouser')
        expected = ("Word(word='cat', definition='a small animal', "
                    "easy='kitty', medium='feline', hard='mouser')")
        self.assertEqual(repr(w), expected)

if __name__ == '__main__':
    unittest.main() 
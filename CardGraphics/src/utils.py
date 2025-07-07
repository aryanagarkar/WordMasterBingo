import random
from CardGraphics.src.word import Word
from CardGraphics.src.difficulty_level import DifficultyLevel
from typing import List

class Utils:
    """
    Static utility class for loading, managing, and providing access to words and their difficulty levels.
    Handles initialization, parsing, and retrieval of word data for the application.
    """
    
    words: List[Word] = []
    _initialized: bool = False

    @staticmethod
    def initialize(file_path: str) -> None:
        """
        Initialize the static `words` array by loading and shuffling words from the given file.
        This method should be called once at the start.

        Args:
            file_path (str): Path to the file containing word data.
        Raises:
            RuntimeError: If called more than once without clearing.
        """
        
        if Utils._initialized:
            raise RuntimeError("Utils has already been initialized. Cannot initialize again.")
        Utils.words = Utils.parse_file(file_path)
        random.shuffle(Utils.words)
        Utils._initialized = True

    @staticmethod
    def get_words() -> List[Word]:
        """
        Return the list of Word objects loaded by this class.

        Returns:
            List[Word]: List of Word objects currently loaded (may be empty if not initialized).
        """

        return Utils.words

    @staticmethod
    def get_words_by_difficulty(difficulty: DifficultyLevel) -> List[str]:
        """
        Returns a list of words for the specified difficulty level.

        Args:
            difficulty (DifficultyLevel): The difficulty level to filter words by.
        Returns:
            List[str]: List of words (str) matching the difficulty.
        """

        words: List[str] = []
        for word_obj in Utils.words:
            # Select the word based on the requested difficulty.
            if difficulty == DifficultyLevel.EASY:
                word = word_obj.easy_word
            elif difficulty == DifficultyLevel.MEDIUM:
                word = word_obj.medium_word
            elif difficulty == DifficultyLevel.HARD:
                word = word_obj.hard_word
            else:
                continue
            if word != '-':
                words.append(word)
        return words

    @staticmethod
    def parse_file(file_path: str) -> List[Word]:
        """
        Parse the word data file and return a list of Word objects.

        Args:
            file_path (str): Path to the file containing word data.
        Returns:
            List[Word]: List of Word objects.
        """

        words: List[Word] = []
        with open(file_path, 'r') as file:
            for line in file:
                # Split the line into the main word and the rest of the attributes.
                word_part, remaining_attributes = line.split(':', 1)
                main_word = word_part.strip()
                attributes = remaining_attributes.split('|')
                if len(attributes) != 4:
                    raise ValueError(f"Line format incorrect: {line}")
                definition = attributes[0].strip()
                easy = attributes[1].strip()
                medium = attributes[2].strip()
                hard = attributes[3].strip()
                word_obj = Word(main_word, definition, easy, medium, hard)
                words.append(word_obj)
        return words

    @staticmethod
    def clear() -> None:
        """
        Clear the words list and reset the initialization flag.
        Allows re-initialization of the Utils class by setting words to an empty list and _initialized to False.
        """
        
        Utils.words = []
        Utils._initialized = False
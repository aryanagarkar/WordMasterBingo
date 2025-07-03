import random
from word import Word
from difficulty_level import DifficultyLevel

class Utils:
    """
    Utility class for loading, managing, and providing access to words and their difficulty levels.
    Handles initialization, parsing, and retrieval of word data for the application.
    """
    
    words = []
    _initialized = False

    @staticmethod
    def initialize(file_path):
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
        
        if(Utils._initialized == False):
            # Parse the file and load words.
            Utils.words = Utils.parse_file(file_path)
            
            # Shuffle the words to introduce randomness.
            random.shuffle(Utils.words)
            
            # Mark as initialized.
            Utils._initialized = True

    @staticmethod
    def get_words():
        """
        Return the list of Word objects loaded by this class.
        Returns:
            list: List of Word objects currently loaded (may be empty if not initialized).
        """
        
        return Utils.words

    @staticmethod
    def get_words_by_difficulty(difficulty: DifficultyLevel):
        """Returns a list of words for the specified difficulty level.
        Args:
            difficulty (DifficultyLevel): The difficulty level to filter words by.
        Returns:
            list: List of words (str) matching the difficulty.
        """
        
        words = []
        for word_obj in Utils.words:
            # Select the word based on the requested difficulty.
            if difficulty == DifficultyLevel.EASY:
                word = word_obj.get_easy_word()
            elif difficulty == DifficultyLevel.MEDIUM:
                word = word_obj.get_medium_word()
            elif difficulty == DifficultyLevel.HARD:
                word = word_obj.get_hard_word()

            # Only add if the word is not a placeholder.
            # Primarily used for testing when the bingo card had more grid cells than the number of words in the list.
            # In reality, this will not be used since the word list will alwayss contain at least the same number as the grid cells.
            if word != '-':
                words.append(word)
        return words

    @staticmethod
    def parse_file(file_path):
        """
        Parse the word data file and return a list of Word objects.
        Args:
            file_path (str): Path to the file containing word data.
        Returns:
            list: List of Word objects.
        """
        
        words = []

        with open(file_path, 'r') as file:
            for line in file:
                # Split the line into the main word and the rest of the attributes.
                word_part, remaining_attributes = line.split(':', 1)
                main_word = word_part.strip()

                # Split the remaining attributes into definition and synonyms.
                attributes = remaining_attributes.split(',')
                definition = attributes[0].strip()
                easy = attributes[1].strip()
                medium = attributes[2].strip()
                hard = attributes[3].strip()

                # Create a Word object and add to the list.
                word_obj = Word(main_word, definition, easy, medium, hard)
                words.append(word_obj)

        return words

    @staticmethod
    def clear():
        """
        Clear the words list and reset the initialization flag.
        Allows re-initialization of the Utils class by setting words to an empty list and _initialized to False.
        """
        
        Utils.words = []
        Utils._initialized = False